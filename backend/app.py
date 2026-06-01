"""
app.py — Servidor Flask para el Asistente de Diagnóstico de Hardware.

Rutas:
  POST /api/diagnosticar  — recibe síntoma y devuelve diagnóstico + solución
  POST /api/feedback      — registra si el diagnóstico fue útil (feedback loop)
  GET  /api/health        — verifica que el servidor esté activo
"""

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client, Client

from model_logic import DiagnosticModel, CONFIDENCE_THRESHOLD

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
logger.info("Modelo de diagnóstico cargado y entrenado (9 categorías, LinearSVC).")

# ---------------------------------------------------------------------------
# Preguntas de clarificación por nivel de confianza
# ---------------------------------------------------------------------------
CLARIFICATION_QUESTIONS = [
    "No pude identificar el problema con certeza. ¿Puedes ser más específico? "
    "Describe qué pasa exactamente: ¿hay sonidos, mensajes de error, luces, o el equipo no reacciona en absoluto?",
    "Necesito más detalles para diagnosticar correctamente. "
    "¿El problema ocurre al encender, durante el uso, o en un momento específico? "
    "¿Qué hardware tienes (GPU, RAM, tipo de disco)?",
    "Con esa descripción no puedo determinar la categoría con seguridad. "
    "¿Puedes mencionar qué componente crees que está afectado y cuándo comenzó el problema?",
]

# ---------------------------------------------------------------------------
# Soluciones de respaldo (sin Supabase)
# ---------------------------------------------------------------------------
FALLBACK_SOLUTIONS: dict[str, str] = {
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
    "Red": (
        "Verifica que el adaptador de red esté habilitado en el Administrador de dispositivos. "
        "Ejecuta 'ipconfig /release' y 'ipconfig /renew' en CMD. "
        "Reinstala los drivers de la tarjeta de red desde el sitio del fabricante."
    ),
    "Audio": (
        "Verifica en el Administrador de dispositivos que el dispositivo de audio esté activo. "
        "Reinstala los drivers de audio (Realtek o el fabricante correspondiente). "
        "Comprueba que el conector de audio esté en el jack correcto (verde = salida)."
    ),
    "Temperatura": (
        "Limpia los ventiladores y disipadores con aire comprimido. "
        "Reaplica pasta térmica en el procesador. "
        "Verifica que todos los ventiladores del chasis estén funcionando y el flujo de aire sea correcto."
    ),
    "USB": (
        "Prueba el dispositivo en otro puerto USB. "
        "En el Administrador de dispositivos, desinstala los controladores USB y reinicia para que se reinstalen. "
        "Verifica que los conectores internos del panel frontal estén bien conectados a la placa."
    ),
    "Drivers": (
        "Abre el Administrador de dispositivos y busca dispositivos con exclamación amarilla. "
        "Descarga los drivers directamente desde el sitio del fabricante del hardware. "
        "Considera usar DDU (Display Driver Uninstaller) para limpiar drivers de GPU antes de reinstalar."
    ),
}


def get_solution_from_supabase(
    category: str,
    brand: str | None = None,
    series: str | None = None,
) -> str | None:
    """
    Busca la solución más específica disponible en este orden de prioridad:
      1. brand + series + category
      2. brand + category (sin series)
      3. category genérica (sin marca)
    """
    if not supabase:
        return None
    try:
        # Intento 1: brand + series + category
        if brand and series:
            r = (
                supabase.table("catalog_solutions")
                .select("solution_text")
                .eq("category", category)
                .eq("brand", brand)
                .eq("series", series)
                .limit(1)
                .execute()
            )
            if r.data:
                return r.data[0]["solution_text"]

        # Intento 2: brand + category
        if brand:
            r = (
                supabase.table("catalog_solutions")
                .select("solution_text")
                .eq("category", category)
                .eq("brand", brand)
                .is_("series", "null")
                .limit(1)
                .execute()
            )
            if r.data:
                return r.data[0]["solution_text"]

        # Intento 3: genérico (sin marca)
        r = (
            supabase.table("catalog_solutions")
            .select("solution_text")
            .eq("category", category)
            .is_("brand", "null")
            .limit(1)
            .execute()
        )
        if r.data:
            return r.data[0]["solution_text"]

    except Exception as exc:
        logger.error("Error consultando Supabase: %s", exc)
    return None


def log_diagnosis(
    query: str,
    category: str,
    confidence: float,
    solution: str,
    brand: str | None = None,
    series: str | None = None,
) -> str | None:
    """Guarda el diagnóstico y devuelve el log_id generado."""
    if not supabase:
        return None
    try:
        result = supabase.table("diagnosis_logs").insert({
            "user_query":          query,
            "predicted_category":  category,
            "accuracy":            confidence,
            "solution_provided":   solution,
            "brand":               brand or None,
            "series":              series or None,
        }).execute()
        if result.data:
            return result.data[0]["id"]
    except Exception as exc:
        logger.error("Error guardando log en Supabase: %s", exc)
    return None


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model": "DiagnosticModel v2.0",
        "algoritmo": "TF-IDF + LinearSVC",
        "categorias": DiagnosticModel.CATEGORIES,
        "umbral_confianza": CONFIDENCE_THRESHOLD,
    }), 200


@app.route("/api/diagnosticar", methods=["POST"])
def diagnosticar():
    """
    Body esperado (JSON):
        {
            "mensaje": "El computador no enciende y hace pitidos",
            "contexto": ["no enciende"]   // opcional — mensajes previos
        }

    Respuesta normal:
        { "categoria", "confianza", "solucion", "probabilidades", "log_id" }

    Respuesta con baja confianza:
        { "necesita_mas_info": true, "pregunta", "probabilidades", "confianza_maxima" }
    """
    data = request.get_json(silent=True)

    if not data or not data.get("mensaje"):
        return jsonify({"error": "El campo 'mensaje' es requerido."}), 400

    mensaje = data["mensaje"].strip()
    if len(mensaje) < 3:
        return jsonify({"error": "El mensaje es demasiado corto para diagnosticar."}), 400

    # Marca y serie opcionales (aportan contexto al diagnóstico)
    marca: str  = (data.get("marca")  or "").strip()
    serie: str  = (data.get("serie")  or "").strip()

    # Combinar con contexto previo si existe (multi-turno)
    contexto: list[str] = data.get("contexto", [])
    texto_completo = " ".join(contexto + [mensaje]) if contexto else mensaje

    # Enriquecer con prefijo de marca para mejor clasificación
    if marca:
        prefix = f"[{marca.upper()}"
        if serie:
            prefix += f" {serie.upper()}"
        prefix += "]"
        texto_completo = f"{prefix} {texto_completo}"

    # Clasificar con el modelo
    prediction = model.predict(texto_completo)
    category = prediction["category"]
    confidence = prediction["confidence"]

    # Respuesta de baja confianza: pedir más información
    if prediction["low_confidence"]:
        pregunta = CLARIFICATION_QUESTIONS[len(contexto) % len(CLARIFICATION_QUESTIONS)]
        logger.info(
            "Baja confianza (%.0f%%) para: '%s'", confidence * 100, mensaje[:60]
        )
        return jsonify({
            "necesita_mas_info": True,
            "pregunta": pregunta,
            "probabilidades": prediction["all_probabilities"],
            "confianza_maxima": confidence,
        }), 200

    # Obtener solución: busca primero la específica por marca/serie
    solution = (
        get_solution_from_supabase(category, marca or None, serie or None)
        or FALLBACK_SOLUTIONS.get(category, "No se encontró solución para esta categoría.")
    )

    # Registrar diagnóstico y obtener log_id
    log_id = log_diagnosis(mensaje, category, confidence, solution, marca or None, serie or None)

    logger.info(
        "Diagnóstico: '%s' [%s %s] → %s (%.0f%%)",
        mensaje[:50], marca, serie, category, confidence * 100
    )

    return jsonify({
        "categoria": category,
        "confianza": confidence,
        "solucion": solution,
        "probabilidades": prediction["all_probabilities"],
        "log_id": log_id,
        "marca": marca or None,
        "serie": serie or None,
    }), 200


@app.route("/api/feedback", methods=["POST"])
def feedback():
    """
    Body esperado:
        { "log_id": "uuid", "util": true/false }

    Actualiza el registro de diagnosis_logs con el feedback del usuario.
    Los logs con feedback positivo pueden usarse para re-entrenar el modelo.
    """
    data = request.get_json(silent=True)

    if not data or "log_id" not in data or "util" not in data:
        return jsonify({"error": "Campos requeridos: log_id, util"}), 400

    log_id = str(data["log_id"])
    util = bool(data["util"])

    if supabase:
        try:
            supabase.table("diagnosis_logs").update({
                "feedback_util": util,
            }).eq("id", log_id).execute()
            logger.info("Feedback '%s' registrado para log %s", util, log_id)
        except Exception as exc:
            logger.error("Error guardando feedback: %s", exc)

    return jsonify({"ok": True}), 200


# ---------------------------------------------------------------------------
# Inicio del servidor
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
