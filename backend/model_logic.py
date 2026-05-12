"""
model_logic.py — Motor de IA para diagnóstico de hardware.

Usa TF-IDF + Naive Bayes para clasificar síntomas en 6 categorías:
Energia, Video, BIOS, Almacenamiento, Temperatura, Red.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import numpy as np


# Dataset de entrenamiento: (síntoma, categoría)
# 310+ ejemplos con marcas y modelos reales de hardware
TRAINING_DATA = [

    # ─────────────────────────────────────────────────────────────
    # CATEGORÍA: Energía
    # Marcas: Corsair, EVGA, Seasonic, Thermaltake, Cooler Master, be quiet!
    # ─────────────────────────────────────────────────────────────
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
    ("la PSU no da voltaje", "Energia"),
    ("el sistema no tiene corriente eléctrica", "Energia"),
    ("el cable de poder está bien pero no enciende", "Energia"),
    ("PC se reinicia constantemente", "Energia"),
    ("apagado repentino sin motivo aparente", "Energia"),
    ("conector ATX 24 pin mal conectado en motherboard", "Energia"),
    ("cable EPS 8 pin CPU no conectado, PC no arranca", "Energia"),
    ("fusible de fuente quemado, sin corriente", "Energia"),
    ("la PSU hace ruido extraño y se reinicia", "Energia"),
    ("voltaje de 12V inestable causando reinicios", "Energia"),
    ("la UPS no da corriente a la PC", "Energia"),
    ("protección de sobretensión activada en PSU", "Energia"),
    ("el interruptor trasero de la fuente está apagado", "Energia"),
    ("cables de energía flojos en la motherboard", "Energia"),
    ("PSU insuficiente para RTX 3080, se apaga bajo carga", "Energia"),
    ("la fuente truena al encender y se apaga", "Energia"),
    ("cortocircuito en la fuente quemó los fusibles", "Energia"),
    ("pico de corriente dañó la fuente de poder", "Energia"),
    ("batería de UPS descargada, PC se apaga en corte", "Energia"),
    # Corsair
    ("fuente Corsair RM850x no enciende el equipo", "Energia"),
    ("PSU Corsair no da señal de vida", "Energia"),
    ("Corsair SF750 SFX no responde al botón de encendido", "Energia"),
    ("Corsair HX1200i reporta error OCP, se apaga", "Energia"),
    ("fuente Corsair CX650M no da los 12V correctos", "Energia"),
    # EVGA
    ("fuente EVGA SuperNOVA 650W se apaga sola", "Energia"),
    ("EVGA G6 750W hace clic y no arranca", "Energia"),
    ("la fuente EVGA SuperNOVA 1000 G6 no da 12V", "Energia"),
    ("EVGA 80 Plus Gold PSU protección OVP activada", "Energia"),
    # Seasonic
    ("Seasonic Focus GX-850 no enciende con la placa", "Energia"),
    ("PSU Seasonic Prime TX-1000 Titanium sin voltaje", "Energia"),
    ("Seasonic FOCUS PX-750 protección por cortocircuito", "Energia"),
    # Thermaltake
    ("fuente Thermaltake Toughpower GF1 850W sin voltaje", "Energia"),
    ("Thermaltake Smart 600W ventilador no gira, PC muerta", "Energia"),
    # Cooler Master
    ("Cooler Master MWE 750W Gold ventilador parado", "Energia"),
    ("Cooler Master V850 SFX Gold no enciende la placa ASUS", "Energia"),
    # be quiet!
    ("be quiet! Straight Power 11 1000W se apaga bajo carga", "Energia"),
    ("be quiet! Pure Power 11 FM 650W no da corriente", "Energia"),
    # Platform Intel
    ("PC Intel i9-13900K con Z790 no enciende desde header", "Energia"),
    ("sistema Intel i7-12700K se reinicia solo sin razón", "Energia"),
    # Platform AMD
    ("PC Ryzen 9 5900X con MSI X570 se apaga repentinamente", "Energia"),
    ("AMD Ryzen 7 5800X3D fuente no da potencia suficiente", "Energia"),

    # ─────────────────────────────────────────────────────────────
    # CATEGORÍA: Video
    # Marcas: NVIDIA RTX/GTX, AMD Radeon RX, ASUS, MSI, Gigabyte,
    #         monitores LG, Samsung, ASUS, Acer, BenQ
    # ─────────────────────────────────────────────────────────────
    ("no hay imagen en el monitor", "Video"),
    ("pantalla negra al encender", "Video"),
    ("la tarjeta de video falla", "Video"),
    ("el monitor no recibe señal", "Video"),
    ("artefactos visuales en pantalla", "Video"),
    ("la pantalla parpadea constantemente", "Video"),
    ("colores distorsionados en la pantalla", "Video"),
    ("resolución incorrecta en Windows", "Video"),
    ("la GPU no es detectada por el sistema", "Video"),
    ("pantalla azul con artefactos gráficos", "Video"),
    ("líneas verticales en el monitor", "Video"),
    ("driver de video corrupto", "Video"),
    ("no hay salida HDMI", "Video"),
    ("DisplayPort sin señal en monitor", "Video"),
    ("la tarjeta gráfica hace ruido y no da imagen", "Video"),
    ("el cable HDMI está dañado y no transmite imagen", "Video"),
    ("la ranura PCIe x16 dañada, GPU no funciona", "Video"),
    ("la VRAM de la GPU está dañada, artefactos visuales", "Video"),
    ("falla VRM en tarjeta gráfica, apagados bajo carga", "Video"),
    ("la GPU integrada Intel UHD 770 no da salida de video", "Video"),
    ("AMD Vega integrada Ryzen 5700G sin imagen", "Video"),
    ("adaptador DVI a HDMI no transmite señal", "Video"),
    ("resolución 4K no soportada por cable HDMI 1.4", "Video"),
    ("frecuencia 144Hz no funciona en monitor", "Video"),
    ("G-Sync no activado correctamente en ASUS", "Video"),
    # NVIDIA RTX 40 series
    ("RTX 4090 no detectada en ranura PCIe x16", "Video"),
    ("RTX 4080 pantalla negra después de instalar drivers", "Video"),
    ("RTX 4070 Ti sin señal HDMI en monitor LG", "Video"),
    ("RTX 4070 Super artefactos visuales en juegos", "Video"),
    # NVIDIA RTX 30 series
    ("RTX 3090 Ti artefactos visuales en resolución 4K", "Video"),
    ("RTX 3080 pantalla negra bajo carga en juegos", "Video"),
    ("RTX 3070 sin imagen, conectores PCIe flojos", "Video"),
    ("RTX 3060 Ti driver NVIDIA 546 causa BSOD", "Video"),
    ("RTX 3060 no da imagen, conectar al puerto GPU no integrado", "Video"),
    # NVIDIA GTX series
    ("GeForce GTX 1080 Ti driver corrupto crash", "Video"),
    ("GTX 1660 Super pantalla parpadea en 1080p", "Video"),
    # AMD Radeon RX 7000
    ("Radeon RX 7900 XTX pantalla verde con distorsión", "Video"),
    ("RX 7800 XT artefactos en resolución 1440p", "Video"),
    # AMD Radeon RX 6000
    ("Radeon RX 6800 XT no detectada por Windows 11", "Video"),
    ("RX 6700 XT artefactos en juegos DirectX 12", "Video"),
    ("RX 6600 XT líneas horizontales en pantalla", "Video"),
    # ASUS GPU
    ("ASUS TUF RTX 3080 sin imagen en DisplayPort 1.4", "Video"),
    ("ASUS ROG STRIX RX 6800 XT falla ventiladores y pantalla", "Video"),
    ("ASUS ROG STRIX RTX 4090 no detectada en PCIe", "Video"),
    # MSI GPU
    ("MSI Gaming X Trio RTX 4070 pantalla parpadea", "Video"),
    ("MSI Ventus RX 6700 no detectada en ranura PCIe x16", "Video"),
    ("MSI SUPRIM X RTX 3080 Ti artefactos VRAM dañada", "Video"),
    # Gigabyte GPU
    ("Gigabyte AORUS RTX 3090 artefactos en 4K HDR", "Video"),
    ("Gigabyte Eagle RX 6600 sin señal HDMI", "Video"),
    # Monitores
    ("monitor LG 27GP850-B sin señal DisplayPort 1.4", "Video"),
    ("Samsung Odyssey G7 pantalla negra intermitente", "Video"),
    ("ASUS ROG Swift PG279QM no enciende", "Video"),
    ("Acer Predator XB273K sin señal HDMI 2.1 en 4K", "Video"),
    ("BenQ MOBIUZ EX2710Q frecuencia 165Hz no funciona", "Video"),

    # ─────────────────────────────────────────────────────────────
    # CATEGORÍA: BIOS
    # Marcas: ASUS, MSI, Gigabyte, ASRock, Intel, AMD
    # ─────────────────────────────────────────────────────────────
    ("la computadora no pasa el POST", "BIOS"),
    ("pitidos al encender la computadora", "BIOS"),
    ("beep codes al iniciar el sistema", "BIOS"),
    ("error de BIOS al arrancar", "BIOS"),
    ("la RAM no es detectada en el BIOS", "BIOS"),
    ("necesito resetear el BIOS a valores de fábrica", "BIOS"),
    ("configuración del BIOS perdida tras corte de luz", "BIOS"),
    ("la pila del CMOS está descargada", "BIOS"),
    ("error de memoria al arrancar el sistema", "BIOS"),
    ("el sistema no detecta el procesador instalado", "BIOS"),
    ("falla en la inicialización del hardware POST", "BIOS"),
    ("pantalla de BIOS no carga, se queda en negro", "BIOS"),
    ("pitido largo al encender la motherboard", "BIOS"),
    ("la motherboard no reconoce los módulos RAM", "BIOS"),
    ("error al iniciar el OS desde BIOS UEFI", "BIOS"),
    ("jumper CMOS no resetea la configuración", "BIOS"),
    ("botón Clear CMOS no funciona en placa madre", "BIOS"),
    ("actualización BIOS interrumpida, placa no arranca", "BIOS"),
    ("BIOS corrupto después de corte de luz", "BIOS"),
    ("UEFI Secure Boot bloquea arranque de Linux", "BIOS"),
    ("Fast Boot en BIOS impide acceder al menú UEFI", "BIOS"),
    ("la fecha y hora del BIOS se resetea sola", "BIOS"),
    ("PCIe slot no habilitado en BIOS para segunda GPU", "BIOS"),
    ("XMP no se activa, RAM corre a 2133MHz solo", "BIOS"),
    ("perfil DOCP no estable con Ryzen en AM4", "BIOS"),
    # ASUS motherboard
    ("ASUS ROG Maximus Z790 Hero no pasa POST con XMP 6000", "BIOS"),
    ("ASUS TUF Gaming B550-PLUS pitido largo uno corto RAM", "BIOS"),
    ("ASUS Prime X570-P no reconoce Ryzen 9 5900X sin update", "BIOS"),
    ("ASUS Q-Flash Plus falla actualizando BIOS sin CPU", "BIOS"),
    ("ASUS debug LED código 00 se congela en POST", "BIOS"),
    ("ASUS EZ Flash 3 falla al actualizar desde USB", "BIOS"),
    ("ASUS ROG STRIX B660-F error A2 POST no detecta CPU", "BIOS"),
    # MSI motherboard
    ("MSI MAG B660M Mortar DDR4 no detecta RAM Corsair XMP", "BIOS"),
    ("MSI MEG Z690 ACE pitidos cortos al encender", "BIOS"),
    ("MSI Click BIOS 5 no guarda configuración overclock", "BIOS"),
    ("MSI X570-A PRO falla POST con dos módulos RAM instalados", "BIOS"),
    ("MSI MEG X670E ACE Q-LED rojo RAM, no pasa POST", "BIOS"),
    ("MSI MAG Z790 Tomahawk DDR5 no reconoce G.Skill 6400", "BIOS"),
    # Gigabyte motherboard
    ("Gigabyte Z790 AORUS Master pantalla negra en POST", "BIOS"),
    ("Gigabyte B550M DS3H pila CR2032 descargada, BIOS reset", "BIOS"),
    ("Gigabyte @BIOS error al actualizar firmware Q-Flash", "BIOS"),
    ("Gigabyte X670E AORUS Extreme no detecta Ryzen 9 7950X", "BIOS"),
    # ASRock motherboard
    ("ASRock B450M PRO4 no reconoce Ryzen 5600X sin update BIOS", "BIOS"),
    ("ASRock Z690 Steel Legend pitido POST falla detección VGA", "BIOS"),
    ("ASRock Z790 Taichi debug LED 00 se congela", "BIOS"),
    # Intel platform
    ("Intel Core i9-13900K no detectado en placa Z790", "BIOS"),
    ("LGA1700 socket con pin doblado, CPU no reconocida", "BIOS"),
    ("Intel i5-12600K requiere BIOS update para DDR5 XMP", "BIOS"),
    ("Intel i9-14900K requiere actualización microcode", "BIOS"),
    # AMD platform
    ("AMD Ryzen 9 7950X necesita BIOS AGESA 1.0.0.7 o superior", "BIOS"),
    ("AM5 socket no detecta Ryzen 7 7700X correctamente", "BIOS"),
    ("Ryzen 5 5600 requiere actualización BIOS en X570", "BIOS"),
    # RAM specific
    ("Corsair Vengeance DDR4 3200MHz no detectada en BIOS ASUS", "BIOS"),
    ("G.Skill Trident Z5 DDR5 6400MHz no bootea con XMP", "BIOS"),
    ("Kingston Fury Beast DDR5 no compatible con perfil XMP3", "BIOS"),
    ("dos módulos Crucial Ballistix DDR4 no detectados", "BIOS"),

    # ─────────────────────────────────────────────────────────────
    # CATEGORÍA: Almacenamiento
    # Marcas: Seagate, WD, Samsung, Kingston, Crucial, Toshiba
    # ─────────────────────────────────────────────────────────────
    ("el disco duro no es detectado por el sistema", "Almacenamiento"),
    ("el SSD no aparece en el administrador de discos", "Almacenamiento"),
    ("error de lectura del disco duro", "Almacenamiento"),
    ("el sistema no encuentra el dispositivo de arranque", "Almacenamiento"),
    ("el HDD hace ruido extraño al girar", "Almacenamiento"),
    ("no bootea desde el disco principal", "Almacenamiento"),
    ("error SMART en el disco duro", "Almacenamiento"),
    ("archivos corruptos en el almacenamiento", "Almacenamiento"),
    ("el disco duro está lleno y el sistema es muy lento", "Almacenamiento"),
    ("no puedo acceder a mis archivos en el disco", "Almacenamiento"),
    ("el SSD NVMe no aparece en el BIOS UEFI", "Almacenamiento"),
    ("sistema de archivos NTFS corrompido", "Almacenamiento"),
    ("el disco hace click click repetitivo", "Almacenamiento"),
    ("error al leer el sector de arranque MBR", "Almacenamiento"),
    ("velocidad de disco extremadamente baja en benchmark", "Almacenamiento"),
    ("cable SATA dañado causa errores de lectura", "Almacenamiento"),
    ("puerto SATA III dañado en placa madre", "Almacenamiento"),
    ("tabla de particiones GPT dañada, no bootea Windows", "Almacenamiento"),
    ("MBR corrompido, Windows no inicia correctamente", "Almacenamiento"),
    ("disco duro externo cae y deja de ser reconocido", "Almacenamiento"),
    ("error 0x80070057 al formatear disco en Windows", "Almacenamiento"),
    ("NTFS no puede montarse, necesita chkdsk urgente", "Almacenamiento"),
    ("SSD lleno al 95% ralentiza el sistema operativo", "Almacenamiento"),
    ("disco duro de laptop no reconocido en bahía SATA", "Almacenamiento"),
    ("TRIM no funciona correctamente en SSD antiguo", "Almacenamiento"),
    ("adaptador M.2 a PCIe no reconoce el SSD NVMe", "Almacenamiento"),
    ("clonación de disco fallida con Macrium Reflect", "Almacenamiento"),
    # Seagate
    ("Seagate Barracuda 2TB no detectado en puerto SATA III", "Almacenamiento"),
    ("Seagate Exos 4TB error SMART reallocated sectors alto", "Almacenamiento"),
    ("Seagate IronWolf 6TB NAS disco hace click de la muerte", "Almacenamiento"),
    ("Seagate FireCuda 530 NVMe 2TB no aparece en Windows 11", "Almacenamiento"),
    ("Seagate Expansion 4TB USB no monta en Windows", "Almacenamiento"),
    ("Seagate SkyHawk 2TB DVR no detectado en sistema", "Almacenamiento"),
    # WD Western Digital
    ("WD Blue 1TB SATA lento con sectores defectuosos SMART", "Almacenamiento"),
    ("WD Black SN850X NVMe 2TB no detectado en ranura M.2", "Almacenamiento"),
    ("WD Red Plus 4TB NAS no detectado por BIOS ASUS", "Almacenamiento"),
    ("Western Digital My Passport 2TB USB no monta en Windows", "Almacenamiento"),
    ("WD Green 240GB SATA velocidad de escritura muy baja", "Almacenamiento"),
    ("WD Gold 8TB Enterprise error SMART en servidor", "Almacenamiento"),
    ("WD SN770 NVMe Gen4 no reconocido en slot M.2 B-key", "Almacenamiento"),
    # Samsung
    ("Samsung 870 EVO 1TB no detectado en puerto SATA II", "Almacenamiento"),
    ("Samsung 980 Pro NVMe temperatura extrema bajo carga", "Almacenamiento"),
    ("Samsung 990 Pro M.2 velocidad real muy inferior al spec", "Almacenamiento"),
    ("Samsung T7 Shield USB 3.2 externo no reconocido", "Almacenamiento"),
    ("Samsung 870 QVO 4TB SMART muestra pending sectors", "Almacenamiento"),
    # Kingston
    ("Kingston A2000 NVMe no aparece en administrador disco", "Almacenamiento"),
    ("Kingston NV2 SSD 1TB velocidad real muy inferior specs", "Almacenamiento"),
    ("Kingston DataTraveler USB corrompido, no monta", "Almacenamiento"),
    # Crucial
    ("Crucial MX500 2TB corrompido después de corte de luz", "Almacenamiento"),
    ("Crucial P3 Plus NVMe no detectado en slot M.2 E-key", "Almacenamiento"),
    ("Crucial BX500 velocidad de escritura cae tras 50% uso", "Almacenamiento"),
    # Toshiba
    ("Toshiba P300 2TB HDD ruido de raspado metálico", "Almacenamiento"),
    ("Toshiba X300 4TB error SMART en PC de escritorio", "Almacenamiento"),

    # ─────────────────────────────────────────────────────────────
    # CATEGORÍA: Temperatura
    # Marcas: Noctua, be quiet!, Cooler Master, Corsair, NZXT,
    #         DeepCool, ARCTIC, Intel, AMD
    # ─────────────────────────────────────────────────────────────
    ("la CPU se sobrecalienta y el sistema se apaga", "Temperatura"),
    ("el procesador llega a 100 grados bajo carga", "Temperatura"),
    ("temperatura excesiva en la GPU durante juegos", "Temperatura"),
    ("el sistema se apaga por protección térmica del CPU", "Temperatura"),
    ("el disipador del CPU está suelto o mal instalado", "Temperatura"),
    ("la pasta térmica del procesador está seca y resquebrajada", "Temperatura"),
    ("los ventiladores del gabinete no giran", "Temperatura"),
    ("temperatura ambiente alta causa throttling del CPU", "Temperatura"),
    ("el flujo de aire del gabinete es insuficiente", "Temperatura"),
    ("filtros de polvo obstruidos causan altas temperaturas", "Temperatura"),
    ("disipador sin pasta térmica, CPU a 95 grados en reposo", "Temperatura"),
    ("thermal throttling en laptop por acumulación de polvo", "Temperatura"),
    ("equipo Lenovo sobrecalienta, ventilador bloqueado", "Temperatura"),
    ("HP laptop alcanza 98 grados y se apaga solo", "Temperatura"),
    ("ventiladores parados en tarjeta gráfica bajo carga", "Temperatura"),
    # Noctua coolers
    ("Noctua NH-D15 mal instalado, CPU Intel i9 a 95 grados", "Temperatura"),
    ("Noctua NH-U12S no baja temperatura Ryzen 9 5900X", "Temperatura"),
    ("Noctua NF-A12x25 ventilador parado, airflow insuficiente", "Temperatura"),
    # be quiet! coolers
    ("be quiet! Dark Rock Pro 4 no baja temperatura Intel i9", "Temperatura"),
    ("be quiet! Pure Rock 2 insuficiente para Ryzen 7 5800X", "Temperatura"),
    # Cooler Master coolers
    ("Cooler Master Hyper 212 EVO insuficiente para i7-13700K", "Temperatura"),
    ("Cooler Master MasterLiquid ML360R bomba no funciona", "Temperatura"),
    # Corsair AIO
    ("Corsair H150i Elite Capellix bomba no funciona i9 a 100", "Temperatura"),
    ("Corsair iCUE H100i RGB PRO XT CPU a 95 grados", "Temperatura"),
    ("Corsair H115i temperatura elevada Ryzen 9 5950X", "Temperatura"),
    # NZXT AIO
    ("NZXT Kraken X73 RGB bomba ruidosa y CPU caliente", "Temperatura"),
    ("NZXT Kraken Z63 temperatura elevada Intel i9-13900K", "Temperatura"),
    # DeepCool coolers
    ("DeepCool ASSASSIN IV mal montado, throttling constante", "Temperatura"),
    ("DeepCool AK620 insuficiente para i9-12900K con OC", "Temperatura"),
    # ARCTIC coolers
    ("ARCTIC Liquid Freezer II 360 temperatura alta en carga", "Temperatura"),
    ("ARCTIC Freezer 34 eSports ventilador parado", "Temperatura"),
    # CPU specific thermal
    ("Intel i9-13900K excede 100 grados en modo performance", "Temperatura"),
    ("Intel i9-14900K temperatura crítica sin OC", "Temperatura"),
    ("Intel i7-12700K pasta térmica desgastada en socket", "Temperatura"),
    ("AMD Ryzen 9 7950X temperaturas 95 grados sin overclock", "Temperatura"),
    ("AMD Ryzen 7 5800X3D caliente en reposo 60 grados AMD", "Temperatura"),
    # GPU thermal
    ("RTX 3080 temperatura GPU 95 grados en juego 4K", "Temperatura"),
    ("RX 6800 XT pasta térmica de fábrica seca y cuarteada", "Temperatura"),
    ("GPU throttling a 83 grados límite de temperatura NVDIA", "Temperatura"),
    ("RTX 4090 temperatura VRM excede 110 grados bajo carga", "Temperatura"),
    # Storage thermal
    ("SSD M.2 Samsung 980 Pro sin disipador, throttling 80C", "Temperatura"),
    ("VRM de motherboard MSI sin disipador se calienta OC", "Temperatura"),

    # ─────────────────────────────────────────────────────────────
    # CATEGORÍA: Red
    # Marcas: Intel, Realtek, Killer, TP-Link, ASUS, Fenvi
    # ─────────────────────────────────────────────────────────────
    ("no hay conexión a internet en la PC", "Red"),
    ("el adaptador de red no funciona", "Red"),
    ("WiFi no conecta a ninguna red", "Red"),
    ("la red local LAN no funciona", "Red"),
    ("el cable Ethernet no tiene señal", "Red"),
    ("tarjeta de red no detectada en Windows", "Red"),
    ("driver de red desactualizado o corrupto", "Red"),
    ("ping muy alto, conexión de internet inestable", "Red"),
    ("velocidad de internet muy baja en equipo", "Red"),
    ("el adaptador WiFi se desconecta solo cada minuto", "Red"),
    ("cable Ethernet Cat5e dañado, sin conexión LAN", "Red"),
    ("switch de red apagado, sin LAN en el equipo", "Red"),
    ("dirección IP duplicada en la red local", "Red"),
    ("DNS configurado incorrectamente, no resuelve web", "Red"),
    ("firewall de Windows bloquea conexión a internet", "Red"),
    ("proxy mal configurado impide la navegación web", "Red"),
    ("VPN causa conflicto con adaptador de red Realtek", "Red"),
    ("router DHCP no asigna IP al equipo correctamente", "Red"),
    ("MTU incorrecto causa problemas de conectividad", "Red"),
    ("controlador de red en modo ahorro energía, se corta", "Red"),
    ("tarjeta de red PCIe sin energía suficiente del slot", "Red"),
    ("interfaz de red en estado Limited Access Windows 11", "Red"),
    ("actualización Windows 11 22H2 dañó el driver de red", "Red"),
    ("antivirus bloquea el adaptador de red virtual VPN", "Red"),
    ("la tarjeta de red PCIe 2.5GbE no reconocida en BIOS", "Red"),
    # Intel NIC
    ("Intel I225-V 2.5Gbps LAN no detectada en BIOS Z690", "Red"),
    ("driver Intel i219-V causa BSOD en Windows 11 22H2", "Red"),
    ("Intel WiFi 6 AX200 no conecta a redes 5GHz", "Red"),
    ("Intel Killer E3100X LAN intermitente en juegos online", "Red"),
    ("Intel WiFi 6E AX210 no detecta red 6GHz correctamente", "Red"),
    # Realtek NIC
    ("Realtek RTL8125B 2.5GbE sin driver en Windows", "Red"),
    ("Realtek PCIe GbE driver no instala en Windows 11", "Red"),
    ("Realtek Ethernet adaptador desactivado en BIOS ASUS", "Red"),
    ("Realtek 8811CU USB WiFi no conecta correctamente", "Red"),
    # WiFi adapters
    ("ASUS PCE-AX58BT WiFi 6 PCIe no detecta redes 5GHz", "Red"),
    ("TP-Link Archer TX3000E PCIe WiFi 6 no conecta", "Red"),
    ("adaptador USB WiFi TP-Link TL-WN823N velocidad lenta", "Red"),
    ("Fenvi FV-T919 Bluetooth WiFi no detectada en Windows", "Red"),
]


class DiagnosticModel:
    """
    Clasificador de síntomas de hardware usando TF-IDF + Naive Bayes.
    Predice la categoría del problema y devuelve la confianza de la predicción.
    Soporta 6 categorías: Energia, Video, BIOS, Almacenamiento, Temperatura, Red.
    """

    CATEGORIES = ["Energia", "Video", "BIOS", "Almacenamiento", "Temperatura", "Red"]

    def __init__(self):
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, 2),
                min_df=1,
                analyzer="word",
                strip_accents="unicode",
                lowercase=True,
            )),
            ("clf", MultinomialNB(alpha=0.3)),
        ])
        self._train()

    def _train(self):
        texts, labels = zip(*TRAINING_DATA)
        self.pipeline.fit(texts, labels)

    def predict(self, symptom_text: str) -> dict:
        """
        Clasifica el síntoma y devuelve categoría + confianza + todas las probabilidades.

        Args:
            symptom_text: Texto del síntoma, puede incluir marca y modelo del hardware.

        Returns:
            {
                "category": str,
                "confidence": float,
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
