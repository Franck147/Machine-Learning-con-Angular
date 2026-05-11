"""
model_logic.py — Motor de IA para diagnóstico de hardware.

Usa TF-IDF + Naive Bayes para clasificar síntomas en 4 categorías:
Energia, Video, BIOS, Almacenamiento.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import numpy as np


# Dataset de entrenamiento: (síntoma, categoría)
TRAINING_DATA = [
    # --- Energía ---
    ("el computador no enciende", "Energia"),
    ("no hay energía en la pc", "Energia"),
    ("la fuente de poder no funciona", "Energia"),
    ("el equipo se apaga solo", "Energia"),
    ("se apaga repentinamente sin aviso", "Energia"),
    ("el botón de encendido no responde", "Energia"),
    ("la PC hace clic pero no enciende", "Energia"),
    ("la fuente de alimentación está muerta", "Energia"),
    ("el ventilador de la fuente no gira", "Energia"),
    ("el equipo enciende y se apaga inmediatamente", "Energia"),
    ("la psu no da voltaje", "Energia"),
    ("el sistema no tiene corriente eléctrica", "Energia"),
    ("el cable de poder está bien pero no enciende", "Energia"),
    ("pc se reinicia constantemente", "Energia"),
    ("apagado repentino por sobrecalentamiento", "Energia"),

    # --- Video ---
    ("no hay imagen en el monitor", "Video"),
    ("pantalla negra al encender", "Video"),
    ("la tarjeta de video falla", "Video"),
    ("el monitor no recibe señal", "Video"),
    ("artefactos visuales en pantalla", "Video"),
    ("la pantalla parpadea", "Video"),
    ("colores distorsionados en la pantalla", "Video"),
    ("resolución incorrecta", "Video"),
    ("la GPU no es detectada", "Video"),
    ("pantalla azul con artefactos gráficos", "Video"),
    ("líneas verticales en el monitor", "Video"),
    ("driver de video corrupto", "Video"),
    ("no hay salida HDMI", "Video"),
    ("DisplayPort sin señal", "Video"),
    ("la tarjeta gráfica hace ruido y no da imagen", "Video"),

    # --- BIOS ---
    ("la computadora no pasa el POST", "BIOS"),
    ("pitidos al encender", "BIOS"),
    ("beep codes al iniciar", "BIOS"),
    ("error de BIOS al arrancar", "BIOS"),
    ("la RAM no es detectada", "BIOS"),
    ("necesito resetear el BIOS", "BIOS"),
    ("configuración del BIOS perdida", "BIOS"),
    ("la pila del CMOS está descargada", "BIOS"),
    ("error de memoria al arrancar", "BIOS"),
    ("el sistema no detecta el procesador", "BIOS"),
    ("falla en la inicialización del hardware", "BIOS"),
    ("pantalla de bios no carga", "BIOS"),
    ("pitido largo al encender", "BIOS"),
    ("la motherboard no reconoce la RAM", "BIOS"),
    ("error al iniciar el sistema operativo desde BIOS", "BIOS"),

    # --- Almacenamiento ---
    ("el disco duro no es detectado", "Almacenamiento"),
    ("el SSD no aparece en el sistema", "Almacenamiento"),
    ("error de lectura del disco", "Almacenamiento"),
    ("el sistema no encuentra el arranque", "Almacenamiento"),
    ("el HDD hace ruido extraño", "Almacenamiento"),
    ("no bootea desde el disco", "Almacenamiento"),
    ("error SMART en el disco duro", "Almacenamiento"),
    ("archivos corruptos en el almacenamiento", "Almacenamiento"),
    ("el disco duro está lleno y el sistema es lento", "Almacenamiento"),
    ("no puedo acceder a mis archivos", "Almacenamiento"),
    ("el SSD NVMe no aparece en BIOS", "Almacenamiento"),
    ("sistema de archivos corrompido", "Almacenamiento"),
    ("el disco hace click click", "Almacenamiento"),
    ("error al leer el sector de arranque", "Almacenamiento"),
    ("velocidad de disco extremadamente baja", "Almacenamiento"),
]


class DiagnosticModel:
    """
    Clasificador de síntomas de hardware usando TF-IDF + Naive Bayes.
    Predice la categoría del problema y devuelve la confianza de la predicción.
    """

    CATEGORIES = ["Energia", "Video", "BIOS", "Almacenamiento"]

    def __init__(self):
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, 2),   # unigramas y bigramas para mejor contexto
                min_df=1,
                analyzer="word",
                strip_accents="unicode",
                lowercase=True,
            )),
            ("clf", MultinomialNB(alpha=0.5)),
        ])
        self._train()

    def _train(self):
        texts, labels = zip(*TRAINING_DATA)
        self.pipeline.fit(texts, labels)

    def predict(self, symptom_text: str) -> dict:
        """
        Clasifica el síntoma y devuelve categoría + confianza.

        Returns:
            {
                "category": str,
                "confidence": float,   # 0.0 – 1.0
                "all_probabilities": dict
            }
        """
        probs = self.pipeline.predict_proba([symptom_text])[0]
        classes = self.pipeline.classes_
        category_index = int(np.argmax(probs))

        return {
            "category": str(classes[category_index]),
            "confidence": round(float(probs[category_index]), 4),
            "all_probabilities": {
                str(cls): round(float(p), 4)
                for cls, p in zip(classes, probs)
            },
        }
