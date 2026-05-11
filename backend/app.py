"""
app.py — Servidor Flask para el Asistente de Diagnóstico de Hardware.

Rutas:
  POST /api/diagnosticar  — recibe síntoma y devuelve diagnóstico + solución
  GET  /api/health        — verifica que el servidor esté activo
"""

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client, Client

from model_logic import DiagnosticModel

# ---------------------------------------------------------------------------
# Configuración inicial
# ---------------------------------------------------------------------------
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s — %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Permitir peticiones del frontend Angular (localhost:4200 en desarrollo)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:4200",
            "http://127.0.0.1:4200",
        ]
    }
})

# ---------------------------------------------------------------------------
# Supabase
# ---------------------------------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

supabase: Client | None = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Conexión a Supabase establecida.")
else:
    logger.warning("Variables SUPABASE_URL / SUPABASE_KEY no configuradas. "
                   "Se usarán soluciones de respaldo.")

# ---------------------------------------------------------------------------
# Modelo de ML (se instancia una sola vez al iniciar el servidor)
# ---------------------------------------------------------------------------
model = DiagnosticModel()
logger.info("Modelo de diagnóstico cargado y entrenado.")

# ---------------------------------------------------------------------------
# Soluciones de respaldo (cuando Supabase no está disponible)
# ---------------------------------------------------------------------------
FALLBACK_SOLUTIONS = {
    "Energia": (
        "Verifica el cable de alimentación y la fuente de poder (PSU). "
        "Mide voltajes con multímetro (+12V, +5V, +3.3V). "
        "Si el equipo enciende y se apaga de inmediato, revisa ventiladores y aplica pasta térmica nueva."
    ),
    "Video": (
        "Conecta el monitor a la GPU dedicada (no a la tarjeta integrada). "
        "Reinserta la GPU en el slot PCIe y limpia contactos con alcohol isopropílico. "
        "Verifica conectores de alimentación PCIe de la GPU."
    ),
    "BIOS": (
        "Verifica que la RAM esté en los slots correctos (A2/B2 para dual channel). "
        "Prueba con un módulo a la vez. Para resetear BIOS: retira la pila CR2032 "
        "por 5 minutos o usa el jumper CMOS."
    ),
    "Almacenamiento": (
        "Verifica cables SATA y alimentación del disco. Comprueba en BIOS que el "
        "puerto SATA esté en modo AHCI. Usa CrystalDiskInfo para revisar S.M.A.R.T. "
        "Ejecuta chkdsk /f /r si hay errores del sistema de archivos."
    ),
}


def get_solution_from_supabase(category: str) -> str | None:
    """Consulta la solución para la categoría en catalog_solutions."""
    if not supabase:
        return None
    try:
        result = (
            supabase.table("catalog_solutions")
            .select("solution_text")
            .eq("category", category)
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]["solution_text"]
    except Exception as exc:
        logger.error("Error consultando Supabase: %s", exc)
    return None


def log_diagnosis(query: str, category: str, confidence: float, solution: str) -> None:
    """Guarda el diagnóstico en diagnosis_logs (sin bloquear la respuesta)."""
    if not supabase:
        return
    try:
        supabase.table("diagnosis_logs").insert({
            "user_query": query,
            "predicted_category": category,
            "accuracy": confidence,
            "solution_provided": solution,
        }).execute()
    except Exception as exc:
        logger.error("Error guardando log en Supabase: %s", exc)


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": "DiagnosticModel v1.0"}), 200


@app.route("/api/diagnosticar", methods=["POST"])
def diagnosticar():
    """
    Body esperado (JSON):
        { "mensaje": "El computador no enciende y hace pitidos" }

    Respuesta:
        {
            "categoria": "BIOS",
            "confianza": 0.87,
            "solucion": "...",
            "probabilidades": { "Energia": 0.05, "Video": 0.03, ... }
        }
    """
    data = request.get_json(silent=True)

    if not data or not data.get("mensaje"):
        return jsonify({"error": "El campo 'mensaje' es requerido."}), 400

    mensaje = data["mensaje"].strip()
    if len(mensaje) < 3:
        return jsonify({"error": "El mensaje es demasiado corto para diagnosticar."}), 400

    # 1. Clasificar con el modelo de ML
    prediction = model.predict(mensaje)
    category = prediction["category"]
    confidence = prediction["confidence"]

    # 2. Obtener solución (Supabase con fallback local)
    solution = get_solution_from_supabase(category) or FALLBACK_SOLUTIONS.get(
        category, "No se encontró solución para esta categoría."
    )

    # 3. Registrar diagnóstico en Supabase (ignora errores)
    log_diagnosis(mensaje, category, confidence, solution)

    logger.info("Diagnóstico: '%s' → %s (%.0f%%)", mensaje[:60], category, confidence * 100)

    return jsonify({
        "categoria": category,
        "confianza": confidence,
        "solucion": solution,
        "probabilidades": prediction["all_probabilities"],
    }), 200


# ---------------------------------------------------------------------------
# Inicio del servidor
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
