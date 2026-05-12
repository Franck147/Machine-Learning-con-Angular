"""
app.py — Servidor Flask para el Asistente de Diagnóstico de Hardware.

Rutas:
  POST /api/diagnosticar  — recibe síntoma (+ marca/modelo opcional) y devuelve diagnóstico
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
# Modelo de ML
# ---------------------------------------------------------------------------
model = DiagnosticModel()
logger.info("Modelo de diagnóstico cargado con %d categorías.", len(model.CATEGORIES))

# ---------------------------------------------------------------------------
# Soluciones de respaldo (cuando Supabase no está disponible)
# ---------------------------------------------------------------------------
FALLBACK_SOLUTIONS = {
    "Energia": (
        "Verifica el cable de alimentación y la fuente de poder (PSU). "
        "Mide voltajes con multímetro (+12V, +5V, +3.3V). "
        "Comprueba el conector ATX 24-pin y el EPS 8-pin del CPU. "
        "Si el equipo enciende y se apaga de inmediato, revisa ventiladores y aplica pasta térmica nueva. "
        "Marcas comunes a revisar: Corsair RM/HX, EVGA SuperNOVA, Seasonic Focus, be quiet! Straight Power."
    ),
    "Video": (
        "Conecta el monitor al puerto de la GPU dedicada (no a la tarjeta integrada). "
        "Reinserta la GPU en el slot PCIe x16 y limpia contactos con alcohol isopropílico. "
        "Verifica conectores de alimentación PCIe (6+2 pin o 16-pin 12VHPWR para RTX 40). "
        "Prueba con otro cable HDMI/DisplayPort o en otro monitor. "
        "Si hay artefactos, actualiza o reinstala drivers NVIDIA/AMD desde sitio oficial."
    ),
    "BIOS": (
        "Verifica que la RAM esté en los slots correctos (A2/B2 para dual channel según manual). "
        "Prueba con un módulo a la vez para identificar el defectuoso. "
        "Para resetear BIOS: retira la pila CR2032 por 5 minutos o usa el jumper/botón CMOS. "
        "Si el CPU es nuevo (Ryzen 5000/7000 o Intel 12a/13a gen), puede requerir actualización de BIOS. "
        "Revisa el manual de tu motherboard (ASUS, MSI, Gigabyte, ASRock) para el procedimiento correcto."
    ),
    "Almacenamiento": (
        "Verifica cables SATA y alimentación del disco. Comprueba en BIOS que el puerto SATA esté en modo AHCI. "
        "Usa CrystalDiskInfo para revisar estado S.M.A.R.T. — reallocated sectors altos indican falla inminente. "
        "Para NVMe (Samsung 980 Pro, WD Black SN850, Seagate FireCuda): verifica que el slot M.2 sea PCIe Gen4. "
        "Ejecuta chkdsk /f /r en Windows o fsck en Linux para reparar el sistema de archivos."
    ),
    "Temperatura": (
        "Monitorea temperaturas con HWiNFO64 o Core Temp. CPU no debe superar 90°C bajo carga sostenida. "
        "Limpia disipador y ventiladores de polvo. Reaplica pasta térmica (Noctua NT-H1, Thermal Grizzly Kryonaut). "
        "Verifica que el cooler esté correctamente montado con presión uniforme (Noctua, be quiet!, Cooler Master). "
        "En AIO (Corsair H150i, NZXT Kraken, DeepCool LS720): verifica que la bomba funcione y el radiador no esté obstruido. "
        "Mejora el flujo de aire del gabinete: ventiladores frontales de entrada, traseros/superiores de salida."
    ),
    "Red": (
        "Verifica el driver de red: Intel i219/i225, Realtek RTL8125. Descárgalo del sitio del fabricante de la motherboard. "
        "Prueba con otro cable Ethernet o en otro puerto del router/switch. "
        "En Windows: ejecuta 'netsh winsock reset' y 'netsh int ip reset' como administrador y reinicia. "
        "Para WiFi (Intel AX200/AX210, ASUS PCE-AX58BT): verifica antenas conectadas y canal WiFi no saturado. "
        "Revisa el Administrador de dispositivos para verificar que el adaptador no tenga código de error."
    ),
}


def build_symptom_text(mensaje: str, marca: str = "", modelo: str = "") -> str:
    """Combina síntoma + marca/modelo para mejorar la precisión del modelo."""
    parts = []
    if marca:
        parts.append(marca.strip())
    if modelo:
        parts.append(modelo.strip())
    parts.append(mensaje.strip())
    return " ".join(parts)


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


def log_diagnosis(query: str, marca: str, modelo: str,
                  category: str, confidence: float, solution: str) -> None:
    """Guarda el diagnóstico en diagnosis_logs."""
    if not supabase:
        return
    try:
        supabase.table("diagnosis_logs").insert({
            "user_query": query,
            "hardware_brand": marca or None,
            "hardware_model": modelo or None,
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
    return jsonify({
        "status": "ok",
        "model": "DiagnosticModel v2.0",
        "categories": model.CATEGORIES,
    }), 200


@app.route("/api/diagnosticar", methods=["POST"])
def diagnosticar():
    """
    Body esperado (JSON):
        {
            "mensaje": "El computador no enciende y hace pitidos",
            "marca":   "ASUS",     (opcional)
            "modelo":  "ROG Z790"  (opcional)
        }

    Respuesta:
        {
            "categoria":    "BIOS",
            "confianza":    0.87,
            "solucion":     "...",
            "probabilidades": { "Energia": 0.05, ... }
        }
    """
    data = request.get_json(silent=True)

    if not data or not data.get("mensaje"):
        return jsonify({"error": "El campo 'mensaje' es requerido."}), 400

    mensaje = data["mensaje"].strip()
    if len(mensaje) < 3:
        return jsonify({"error": "El mensaje es demasiado corto para diagnosticar."}), 400

    marca  = data.get("marca", "").strip()
    modelo = data.get("modelo", "").strip()

    # Construir texto enriquecido con marca/modelo para el modelo ML
    symptom_text = build_symptom_text(mensaje, marca, modelo)

    # 1. Clasificar con el modelo de ML
    prediction = model.predict(symptom_text)
    category   = prediction["category"]
    confidence = prediction["confidence"]

    # 2. Obtener solución (Supabase con fallback local)
    solution = get_solution_from_supabase(category) or FALLBACK_SOLUTIONS.get(
        category, "No se encontró solución para esta categoría."
    )

    # 3. Registrar diagnóstico en Supabase
    log_diagnosis(mensaje, marca, modelo, category, confidence, solution)

    logger.info(
        "Diagnóstico: '%s' [%s %s] → %s (%.0f%%)",
        mensaje[:60], marca or "—", modelo or "—", category, confidence * 100,
    )

    return jsonify({
        "categoria":      category,
        "confianza":      confidence,
        "solucion":       solution,
        "probabilidades": prediction["all_probabilities"],
    }), 200


# ---------------------------------------------------------------------------
# Inicio del servidor
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
