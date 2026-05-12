-- ============================================================
-- TechDiag Pro — Schema SQL v2.0
-- Asistente Inteligente de Soporte Técnico de Hardware
-- Base de datos: Supabase (PostgreSQL)
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ------------------------------------------------------------
-- Tabla: catalog_solutions
-- Catálogo de soluciones técnicas detalladas por categoría.
-- Incluye marcas, modelos y herramientas específicas.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS catalog_solutions (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    category        VARCHAR(50) NOT NULL,
    solution_text   TEXT        NOT NULL,
    hardware_specs  JSONB       DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_catalog_solutions_category
    ON catalog_solutions (category);

-- ------------------------------------------------------------
-- Tabla: diagnosis_logs
-- Registro histórico con marca y modelo del hardware.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS diagnosis_logs (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_query          TEXT        NOT NULL,
    hardware_brand      VARCHAR(100),
    hardware_model      VARCHAR(200),
    predicted_category  VARCHAR(50) NOT NULL,
    accuracy            NUMERIC(5,4),
    solution_provided   TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_diagnosis_logs_created_at
    ON diagnosis_logs (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_diagnosis_logs_category
    ON diagnosis_logs (predicted_category);
CREATE INDEX IF NOT EXISTS idx_diagnosis_logs_brand
    ON diagnosis_logs (hardware_brand);

-- ============================================================
-- Catálogo de soluciones técnicas detalladas
-- ============================================================

INSERT INTO catalog_solutions (category, solution_text, hardware_specs) VALUES

-- ────────────────────────────────────────────────────────────
-- ENERGÍA
-- ────────────────────────────────────────────────────────────
('Energia',
 'DIAGNÓSTICO DE FUENTE DE PODER (PSU):

1. VERIFICACIÓN BÁSICA
   • Comprueba que el interruptor trasero de la PSU esté en posición ON (I).
   • Verifica que el cable de poder esté bien conectado a la PSU y al tomacorriente.
   • Prueba con otro cable de poder o en otro tomacorriente diferente.

2. TEST PAPERCLIP (sin PC encendida)
   • Desconecta la PSU de la placa madre.
   • Cortocircuita los pines PS-ON (verde) y COM (negro) del conector ATX 24-pin con un clip.
   • Si el ventilador de la PSU gira → la PSU funciona. Si no gira → PSU defectuosa.

3. MEDICIÓN DE VOLTAJES (con multímetro)
   • +12V (cable amarillo): debe estar entre 11.4V y 12.6V
   • +5V (cable rojo): debe estar entre 4.75V y 5.25V
   • +3.3V (cable naranja): debe estar entre 3.14V y 3.47V
   • Variaciones fuera de rango indican PSU defectuosa.

4. CONECTORES A VERIFICAR
   • ATX 24-pin: completamente insertado en la placa madre.
   • EPS 8-pin (o 4+4-pin): cable de CPU conectado cerca del socket.
   • PCIe 8-pin (o 6+2-pin): para GPUs — RTX 3080/4090 requieren 2-3 conectores.
   • Conector de 16 pines 12VHPWR: obligatorio para RTX 4090/4080 — no doblar a 90°.

5. MARCAS Y WATTAJE RECOMENDADO
   • Corsair RM850x / HX1200i — calidad premium, garantía 10 años
   • Seasonic Focus GX-850 / Prime TX-1000 — referencia en estabilidad
   • EVGA SuperNOVA 850 G6 / 1000 G6 — excelente relación calidad-precio
   • be quiet! Straight Power 11 / Dark Power Pro 12 — silenciosas y estables
   • Para RTX 4090 + i9: mínimo 1000W 80 Plus Gold',
 '{"components": ["PSU", "Cable ATX 24-pin", "Cable EPS 8-pin", "Conector PCIe"], "brands": ["Corsair", "EVGA", "Seasonic", "be quiet!", "Thermaltake", "Cooler Master"], "tools_required": ["Multímetro", "Clip metálico"], "severity": "alta", "estimated_time": "30-60 min"}'
),

('Energia',
 'APAGADOS REPENTINOS Y REINICIOS INESPERADOS:

1. CAUSA: SOBRECALENTAMIENTO
   • Monitorea temperaturas con HWiNFO64 o Core Temp antes del apagado.
   • CPU no debe superar 90°C (Intel) o 95°C (AMD Ryzen) bajo carga sostenida.
   • Limpia disipador y ventiladores de polvo con aire comprimido.
   • Reaplica pasta térmica (Noctua NT-H1, Thermal Grizzly Kryonaut, Arctic MX-6).

2. CAUSA: PSU INSUFICIENTE PARA EL SISTEMA
   • Calcula consumo: i9-13900K (~250W) + RTX 4090 (~450W) + resto = ~850W mínimo.
   • Usa calculadora de wattaje de OuterVision o Corsair para tu configuración.
   • Una PSU sobredimensionada es más eficiente y duradera.

3. CAUSA: VOLTAJE INESTABLE
   • Usa un UPS/regulador de voltaje si hay fluctuaciones en la red eléctrica.
   • Verifica en BIOS que los voltajes del CPU (Vcore) no estén sobrevoltados por OC.

4. CAUSA: FALLA DE CONDENSADORES
   • Inspecciona visualmente la placa madre y PSU en busca de condensadores abultados.
   • Condensadores dañados requieren reemplazo profesional de la unidad.',
 '{"components": ["PSU", "CPU", "Disipador", "Pasta térmica", "UPS"], "tools_required": ["HWiNFO64", "Core Temp", "Pasta térmica"], "severity": "media", "estimated_time": "45-90 min"}'
),

-- ────────────────────────────────────────────────────────────
-- VIDEO
-- ────────────────────────────────────────────────────────────
('Video',
 'DIAGNÓSTICO SIN SEÑAL DE VIDEO / PANTALLA NEGRA:

1. VERIFICACIÓN DE CONEXIONES
   • Conecta el monitor DIRECTAMENTE al puerto de la GPU dedicada (no al de la placa madre).
   • Las placas con GPU integrada (Intel UHD, AMD Vega) tienen puertos separados — usa el de la GPU.
   • Prueba con otro cable HDMI o DisplayPort. Cables HDMI 1.4 no soportan 4K@60Hz ni 144Hz.
   • Cable HDMI 2.1 requerido para 4K@120Hz o 8K@60Hz.

2. REINSTALACIÓN DE LA GPU
   • Apaga y desconecta la PC de la corriente.
   • Extrae la GPU del slot PCIe x16.
   • Limpia los contactos dorados con alcohol isopropílico al 99% y algodón.
   • Reinserta la GPU firmemente hasta escuchar el clic del seguro PCIe.
   • Reconecta los cables de alimentación PCIe.

3. CONECTORES DE ALIMENTACIÓN PCIe
   • GTX/RTX 3060-3070: 1x 8-pin (6+2)
   • RTX 3080/3090: 2x 8-pin (6+2) o 3x 8-pin
   • RTX 4080/4090: conector 16-pin 12VHPWR (adaptador 4x8-pin incluido)
   • NO doblar el cable 12VHPWR a menos de 35mm del conector — riesgo de incendio.

4. DRIVERS DE VIDEO
   • Desinstala drivers con DDU (Display Driver Uninstaller) en modo seguro.
   • Instala desde: NVIDIA.com o AMD.com — NO desde Windows Update.
   • NVIDIA: GeForce Experience o driver manual DCH/Standard.
   • AMD: Adrenalin Edition con Radeon Software.

5. DIAGNÓSTICO DE GPU DEFECTUOSA
   • Prueba la GPU en otro PC para aislar si la falla es de la GPU o la placa.
   • Herramientas: GPU-Z (información), MSI Kombustor (stress test), FurMark (quema GPU).
   • Artefactos en stress test = VRAM o GPU dañada.',
 '{"components": ["GPU", "Monitor", "Cable HDMI/DisplayPort", "Slot PCIe x16"], "brands": ["NVIDIA", "AMD", "ASUS ROG/TUF", "MSI Gaming", "Gigabyte AORUS", "LG", "Samsung", "ASUS Monitor", "Acer Predator"], "tools_required": ["Alcohol isopropílico 99%", "DDU", "GPU-Z", "MSI Kombustor"], "severity": "alta", "estimated_time": "60-120 min"}'
),

('Video',
 'ARTEFACTOS VISUALES, DISTORSIÓN Y DRIVER CRASH:

1. ARTEFACTOS EN PANTALLA (triángulos, colores, líneas)
   • Causa más común: VRAM dañada, GPU sobrecalentada, o driver corrupto.
   • Monitorea temperatura GPU con MSI Afterburner — no debe superar 83°C (NVIDIA) o 90°C (AMD).
   • Aplica pasta térmica nueva en la GPU si tiene más de 3 años (Thermal Grizzly o Kryonaut).

2. PANTALLA AZUL (BSOD) RELACIONADO CON GPU
   • Errores comunes: VIDEO_TDR_FAILURE, THREAD_STUCK_IN_DEVICE_DRIVER.
   • Solución: reinstala driver con DDU en modo seguro. Usa versión anterior de driver si el problema persiste.
   • Verifica con WhoCrashed o WinDbg para identificar el driver causante.

3. PANTALLA CON FLICKERING (parpadeo)
   • Verifica frecuencia de actualización en Windows: Configuración → Pantalla → Frecuencia.
   • Activa G-Sync (NVIDIA) o FreeSync/AMD Fluid Motion (AMD) solo si el monitor lo soporta.
   • Prueba con otro cable — cables de baja calidad causan parpadeo a frecuencias altas.

4. RESOLUCIÓN INCORRECTA O NO DETECTADA
   • Drivers correctos deben detectar la resolución nativa del monitor automáticamente.
   • En NVIDIA: Panel de control → Cambiar resolución → selecciona la resolución nativa.
   • En AMD: Radeon Software → Pantalla → Configuración personalizada.',
 '{"components": ["GPU", "VRAM", "Drivers", "Monitor"], "tools_required": ["MSI Afterburner", "DDU", "WhoCrashed", "GPU-Z"], "severity": "media", "estimated_time": "45-90 min"}'
),

-- ────────────────────────────────────────────────────────────
-- BIOS
-- ────────────────────────────────────────────────────────────
('BIOS',
 'DIAGNÓSTICO POST (Power-On Self-Test) Y BIOS:

1. DECODIFICAR BEEP CODES (pitidos)
   • 1 pitido corto: POST exitoso (en algunas placas).
   • 1 pitido largo + 2 cortos: falla de video (GPU no detectada).
   • 1 pitido largo + 3 cortos: falla de video (Award BIOS).
   • Pitidos continuos: problema de RAM.
   • Sin pitido + sin imagen: puede ser CPU, RAM o placa muerta.
   • Consulta el manual de tu placa (ASUS, MSI, Gigabyte) para el código exacto.

2. DEBUG LED / Q-CODE EN PLACA MADRE
   • ASUS: LEDs Q (CPU, DRAM, VGA, BOOT) — LED rojo indica componente con falla.
   • MSI: LED EZ Debug (CPU, DRAM, VGA, BOOT).
   • Gigabyte: Q-Flash Plus LED o Debug LED.
   • Código A0/A2 ASUS = problema de inicialización de CPU o PCI.

3. DIAGNÓSTICO DE RAM
   • Retira todos los módulos. Instala solo 1 módulo en el slot A2 (primero desde la CPU).
   • Prueba cada módulo por separado para identificar el defectuoso.
   • Limpia los contactos dorados con goma de borrar (toque suave) y aire comprimido.
   • Verifica compatibilidad en QVL (Qualified Vendor List) de la motherboard.

4. RESETEAR BIOS
   • Método 1: Botón Clear CMOS en la placa madre (mientras está DESCONECTADA).
   • Método 2: Quita la pila CR2032 por 10 minutos con PC desconectada.
   • Método 3: Jumper CMOS — consulta ubicación en el manual (generalmente cerca de la pila).
   • Después del reset, reconfigura XMP/DOCP en BIOS para velocidad correcta de RAM.',
 '{"components": ["RAM", "CPU", "BIOS", "Motherboard", "Pila CR2032"], "brands": ["ASUS ROG/TUF/Prime", "MSI MAG/MEG", "Gigabyte AORUS/Gaming", "ASRock Steel Legend/Taichi"], "tools_required": ["Manual de motherboard", "Goma de borrar", "Aire comprimido"], "severity": "alta", "estimated_time": "45-90 min"}'
),

('BIOS',
 'ACTUALIZACIÓN DE BIOS Y COMPATIBILIDAD DE COMPONENTES:

1. CUÁNDO ACTUALIZAR EL BIOS
   • CPU nueva generación no detectada (Ryzen 5000/7000 en placa X570/B550/X670).
   • RAM XMP/DOCP no estable o no detectada a velocidad completa.
   • Mejoras de estabilidad publicadas por el fabricante.
   • AGESA nuevo (AMD) o microcode nuevo (Intel) disponible.

2. PROCESO SEGURO DE ACTUALIZACIÓN
   • ASUS: EZ Flash 3 (desde BIOS) o Q-Flash Plus (sin CPU, con USB en puerto específico).
   • MSI: M-Flash (desde BIOS) — descarga el archivo .ROM del sitio MSI.
   • Gigabyte: Q-Flash (F8 en arranque) o @BIOS desde Windows.
   • ASRock: Instant Flash (F6 en arranque).
   • USA UPS durante la actualización — un corte de luz puede brickear la placa.

3. CONFIGURACIÓN XMP/DOCP PARA RAM
   • DDR4: activa XMP 2.0 o DOCP en BIOS para velocidad especificada.
   • DDR5: activa XMP 3.0 o EXPO (AMD) — velocidades 6000-7200MHz.
   • Si no arranca con XMP, baja la velocidad en escalones de 200MHz.
   • Incompatibilidades comunes: G.Skill + AMD, Corsair DDR5 + Intel Z690.

4. COMPATIBILIDAD CPU-MOTHERBOARD
   • AMD AM4: Ryzen 5000 requiere BIOS con AGESA Combo V2 en placas 400/500 series.
   • AMD AM5: Ryzen 7000 con X670/B650 — verifica AGESA mínimo requerido.
   • Intel LGA1700: i9-13a/14a gen puede requerir actualización de microcode.',
 '{"components": ["BIOS", "CPU", "RAM DDR4/DDR5", "Motherboard"], "brands": ["ASUS", "MSI", "Gigabyte", "ASRock", "Intel", "AMD"], "tools_required": ["USB FAT32 para actualización", "UPS"], "severity": "media", "estimated_time": "30-60 min"}'
),

-- ────────────────────────────────────────────────────────────
-- ALMACENAMIENTO
-- ────────────────────────────────────────────────────────────
('Almacenamiento',
 'DIAGNÓSTICO DE DISCO DURO (HDD) Y SSD SATA:

1. VERIFICACIÓN DE CONEXIÓN
   • Comprueba que el cable SATA esté firmemente conectado en ambos extremos (disco y placa).
   • Prueba con otro cable SATA — son la causa más frecuente de fallos de detección.
   • Verifica en BIOS que el puerto SATA esté habilitado y en modo AHCI (no IDE ni RAID).

2. DIAGNÓSTICO S.M.A.R.T. CON CRYSTALDISKINFO
   • Instala CrystalDiskInfo (gratuito) para ver estado del disco.
   • Estado "Bueno" (azul) = sin problemas actuales.
   • Estado "Precaución" (amarillo) = sectores defectuosos — respalda INMEDIATAMENTE.
   • Estado "Malo" (rojo) = falla inminente — reemplaza el disco ya.
   • Indicadores críticos: Reallocated Sectors Count, Pending Sectors, Uncorrectable Errors.

3. REPARAR SISTEMA DE ARCHIVOS
   • Windows: abre CMD como Administrador → chkdsk C: /f /r /x (tarda horas en discos grandes).
   • Linux: fsck -y /dev/sda1 (con disco desmontado).
   • Si chkdsk no puede completarse, el disco tiene daño físico grave.

4. RECUPERACIÓN DE DATOS
   • Software gratuito: Recuva, PhotoRec, TestDisk.
   • Si el disco hace click, NO lo enciendas más — lleva a recuperación profesional.
   • Para SSD con datos críticos: MiniTool Partition Wizard o R-Studio.

5. MARCAS Y VIDA ÚTIL ESPERADA
   • Seagate Barracuda/Exos: HDD confiable, monitorear S.M.A.R.T. periódicamente.
   • WD Blue/Black/Red: excelente reputación — Red Plus para NAS.
   • Toshiba P300/X300: buena relación precio-capacidad.
   • Samsung 870 EVO/QVO: SSD SATA líderes en durabilidad (TBW alto).',
 '{"components": ["HDD", "SSD SATA", "Cable SATA", "Puerto SATA"], "brands": ["Seagate", "WD Western Digital", "Toshiba", "Samsung", "Kingston", "Crucial"], "tools_required": ["CrystalDiskInfo", "Recuva", "chkdsk", "TestDisk"], "severity": "alta", "estimated_time": "60-180 min"}'
),

('Almacenamiento',
 'DIAGNÓSTICO DE SSD NVME M.2 Y PROBLEMAS DE ARRANQUE:

1. SSD NVME NO DETECTADO
   • Verifica que el slot M.2 soporte el tipo correcto: M.2 PCIe NVMe (no SATA M.2).
   • Algunos slots M.2 comparten ancho de banda con puertos SATA — revisa el manual.
   • Instala el SSD en ángulo (~30°), empuja hasta el tope y fija con tornillo.
   • Temperatura alta puede causar throttling: usa disipador M.2 si tu placa no lo incluye.

2. VELOCIDAD BAJA EN NVME
   • Samsung 990 Pro: conecta en slot M.2 PCIe Gen 4 (Z690, X570, B650 o superior).
   • WD Black SN850X, Seagate FireCuda 530: requieren PCIe Gen 4 para velocidades máximas.
   • Verifica en Crystal DiskMark que la velocidad de lectura sea >5000 MB/s (Gen 4).
   • Si está en PCIe Gen 3, la velocidad máxima es ~3500 MB/s — normal para ese slot.

3. REPARAR ARRANQUE DE WINDOWS
   • Si Windows no inicia (disco detectado en BIOS pero no bootea):
     a. Crea USB de instalación de Windows con Media Creation Tool.
     b. Arranca desde USB → Reparar equipo → Solucionar problemas → Reparación de inicio.
     c. O en CMD: bootrec /fixmbr, bootrec /fixboot, bootrec /scanos, bootrec /rebuildbcd.

4. CLONAR DISCO ANTIGUO A NUEVO
   • Usa Macrium Reflect Free para clonar HDD a SSD sin reinstalar Windows.
   • Proceso: conecta el SSD nuevo → Macrium → Clonar → selecciona origen y destino.
   • Después de clonar, cambia el orden de arranque en BIOS para arrancar desde el SSD.

5. GESTIÓN DE ESPACIO SSD
   • Mantén al menos 10-15% libre en un SSD para rendimiento óptimo.
   • Verifica que TRIM esté habilitado: CMD → fsutil behavior query DisableDeleteNotify (0 = activo).',
 '{"components": ["SSD NVMe", "Slot M.2 PCIe Gen4", "Bootloader Windows", "Partición GPT"], "brands": ["Samsung 980 Pro/990 Pro", "WD Black SN850X", "Seagate FireCuda 530", "Crucial P3 Plus", "Kingston Fury Renegade"], "tools_required": ["CrystalDiskMark", "Macrium Reflect", "USB Windows", "bootrec"], "severity": "alta", "estimated_time": "60-240 min"}'
),

-- ────────────────────────────────────────────────────────────
-- TEMPERATURA
-- ────────────────────────────────────────────────────────────
('Temperatura',
 'DIAGNÓSTICO DE TEMPERATURA DE CPU Y SISTEMA DE ENFRIAMIENTO:

1. TEMPERATURAS DE REFERENCIA (en carga máxima)
   • Intel Core i9-13900K / i9-14900K: máximo recomendado 80-90°C (diseñado para 100°C)
   • Intel Core i7-12700K / i7-13700K: máximo 85°C
   • AMD Ryzen 9 7950X / 7900X: máximo 90-95°C (Tctl max 95°C)
   • AMD Ryzen 7 5800X3D: máximo 90°C (especialmente sensible al calor)
   • AMD Ryzen 5 5600: máximo 85°C con cooler stock

2. REAPLICAR PASTA TÉRMICA
   • Limpia la pasta vieja con alcohol isopropílico al 99% y hisopo.
   • Aplica una gota del tamaño de un guisante en el centro del IHS del CPU.
   • Pastas recomendadas: Thermal Grizzly Kryonaut, Noctua NT-H1, Arctic MX-6.
   • Kryonaut = mejor rendimiento. NT-H1 = facilidad de aplicación. MX-6 = sin metal líquido.
   • NO uses las pastas incluidas con coolers económicos.

3. COOLERS RECOMENDADOS POR TDP
   • Hasta 65W: Cooler Master Hyper 212 EVO, be quiet! Pure Rock 2
   • Hasta 125W: Noctua NH-U12S, DeepCool AK620, be quiet! Dark Rock 4
   • Hasta 200W: Noctua NH-D15, DeepCool ASSASSIN IV
   • +200W (i9/Ryzen 9): AIO 360mm — Corsair H150i, NZXT Kraken X73, DeepCool LS720

4. VERIFICAR MONTAJE DEL COOLER
   • Presión uniforme en las 4 esquinas del socket.
   • Intel LGA1700: usa bracket actualizado de Noctua para presión correcta.
   • AMD AM5: backplate de plástico stock — algunos coolers requieren su propio backplate.
   • AIO: coloca el radiador en posición donde las mangueras queden en la parte baja.

5. FLUJO DE AIRE DEL GABINETE
   • Configuración ideal: 2-3 ventiladores frontales (entrada) + 1 trasero + 1-2 superiores (salida).
   • Positiva vs negativa: presión positiva (más entrada) reduce polvo.
   • Limpia filtros de polvo cada 3-6 meses.',
 '{"components": ["CPU", "Cooler", "Pasta térmica", "Gabinete", "Ventiladores"], "brands": ["Noctua", "be quiet!", "Cooler Master", "Corsair", "NZXT", "DeepCool", "ARCTIC"], "tools_required": ["HWiNFO64", "Core Temp", "Thermal Grizzly Kryonaut", "Alcohol isopropílico 99%"], "severity": "alta", "estimated_time": "30-90 min"}'
),

('Temperatura',
 'TEMPERATURA DE GPU Y THROTTLING TÉRMICO:

1. TEMPERATURAS DE REFERENCIA GPU
   • NVIDIA RTX 40 series: límite térmico 83°C (configurable con Afterburner hasta 87°C)
   • NVIDIA RTX 30 series: límite térmico 83-84°C
   • AMD Radeon RX 7000: junction temp hasta 110°C (normal), die temp hasta 95°C
   • AMD Radeon RX 6000: límite 110°C junction (reportado por HWiNFO)
   • Hotspot/Junction temp siempre es más alta que la temperatura del die — es normal.

2. GPU THROTTLING
   • Si la GPU baja de frecuencia sola (throttling), la causa es térmica o de potencia.
   • MSI Afterburner: abre la curva de ventiladores y aumenta el perfil al 100% a 70°C.
   • Limpia los ventiladores y el disipador de la GPU con aire comprimido.
   • Si el throttling persiste: repasta la GPU (pasta Thermal Grizzly o almohadillas).

3. REAPLICAR PASTA A GPU
   • Aplica solo si la GPU está fuera de garantía.
   • Componentes: pasta para el die de GPU, almohadillas térmicas para VRAM y VRM.
   • RTX 3080/3090: almohadillas de 1.0mm para VRAM, 1.5mm para VRM.
   • RX 6800 XT: almohadillas de 1.5-2.0mm para memoria GDDR6.

4. CURVA DE VENTILADORES PERSONALIZADA
   • MSI Afterburner: ajusta la curva para que ventiladores suban antes del límite térmico.
   • Temperatura objetivo: mantener GPU por debajo de 80°C con ventiladores al 70-80%.

5. DISIPADOR AFTERMARKET PARA GPU
   • Arctic Accelero III: disipador universal para GPUs de hasta 300W.
   • Reemplaza el disipador original por uno más eficiente si el cooler de fábrica es insuficiente.',
 '{"components": ["GPU", "VRAM", "VRM", "Ventiladores GPU", "Disipador GPU"], "brands": ["NVIDIA RTX", "AMD Radeon", "ASUS ROG/TUF", "MSI Gaming", "Gigabyte AORUS"], "tools_required": ["MSI Afterburner", "HWiNFO64", "Thermal Grizzly", "Almohadillas térmicas"], "severity": "media", "estimated_time": "60-180 min"}'
),

-- ────────────────────────────────────────────────────────────
-- RED
-- ────────────────────────────────────────────────────────────
('Red',
 'DIAGNÓSTICO DE CONEXIÓN DE RED Y TARJETA DE RED:

1. DIAGNÓSTICO BÁSICO (Windows)
   • Abre CMD como Administrador y ejecuta:
     - ipconfig /all   → verifica que tienes IP válida (no 169.x.x.x = APIPA = sin DHCP)
     - ping 8.8.8.8    → si responde, internet funciona (problema puede ser DNS)
     - ping google.com → si falla pero 8.8.8.8 responde = problema de DNS
     - tracert 8.8.8.8 → identifica en qué salto se pierde la conexión

2. RESET DE PILA DE RED
   • Ejecuta como Administrador (reinicia después):
     - netsh winsock reset
     - netsh int ip reset
     - ipconfig /flushdns
     - ipconfig /release  →  ipconfig /renew

3. DRIVER DE RED DESACTUALIZADO O CORRUPTO
   • Intel i219-V / i225-V: descarga driver desde el sitio de la motherboard (ASUS, MSI, Gigabyte).
   • Realtek RTL8125B 2.5GbE: descarga desde Realtek.com o sitio de la motherboard.
   • NO uses el driver de Windows Update — usa el del fabricante.
   • Desinstala el adaptador en Administrador de dispositivos y reinstala el driver.

4. TARJETA DE RED NO DETECTADA
   • Verifica en BIOS que el LAN onboard esté habilitado (busca "Onboard LAN" o "Ethernet").
   • Prueba el slot PCIe con otra tarjeta si la tarjeta de red es PCIe (Intel I225-V).
   • Conecta el cable Ethernet — algunos adaptadores no aparecen sin cable conectado.

5. PROBLEMA INTERMITENTE / DESCONEXIONES
   • Administrador de dispositivos → Adaptador de red → Propiedades → Administración de energía.
   • Desmarca "Permitir que el equipo apague este dispositivo para ahorrar energía".
   • En opciones avanzadas: desactiva "Wake on LAN" y "Green Ethernet" si causan problemas.',
 '{"components": ["Tarjeta de red", "Driver LAN", "Cable Ethernet", "Router/Switch"], "brands": ["Intel i219/i225", "Realtek RTL8125", "Killer E3100", "ASUS PCE-AX", "TP-Link"], "tools_required": ["CMD ipconfig", "netsh", "ping", "tracert"], "severity": "media", "estimated_time": "30-60 min"}'
),

('Red',
 'DIAGNÓSTICO DE WIFI Y ADAPTADORES INALÁMBRICOS:

1. DIAGNÓSTICO WiFi
   • Verifica que las antenas del adaptador PCIe estén conectadas y verticales.
   • Prueba conectarte a red de 2.4GHz y 5GHz por separado.
   • Intel AX200/AX210 WiFi 6/6E: para redes 6GHz necesitas router WiFi 6E y Windows 11.
   • Si el adaptador no aparece: instala driver desde sitio de Intel o fabricante de placa.

2. ADAPTADORES WIFI PCIe RECOMENDADOS
   • Intel WiFi 6 AX200: excelente para Intel y AMD AM4 — Bluetooth 5.2 incluido.
   • Intel WiFi 6E AX210: agrega banda 6GHz — recomendado para routers WiFi 6E.
   • ASUS PCE-AX58BT: WiFi 6 PCIe con antenas externas — buena cobertura.
   • Fenvi FV-T919: Broadcom BCM94360 — compatible nativo con macOS si tienes Hackintosh.

3. PROBLEMAS COMUNES WIFI EN WINDOWS 11
   • Actualizaciones KB5012170 / KB5025305 pueden corromper drivers WiFi.
   • Solución: Administrador de dispositivos → desinstalar adaptador → reiniciar → reinstalar driver.
   • Si el problema persiste: ejecuta "sfc /scannow" y "DISM /Online /Cleanup-Image /RestoreHealth".

4. VELOCIDAD WIFI BAJA
   • Verifica que conectas a 5GHz y no a 2.4GHz (5GHz = más velocidad, menos alcance).
   • Cambia el canal WiFi en el router: canales 36, 40, 44, 48 son los menos congestionados en 5GHz.
   • Mantén el router a menos de 10 metros sin obstáculos para WiFi 5/6.
   • Considera powerline o MoCA si necesitas velocidad garantizada.',
 '{"components": ["Adaptador WiFi", "Antenas", "Driver Intel/Realtek", "Router"], "brands": ["Intel AX200/AX210", "ASUS PCE-AX58BT", "TP-Link Archer", "Fenvi", "Realtek"], "tools_required": ["Administrador de dispositivos", "sfc /scannow", "DISM"], "severity": "baja", "estimated_time": "20-45 min"}'
);
