"""
model_logic.py — Motor de IA para diagnóstico de hardware.

Usa TF-IDF + LinearSVC (calibrado) para clasificar síntomas en 9 categorías.
Incluye umbral de confianza y soporte para re-entrenamiento con feedback.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
import numpy as np

CONFIDENCE_THRESHOLD = 0.45

TRAINING_DATA: list[tuple[str, str]] = [
    # ------------------------------------------------------------------ Energia
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
    ("la PC no da señales de vida", "Energia"),
    ("el LED de encendido no se ilumina", "Energia"),
    ("la pantalla y ventiladores no reaccionan al encender", "Energia"),
    ("el interruptor de la fuente está dañado", "Energia"),
    ("pico de voltaje quemó la fuente", "Energia"),
    ("el UPS no alimenta el equipo correctamente", "Energia"),
    ("voltaje insuficiente de la PSU", "Energia"),
    ("conector ATX de la fuente no hace contacto", "Energia"),
    ("la pc parpadea y se apaga sola", "Energia"),
    ("los ventiladores giran medio segundo y se detienen", "Energia"),
    ("la fuente hace ruido y no da energía", "Energia"),
    ("el jumper del panel frontal está desconectado", "Energia"),
    ("no hay corriente en ningún componente", "Energia"),
    ("la regleta está funcionando pero la pc no enciende", "Energia"),
    ("la PSU pita y se apaga inmediatamente", "Energia"),
    ("el sistema no responde al botón de power", "Energia"),

    # ------------------------------------------------------------------- Video
    ("no hay imagen en el monitor", "Video"),
    ("pantalla negra al encender", "Video"),
    ("la tarjeta de video falla", "Video"),
    ("el monitor no recibe señal", "Video"),
    ("artefactos visuales en pantalla", "Video"),
    ("la pantalla parpadea constantemente", "Video"),
    ("colores distorsionados en la pantalla", "Video"),
    ("resolución incorrecta no puedo cambiarla", "Video"),
    ("la GPU no es detectada por el sistema", "Video"),
    ("pantalla azul con artefactos gráficos", "Video"),
    ("líneas verticales en el monitor", "Video"),
    ("no hay salida HDMI en la tarjeta gráfica", "Video"),
    ("DisplayPort sin señal de video", "Video"),
    ("la tarjeta gráfica hace ruido y no da imagen", "Video"),
    ("pantalla con rayas horizontales", "Video"),
    ("colores invertidos en la pantalla", "Video"),
    ("el monitor parpadea y se apaga solo", "Video"),
    ("la pantalla se congela con artefactos gráficos", "Video"),
    ("no detecta el segundo monitor", "Video"),
    ("resolución fija en 800x600 sin poder cambiar", "Video"),
    ("imagen borrosa en el monitor", "Video"),
    ("el monitor dice no signal", "Video"),
    ("glitches visuales en juegos", "Video"),
    ("la pantalla se pone verde o morada", "Video"),
    ("pixeles muertos en la pantalla", "Video"),
    ("la GPU emite pitidos y no muestra imagen", "Video"),
    ("salida de video VGA no funciona", "Video"),
    ("pantalla dividida en colores aleatorios", "Video"),
    ("el monitor se ve con sombras fantasma", "Video"),
    ("la imagen tiembla en el monitor", "Video"),

    # -------------------------------------------------------------------- BIOS
    ("la computadora no pasa el POST", "BIOS"),
    ("pitidos al encender la computadora", "BIOS"),
    ("beep codes al iniciar el sistema", "BIOS"),
    ("error de BIOS al arrancar", "BIOS"),
    ("la RAM no es detectada por la placa", "BIOS"),
    ("necesito resetear el BIOS a valores de fábrica", "BIOS"),
    ("configuración del BIOS se pierde al apagar", "BIOS"),
    ("la pila del CMOS está descargada", "BIOS"),
    ("error de memoria al arrancar el sistema", "BIOS"),
    ("el sistema no detecta el procesador", "BIOS"),
    ("falla en la inicialización del hardware POST", "BIOS"),
    ("pantalla de bios no carga correctamente", "BIOS"),
    ("pitido largo al encender la PC", "BIOS"),
    ("la motherboard no reconoce la RAM instalada", "BIOS"),
    ("el BIOS no guarda la hora del sistema", "BIOS"),
    ("la fecha y hora se resetean solas al reiniciar", "BIOS"),
    ("la placa madre hace 3 pitidos cortos", "BIOS"),
    ("error memory test failed al iniciar", "BIOS"),
    ("no puedo entrar a la configuración del BIOS", "BIOS"),
    ("el sistema muestra pantalla de BIOS en bucle", "BIOS"),
    ("memoria RAM incompatible con la placa base", "BIOS"),
    ("la motherboard tiene LED de debug rojo encendido", "BIOS"),
    ("error Q-Code en la placa madre", "BIOS"),
    ("el sistema ignora el boot order configurado en BIOS", "BIOS"),
    ("POST se detiene y no continúa el arranque", "BIOS"),
    ("la placa madre no reconoce el nuevo procesador", "BIOS"),
    ("error al actualizar el firmware BIOS", "BIOS"),
    ("la BIOS no detecta el disco duro conectado", "BIOS"),
    ("el overclock no funciona ni se guarda en BIOS", "BIOS"),
    ("la placa base no arranca sin pitido de error", "BIOS"),

    # ------------------------------------------------------------- Almacenamiento
    ("el disco duro no es detectado por el sistema", "Almacenamiento"),
    ("el SSD no aparece en el sistema operativo", "Almacenamiento"),
    ("error de lectura del disco duro", "Almacenamiento"),
    ("el sistema no encuentra el arranque del disco", "Almacenamiento"),
    ("el HDD hace ruido extraño de clic", "Almacenamiento"),
    ("no bootea desde el disco duro", "Almacenamiento"),
    ("error SMART en el disco duro", "Almacenamiento"),
    ("archivos corruptos en el almacenamiento", "Almacenamiento"),
    ("el disco duro está lleno y el sistema es lento", "Almacenamiento"),
    ("no puedo acceder a mis archivos guardados", "Almacenamiento"),
    ("el SSD NVMe no aparece en BIOS ni en Windows", "Almacenamiento"),
    ("sistema de archivos corrompido", "Almacenamiento"),
    ("el disco hace click click repetido", "Almacenamiento"),
    ("error al leer el sector de arranque del disco", "Almacenamiento"),
    ("velocidad de disco extremadamente baja", "Almacenamiento"),
    ("el disco M.2 no es reconocido por la placa", "Almacenamiento"),
    ("error de escritura en el SSD", "Almacenamiento"),
    ("la partición del disco desapareció", "Almacenamiento"),
    ("Windows no encuentra el disco de instalación", "Almacenamiento"),
    ("el disco duro no monta en el sistema", "Almacenamiento"),
    ("pérdida de datos sin causa aparente", "Almacenamiento"),
    ("el explorador de archivos no abre la unidad", "Almacenamiento"),
    ("el disco tarda mucho en responder", "Almacenamiento"),
    ("error al formatear la unidad de disco", "Almacenamiento"),
    ("error de sectores defectuosos en el disco", "Almacenamiento"),
    ("el SSD se desconecta aleatoriamente", "Almacenamiento"),
    ("error input output device al acceder al disco", "Almacenamiento"),
    ("la unidad de disco óptico no lee CDs", "Almacenamiento"),
    ("el RAID no sincroniza los discos correctamente", "Almacenamiento"),
    ("el disco duro externo USB no aparece en sistema", "Almacenamiento"),

    # ----------------------------------------------------------------------- Red
    ("no tengo conexión a internet", "Red"),
    ("el WiFi no funciona en el equipo", "Red"),
    ("la tarjeta de red no es detectada", "Red"),
    ("conexión ethernet no responde", "Red"),
    ("la red inalámbrica se desconecta frecuentemente", "Red"),
    ("velocidad de internet muy lenta", "Red"),
    ("el adaptador WiFi no aparece en dispositivos", "Red"),
    ("no puedo conectarme a la red local", "Red"),
    ("el cable de red no da señal", "Red"),
    ("error de dirección IP en conflicto", "Red"),
    ("DNS no resuelve nombres de dominio", "Red"),
    ("la antena WiFi está rota o sin señal", "Red"),
    ("no detecta redes inalámbricas cercanas", "Red"),
    ("la tarjeta de red no tiene controladores instalados", "Red"),
    ("ping de red muy alto o time out constante", "Red"),
    ("conexión intermitente a internet", "Red"),
    ("la tarjeta ethernet muestra cable desconectado", "Red"),
    ("WiFi conectado pero sin acceso a internet", "Red"),
    ("la velocidad de descarga es mínima o nula", "Red"),
    ("el adaptador de red no enciende", "Red"),
    ("no puedo conectarme al servidor local de red", "Red"),
    ("el protocolo TCP IP está corrupto", "Red"),
    ("el módem no es reconocido por el sistema", "Red"),
    ("no hay señal en el puerto ethernet trasero", "Red"),
    ("error de autenticación al conectar a red WiFi", "Red"),
    ("la red aparece disponible pero no conecta", "Red"),
    ("el driver de la tarjeta de red no instala", "Red"),
    ("el router no asigna IP al equipo", "Red"),
    ("la tarjeta de red integrada dejó de funcionar", "Red"),
    ("error obteniendo dirección IP automáticamente", "Red"),

    # --------------------------------------------------------------------- Audio
    ("no hay sonido en los altavoces", "Audio"),
    ("el micrófono no funciona", "Audio"),
    ("audio distorsionado o con ruido", "Audio"),
    ("la tarjeta de sonido no es detectada", "Audio"),
    ("los auriculares no dan sonido", "Audio"),
    ("el audio se corta intermitentemente", "Audio"),
    ("el volumen no responde a los controles", "Audio"),
    ("zumbido constante en los altavoces", "Audio"),
    ("el jack de audio no funciona", "Audio"),
    ("el driver de audio está corrompido", "Audio"),
    ("los altavoces internos no producen sonido", "Audio"),
    ("el dispositivo de audio no aparece en sistema", "Audio"),
    ("audio solo en un canal derecho o izquierdo", "Audio"),
    ("el sonido tiene eco o reverberación", "Audio"),
    ("los auriculares de 3.5mm no son reconocidos", "Audio"),
    ("el HDMI no transmite audio al televisor", "Audio"),
    ("no hay sonido en las aplicaciones", "Audio"),
    ("el audio por bluetooth no funciona", "Audio"),
    ("el micrófono capta ruido de fondo excesivo", "Audio"),
    ("los altavoces emiten sonido demasiado bajo", "Audio"),
    ("la salida de audio muestra dispositivo no disponible", "Audio"),
    ("error realtek audio no instalado", "Audio"),
    ("el sonido surround 5.1 no funciona", "Audio"),
    ("el dispositivo de audio desaparece al reiniciar", "Audio"),
    ("el audio se retrasa al reproducir video", "Audio"),
    ("el conector frontal de audio del gabinete no funciona", "Audio"),
    ("los altavoces hacen clic al activarse", "Audio"),
    ("no hay sonido en videollamadas", "Audio"),
    ("el volumen se sube y baja solo sin control", "Audio"),
    ("el equalizador de audio no aplica cambios", "Audio"),

    # --------------------------------------------------------------- Temperatura
    ("el equipo se sobrecalienta constantemente", "Temperatura"),
    ("el procesador tiene temperatura muy alta", "Temperatura"),
    ("la GPU supera los 90 grados de temperatura", "Temperatura"),
    ("el ventilador del CPU gira muy rápido con ruido", "Temperatura"),
    ("el equipo se apaga solo por temperatura elevada", "Temperatura"),
    ("el disipador del procesador está extremadamente caliente", "Temperatura"),
    ("la pasta térmica del CPU está seca y deteriorada", "Temperatura"),
    ("el sistema activa el thermal throttling", "Temperatura"),
    ("los ventiladores hacen ruido a alta velocidad constante", "Temperatura"),
    ("el gabinete está muy caliente al tocarlo", "Temperatura"),
    ("temperatura de CPU mayor a 90 grados en reposo", "Temperatura"),
    ("el sistema reduce rendimiento por calor excesivo", "Temperatura"),
    ("los ventiladores del chasis no giran", "Temperatura"),
    ("el flujo de aire del case es deficiente", "Temperatura"),
    ("el disipador de la GPU está obstruido por polvo", "Temperatura"),
    ("el sistema indica CPU temperature error en BIOS", "Temperatura"),
    ("el equipo se apaga al jugar por sobrecalentamiento", "Temperatura"),
    ("el cooler del procesador no está bien sujeto", "Temperatura"),
    ("temperatura anormalmente alta en todos los sensores", "Temperatura"),
    ("el radiador del refrigerado líquido está obstruido", "Temperatura"),
    ("la bomba del water cooling no funciona", "Temperatura"),
    ("acumulación de polvo en ventiladores y disipadores", "Temperatura"),
    ("el equipo funciona bien en frío pero falla en caliente", "Temperatura"),
    ("los ventiladores giran pero no bajan la temperatura", "Temperatura"),
    ("el cooler tower no tiene pasta térmica aplicada", "Temperatura"),
    ("el equipo se apaga a los pocos minutos de encendido", "Temperatura"),
    ("el procesador hace throttling a 800MHz por calor", "Temperatura"),
    ("temperatura de VRM de la placa muy alta", "Temperatura"),
    ("alarma de temperatura activada en BIOS", "Temperatura"),
    ("el monitor de temperatura muestra valores críticos", "Temperatura"),

    # ----------------------------------------------------------------------- USB
    ("el puerto USB no funciona", "USB"),
    ("el dispositivo USB no es reconocido", "USB"),
    ("el teclado USB no responde", "USB"),
    ("el mouse USB no funciona", "USB"),
    ("el pendrive no aparece en el sistema", "USB"),
    ("la impresora USB no conecta", "USB"),
    ("el hub USB no da energía a los dispositivos", "USB"),
    ("error dispositivo USB desconocido", "USB"),
    ("los puertos USB traseros no funcionan", "USB"),
    ("el USB 3.0 funciona a velocidad USB 2.0", "USB"),
    ("el disco duro externo USB no conecta", "USB"),
    ("el puerto USB se desconecta y reconecta solo", "USB"),
    ("el controlador USB host está dañado", "USB"),
    ("error código 43 en dispositivo USB", "USB"),
    ("el lector de tarjetas USB no funciona", "USB"),
    ("la cámara web USB no es detectada", "USB"),
    ("los puertos USB frontales no tienen energía", "USB"),
    ("el USB type-C no funciona", "USB"),
    ("el gamepad USB no es reconocido por Windows", "USB"),
    ("la unidad de almacenamiento USB se expulsa sola", "USB"),
    ("error al transferir archivos por cable USB", "USB"),
    ("el USB se sobrecarga y apaga el dispositivo", "USB"),
    ("los puertos USB están quemados", "USB"),
    ("el controlador USB no aparece en administrador de dispositivos", "USB"),
    ("la tarjeta PCIe con puertos USB no es reconocida", "USB"),
    ("error power surge on USB port", "USB"),
    ("el puerto thunderbolt USB4 no funciona", "USB"),
    ("el headset USB no aparece en los dispositivos de audio", "USB"),
    ("el adaptador USB WiFi no conecta a redes", "USB"),
    ("Windows no detecta el dispositivo USB al conectar", "USB"),

    # ------------------------------------------------------------------- Drivers
    ("el driver del dispositivo está desactualizado", "Drivers"),
    ("error de driver causó pantalla azul BSOD", "Drivers"),
    ("el sistema operativo no encuentra el controlador", "Drivers"),
    ("la actualización de Windows rompió el driver", "Drivers"),
    ("el device manager muestra exclamaciones amarillas", "Drivers"),
    ("el driver de la impresora no instala correctamente", "Drivers"),
    ("conflicto de drivers en el sistema operativo", "Drivers"),
    ("el driver de audio fue eliminado automáticamente", "Drivers"),
    ("no encuentro el driver para mi hardware antiguo", "Drivers"),
    ("el chipset driver no está instalado", "Drivers"),
    ("el driver de la GPU da error al instalar", "Drivers"),
    ("el driver de red no tiene firma digital válida", "Drivers"),
    ("Windows Update instaló driver incorrecto", "Drivers"),
    ("error inf file missing en instalación de driver", "Drivers"),
    ("el driver causa inestabilidad y cuelgues del sistema", "Drivers"),
    ("no se puede instalar driver en Windows 11", "Drivers"),
    ("el controlador Bluetooth no instala", "Drivers"),
    ("error code 28 no driver installed para dispositivo", "Drivers"),
    ("el driver de captura de video falla al iniciar", "Drivers"),
    ("el scanner no tiene driver compatible con Windows 10", "Drivers"),
    ("el driver está corrupto y genera pantalla azul", "Drivers"),
    ("error driver irql not less or equal", "Drivers"),
    ("el controlador de pantalla táctil falla", "Drivers"),
    ("los drivers están desactualizados después de reinstalar Windows", "Drivers"),
    ("el driver de Thunderbolt no instala correctamente", "Drivers"),
    ("error system thread exception not handled por driver", "Drivers"),
    ("el driver de la tarjeta capturadora da error al cargar", "Drivers"),
    ("los drivers de chipset de la placa base no están instalados", "Drivers"),
    ("error page fault in nonpaged area causado por driver", "Drivers"),
    ("el driver de la tarjeta madre es incompatible con el sistema", "Drivers"),

    # ---------------------------------------------------------------- [DELL]
    ("[DELL XPS] pantalla con líneas verticales y artefactos gráficos", "Video"),
    ("[DELL XPS] thermal throttling severo bajo carga sostenida", "Temperatura"),
    ("[DELL INSPIRON] batería no carga ni es detectada", "Energia"),
    ("[DELL LATITUDE] WiFi Intel desaparece del administrador dispositivos", "Red"),
    ("[DELL] Dell Command Update rompe el driver de audio Realtek", "Drivers"),
    ("[DELL ALIENWARE] GPU no detectada después de actualización BIOS", "Video"),
    ("[DELL] USB-C Thunderbolt no carga ni transmite datos", "USB"),
    ("[DELL] SSD NVMe desaparece en BIOS tras actualización firmware", "Almacenamiento"),
    ("[DELL] no supera el POST después de flash de BIOS", "BIOS"),
    ("[DELL INSPIRON] ventilador siempre al máximo con ruido excesivo", "Temperatura"),
    ("[DELL XPS] pantalla OLED con manchas de quemado ghosting", "Video"),
    ("[DELL] Dell SupportAssist no detecta la batería del equipo", "Energia"),

    # ------------------------------------------------------------------ [HP]
    ("[HP PAVILION] batería al 0% no carga con adaptador HP original", "Energia"),
    ("[HP SPECTRE] pantalla OLED con flicker parpadeo intermitente", "Video"),
    ("[HP ELITEBOOK] HP Sure Start bloquea arranque del sistema operativo", "BIOS"),
    ("[HP OMEN] sobrecalentamiento severo jugando videojuegos", "Temperatura"),
    ("[HP] HP Support Assistant causa pantalla azul BSOD al actualizar", "Drivers"),
    ("[HP PAVILION] WiFi Realtek se desconecta cada 10 minutos", "Red"),
    ("[HP] audio Bang Olufsen no produce sonido en altavoces", "Audio"),
    ("[HP] puerto USB-C no reconoce ningún dispositivo conectado", "USB"),
    ("[HP] disco duro no detectado después de golpe o caída", "Almacenamiento"),
    ("[HP ENVY] pantalla táctil no responde al tacto", "USB"),
    ("[HP OMEN] ventiladores a máxima velocidad con ruido constante", "Temperatura"),
    ("[HP ELITEBOOK] HP PC Hardware Diagnostics muestra error disco", "Almacenamiento"),

    # --------------------------------------------------------------- [LENOVO]
    ("[LENOVO THINKPAD] algunas teclas del teclado no responden", "USB"),
    ("[LENOVO LEGION] GPU NVIDIA no se activa en juegos detectada integrada", "Video"),
    ("[LENOVO IDEAPAD] batería agotada en 30 minutos siendo nueva", "Energia"),
    ("[LENOVO THINKPAD] Lenovo Vantage no encuentra actualizaciones driver", "Drivers"),
    ("[LENOVO LEGION] thermal throttling con perfil rendimiento activo", "Temperatura"),
    ("[LENOVO YOGA] pantalla táctil no responde en modo tablet", "USB"),
    ("[LENOVO] Dolby Atmos audio con distorsión y cracks", "Audio"),
    ("[LENOVO THINKPAD] WiFi Intel AX200 desconexión frecuente", "Red"),
    ("[LENOVO] SSD M.2 no detectado después de reinstalar Windows", "Almacenamiento"),
    ("[LENOVO] no entra a BIOS con botón Novo ni con tecla F2", "BIOS"),
    ("[LENOVO LEGION] temperatura CPU 95 grados bajo carga de juegos", "Temperatura"),
    ("[LENOVO THINKPAD] TrackPoint y touchpad no responden", "USB"),

    # ---------------------------------------------------------------- [ASUS]
    ("[ASUS ROG] Armoury Crate causa BSOD pantalla azul al iniciar", "Drivers"),
    ("[ASUS VIVOBOOK] touchpad completamente inactivo no responde", "USB"),
    ("[ASUS ROG] GPU descarta señal HDMI al iniciar un juego", "Video"),
    ("[ASUS ZENSBOOK] ventilador siempre a máxima velocidad ruido", "Temperatura"),
    ("[ASUS] MyASUS no reconoce la batería del equipo", "Energia"),
    ("[ASUS ROG] sonido con cracks y distorsión en altavoces", "Audio"),
    ("[ASUS TUF] WiFi Mediatek se desconecta en partidas de juegos", "Red"),
    ("[ASUS] SSD desaparece después de actualización BIOS ASUS", "Almacenamiento"),
    ("[ASUS ROG] temperatura VRM muy alta con overclock activo", "Temperatura"),
    ("[ASUS] BIOS no permite cambiar orden de arranque boot order", "BIOS"),

    # --------------------------------------------------------------- [ACER]
    ("[ACER ASPIRE] batería inflamada hinchada no carga", "Energia"),
    ("[ACER NITRO] temperatura CPU 100 grados bajo carga de juegos", "Temperatura"),
    ("[ACER PREDATOR] PredatorSense no controla los ventiladores", "Temperatura"),
    ("[ACER] WiFi Atheros muy lento o se desconecta solo", "Red"),
    ("[ACER] driver Realtek audio con error al instalar en Windows", "Drivers"),
    ("[ACER] SSD SATA no detectado en slot óptico conversión", "Almacenamiento"),
    ("[ACER SWIFT] pantalla flickering parpadeo en brillo bajo", "Video"),
    ("[ACER] BIOS no permite cambiar el orden de arranque", "BIOS"),
    ("[ACER] puerto USB 3.0 no entrega energía a dispositivos", "USB"),
    ("[ACER ASPIRE] sonido con eco y distorsión en altavoces", "Audio"),

    # ----------------------------------------------------------------- [MSI]
    ("[MSI GAMING] MSI Center Dragon Center conflicto con antivirus BSOD", "Drivers"),
    ("[MSI] GPU discreta no activa NVIDIA Optimus no funciona", "Video"),
    ("[MSI GE] temperatura 98 grados bajo carga total de juegos", "Temperatura"),
    ("[MSI] batería no carga más del 80% con MSI Center activo", "Energia"),
    ("[MSI] audio Nahimic con latencia alta y distorsión", "Audio"),
    ("[MSI CREATOR] WiFi Killer desconexión intermitente en uso", "Red"),
    ("[MSI] SSD secundario no detectado en segundo slot M.2", "Almacenamiento"),
    ("[MSI] BIOS no guarda perfil XMP de RAM al reiniciar", "BIOS"),
    ("[MSI] USB-C no funciona para carga ni transmisión datos", "USB"),
    ("[MSI GS] pantalla 144Hz cae automáticamente a 60Hz sola", "Video"),
]


class DiagnosticModel:
    """
    Clasificador de síntomas de hardware: TF-IDF + LinearSVC calibrado.
    9 categorías de hardware con umbral de confianza configurable.
    """

    CATEGORIES = [
        "Energia", "Video", "BIOS", "Almacenamiento",
        "Red", "Audio", "Temperatura", "USB", "Drivers",
    ]

    def __init__(self, extra_data: list[tuple[str, str]] | None = None):
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, 2),
                min_df=1,
                analyzer="word",
                strip_accents="unicode",
                lowercase=True,
                sublinear_tf=True,
            )),
            ("clf", CalibratedClassifierCV(
                LinearSVC(C=1.0, max_iter=2000, class_weight="balanced"),
                cv=3,
            )),
        ])
        self._extra_data: list[tuple[str, str]] = extra_data or []
        self._train()

    def _train(self) -> None:
        data = TRAINING_DATA + self._extra_data
        texts, labels = zip(*data)
        self.pipeline.fit(texts, labels)

    def retrain(self, new_examples: list[tuple[str, str]]) -> None:
        """Agrega nuevos ejemplos validados y re-entrena el modelo."""
        self._extra_data.extend(new_examples)
        self._train()

    def predict(self, symptom_text: str) -> dict:
        """
        Clasifica el síntoma y devuelve categoría, confianza y flag de baja confianza.

        Returns:
            {
                "category": str,
                "confidence": float,
                "low_confidence": bool,   # True si confianza < CONFIDENCE_THRESHOLD
                "all_probabilities": dict
            }
        """
        probs = self.pipeline.predict_proba([symptom_text])[0]
        classes = self.pipeline.classes_
        category_index = int(np.argmax(probs))
        confidence = round(float(probs[category_index]), 4)

        return {
            "category": str(classes[category_index]),
            "confidence": confidence,
            "low_confidence": confidence < CONFIDENCE_THRESHOLD,
            "all_probabilities": {
                str(cls): round(float(p), 4)
                for cls, p in zip(classes, probs)
            },
        }
