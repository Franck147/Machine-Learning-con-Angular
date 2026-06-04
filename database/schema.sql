-- ============================================================
-- Asistente Inteligente de Soporte Técnico — Schema SQL
-- Base de datos: Supabase (PostgreSQL)
-- v3: marcas, series, soluciones específicas por marca/modelo
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ------------------------------------------------------------
-- Tabla: brands
-- Catálogo de marcas de PC/laptops soportadas.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS brands (
    name            VARCHAR(50)  PRIMARY KEY,
    display_name    VARCHAR(100) NOT NULL,
    support_tool    VARCHAR(150),          -- herramienta oficial de soporte
    diagnostic_tool VARCHAR(150),          -- herramienta de diagnóstico de hardware
    support_url     VARCHAR(255),
    created_at      TIMESTAMPTZ  DEFAULT NOW()
);

-- ------------------------------------------------------------
-- Tabla: model_series
-- Series de productos por marca.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS model_series (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_name  VARCHAR(50) NOT NULL REFERENCES brands(name),
    series      VARCHAR(100) NOT NULL,
    type        VARCHAR(30)  DEFAULT 'laptop',  -- laptop, desktop, gaming, workstation
    description VARCHAR(255),
    created_at  TIMESTAMPTZ  DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_model_series_brand ON model_series (brand_name);

-- ------------------------------------------------------------
-- Tabla: catalog_solutions
-- brand/series NULL = solución genérica para todos.
-- Lookup: brand+series+category > brand+category > category
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS catalog_solutions (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    category        VARCHAR(50) NOT NULL,
    brand           VARCHAR(50) DEFAULT NULL REFERENCES brands(name),
    series          VARCHAR(100) DEFAULT NULL,
    solution_text   TEXT        NOT NULL,
    hardware_specs  JSONB       DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_catalog_solutions_category  ON catalog_solutions (category);
CREATE INDEX IF NOT EXISTS idx_catalog_solutions_brand     ON catalog_solutions (brand);
CREATE INDEX IF NOT EXISTS idx_catalog_solutions_brand_cat ON catalog_solutions (brand, category);

-- ------------------------------------------------------------
-- Tabla: diagnosis_logs
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS diagnosis_logs (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_query          TEXT        NOT NULL,
    predicted_category  VARCHAR(50) NOT NULL,
    accuracy            NUMERIC(5,4),
    solution_provided   TEXT,
    brand               VARCHAR(50) DEFAULT NULL,
    series              VARCHAR(100) DEFAULT NULL,
    feedback_util                  BOOLEAN      DEFAULT NULL,
    feedback_comment               TEXT         DEFAULT NULL,
    feedback_category_correction   VARCHAR(50)  DEFAULT NULL,
    created_at                     TIMESTAMPTZ  DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_diagnosis_logs_created_at  ON diagnosis_logs (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_diagnosis_logs_category    ON diagnosis_logs (predicted_category);
CREATE INDEX IF NOT EXISTS idx_diagnosis_logs_feedback    ON diagnosis_logs (feedback_util) WHERE feedback_util IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_diagnosis_logs_brand       ON diagnosis_logs (brand);
CREATE INDEX IF NOT EXISTS idx_diagnosis_logs_correction  ON diagnosis_logs (feedback_category_correction) WHERE feedback_category_correction IS NOT NULL;

-- ============================================================
-- DATOS: Marcas
-- ============================================================

INSERT INTO brands (name, display_name, support_tool, diagnostic_tool, support_url) VALUES
('Dell',     'Dell',     'Dell Command Update',    'Dell Pre-Boot Diagnostics (F12)',          'https://www.dell.com/support'),
('HP',       'HP',       'HP Support Assistant',   'HP PC Hardware Diagnostics UEFI (F2)',     'https://support.hp.com'),
('Lenovo',   'Lenovo',   'Lenovo Vantage',         'Lenovo Diagnostics (F10/Fn+F10)',          'https://support.lenovo.com'),
('ASUS',     'ASUS',     'MyASUS / Armoury Crate', 'ASUS PC Diagnostics / BIOS EZ Mode',      'https://www.asus.com/support'),
('Acer',     'Acer',     'Acer Care Center',       'eRecovery / Acer Quick Access',            'https://www.acer.com/support'),
('MSI',      'MSI',      'MSI Center',             'MSI Diagnostics / Dragon Center',          'https://www.msi.com/support'),
('Generica', 'PC Genérico / Otro', NULL,           NULL,                                       NULL)
ON CONFLICT (name) DO NOTHING;

-- ============================================================
-- DATOS: Series por marca
-- ============================================================

INSERT INTO model_series (brand_name, series, type, description) VALUES
-- Dell
('Dell', 'XPS',       'laptop',      'Laptops premium ultradelgadas, pantallas OLED/4K'),
('Dell', 'Inspiron',  'laptop',      'Laptops de uso general, gama media'),
('Dell', 'Latitude',  'laptop',      'Laptops empresariales, durabilidad certificada'),
('Dell', 'Alienware', 'gaming',      'Gaming de alto rendimiento, refrigeración avanzada'),
('Dell', 'OptiPlex',  'desktop',     'PCs de escritorio corporativas'),
('Dell', 'Precision', 'workstation', 'Estaciones de trabajo para diseño/ingeniería'),
('Dell', 'Vostro',    'laptop',      'Laptops para pequeña empresa'),
-- HP
('HP', 'Pavilion',  'laptop',      'Laptops de gama media, uso doméstico'),
('HP', 'Spectre',   'laptop',      'Laptops premium ultradelgadas'),
('HP', 'EliteBook', 'laptop',      'Laptops empresariales premium'),
('HP', 'ProBook',   'laptop',      'Laptops empresariales gama media'),
('HP', 'Omen',      'gaming',      'Gaming de alto rendimiento'),
('HP', 'Envy',      'laptop',      'Laptops multimedia premium'),
('HP', 'ZBook',     'workstation', 'Estaciones de trabajo móviles'),
-- Lenovo
('Lenovo', 'ThinkPad',    'laptop',   'Laptops empresariales icónicas, teclado excepcional'),
('Lenovo', 'IdeaPad',     'laptop',   'Laptops de uso general, gama media'),
('Lenovo', 'Legion',      'gaming',   'Gaming de alto rendimiento'),
('Lenovo', 'Yoga',        'laptop',   'Laptops convertibles 2-en-1'),
('Lenovo', 'ThinkCentre', 'desktop',  'PCs de escritorio corporativas'),
('Lenovo', 'IdeaCentre',  'desktop',  'PCs de escritorio domésticas'),
-- ASUS
('ASUS', 'VivoBook',   'laptop',      'Laptops de uso general, livianas'),
('ASUS', 'ZenBook',    'laptop',      'Laptops ultradelgadas premium'),
('ASUS', 'ROG',        'gaming',      'Republic of Gamers, alto rendimiento'),
('ASUS', 'TUF',        'gaming',      'Gaming resistente y duradero'),
('ASUS', 'ExpertBook', 'laptop',      'Laptops empresariales ultralivianas'),
('ASUS', 'ProArt',     'workstation', 'Estaciones de trabajo para creadores'),
-- Acer
('Acer', 'Aspire',     'laptop',  'Laptops de uso general, gama media'),
('Acer', 'Swift',      'laptop',  'Laptops ultradelgadas y ligeras'),
('Acer', 'Nitro',      'gaming',  'Gaming de entrada/gama media'),
('Acer', 'Predator',   'gaming',  'Gaming de alto rendimiento'),
('Acer', 'TravelMate', 'laptop',  'Laptops empresariales robustas'),
-- MSI
('MSI', 'GF Series',  'gaming',      'Gaming gama media, buena relación calidad-precio'),
('MSI', 'GE Series',  'gaming',      'Gaming de alto rendimiento, pantalla alta tasa de refresco'),
('MSI', 'Stealth',    'gaming',      'Gaming ultradelgado y silencioso'),
('MSI', 'Creator',    'workstation', 'Laptops para creadores de contenido'),
('MSI', 'Prestige',   'laptop',      'Laptops de negocios premium'),
-- Genérica
('Generica', 'PC Escritorio', 'desktop', 'PC armada o marca blanca'),
('Generica', 'Laptop',        'laptop',  'Laptop sin marca específica'),
('Generica', 'Gaming PC',     'gaming',  'PC gaming armada o clonada');

-- ============================================================
-- DATOS: Soluciones genéricas (sin marca)
-- ============================================================

INSERT INTO catalog_solutions (category, brand, series, solution_text, hardware_specs) VALUES

('Energia', NULL, NULL,
 'Verifica que el cable de alimentación esté correctamente conectado. Comprueba el fusible de la fuente de poder (PSU) y usa un multímetro para medir los voltajes (+12V, +5V, +3.3V). Si la PSU no responde, prueba con otra unidad. Asegúrate de que el conector ATX de 24 pines y el EPS de 8 pines estén correctamente insertados en la placa.',
 '{"components": ["PSU", "Motherboard", "Cable ATX"], "tools_required": ["Multímetro"], "severity": "alta"}'
),
('Energia', NULL, NULL,
 'Si el equipo enciende pero se apaga inmediatamente: limpia los ventiladores y disipadores de polvo. Aplica pasta térmica nueva al procesador. Verifica que los ventiladores del CPU y chasis estén funcionando. El sobrecalentamiento provoca shutdown de protección automática.',
 '{"components": ["CPU", "Disipador", "Pasta térmica"], "tools_required": ["Pasta térmica", "Aire comprimido"], "severity": "media"}'
),
-- Video genérico
('Video', NULL, NULL,
 'Si no hay señal de video: conecta el monitor al puerto correcto (GPU dedicada, no tarjeta integrada). Reinserta la GPU en el slot PCIe, limpiando los contactos con alcohol isopropílico. Comprueba los conectores de alimentación PCIe de la GPU (6-pin u 8-pin). Prueba con otro monitor o cable.',
 '{"components": ["GPU", "Monitor", "Cable HDMI/DisplayPort"], "severity": "alta"}'
),
('Video', NULL, NULL,
 'Para artefactos visuales o distorsión: actualiza o reinstala los drivers de la GPU. Si persiste, puede indicar VRAM dañada o GPU sobrecalentada. Usa GPU-Z para monitorear temperatura y MSI Kombustor para stress test. Verifica la frecuencia del ventilador de la GPU.',
 '{"components": ["GPU", "Drivers", "VRAM"], "tools_required": ["GPU-Z", "MSI Kombustor"], "severity": "media"}'
),
-- BIOS genérico
('BIOS', NULL, NULL,
 'Si el sistema no supera el POST: verifica que la RAM esté en los slots correctos (generalmente A2/B2 para dual channel). Limpia los slots de RAM con aire comprimido. Prueba con un solo módulo a la vez para identificar módulos defectuosos.',
 '{"components": ["RAM", "BIOS", "Motherboard"], "severity": "alta"}'
),
('BIOS', NULL, NULL,
 'Para restablecer la BIOS: usa el jumper CMOS (consulta el manual) cortocircuitándolo 10 segundos con el equipo desconectado, o retira la pila CR2032 por 5 minutos. Esto restablece la configuración de fábrica.',
 '{"components": ["BIOS", "CMOS", "Pila CR2032"], "severity": "baja"}'
),
-- Almacenamiento genérico
('Almacenamiento', NULL, NULL,
 'Si el disco no es detectado: verifica los cables SATA y la alimentación. En la BIOS, confirma que el puerto SATA esté en modo AHCI. Usa CrystalDiskInfo para verificar el estado S.M.A.R.T. Un valor alto de reallocated sectors indica fallas inminentes.',
 '{"components": ["HDD/SSD", "Cable SATA", "S.M.A.R.T."], "tools_required": ["CrystalDiskInfo"], "severity": "alta"}'
),
('Almacenamiento', NULL, NULL,
 'Para errores del sistema de archivos o lentitud extrema: ejecuta chkdsk /f /r en Windows o fsck en Linux. Si el SSD muestra bajo rendimiento, verifica que esté en un puerto SATA III (6Gbps) o M.2 PCIe correcto.',
 '{"components": ["HDD/SSD", "Sistema de archivos", "SATA III"], "tools_required": ["chkdsk", "CrystalDiskInfo"], "severity": "media"}'
),
-- Red genérica
('Red', NULL, NULL,
 'Si el adaptador de red no funciona: abre el Administrador de dispositivos y busca la tarjeta de red. Descarga los drivers desde el sitio oficial del fabricante. Ejecuta "ipconfig /release" y "ipconfig /renew" en CMD. Verifica que el cable ethernet esté firmemente conectado.',
 '{"components": ["NIC", "Drivers de red"], "severity": "media"}'
),
('Red', NULL, NULL,
 'Para WiFi inestable: actualiza los drivers del adaptador inalámbrico. Ejecuta "netsh winsock reset" y reinicia. Verifica que el adaptador no esté en modo avión. Si persiste, desinstala el adaptador desde Administrador de dispositivos y reinicia para auto-reinstalar.',
 '{"components": ["Adaptador WiFi", "Drivers inalámbricos"], "severity": "media"}'
),
-- Audio genérico
('Audio', NULL, NULL,
 'Si no hay sonido: verifica en Administrador de dispositivos que el dispositivo de audio esté activo. Haz clic derecho en el ícono de audio → Dispositivos de reproducción y confirma el dispositivo predeterminado. Reinstala los drivers de audio (Realtek HD Audio u otro fabricante).',
 '{"components": ["Tarjeta de sonido", "Drivers de audio"], "severity": "media"}'
),
('Audio', NULL, NULL,
 'Para audio distorsionado: verifica que el conector esté en el jack correcto (verde = salida, rosa = micrófono). Deshabilita mejoras de audio en las propiedades del dispositivo. Si usas audio HDMI, selecciónalo como dispositivo predeterminado.',
 '{"components": ["Jack de audio 3.5mm", "HDMI audio"], "severity": "baja"}'
),
-- Temperatura genérica
('Temperatura', NULL, NULL,
 'Si el equipo se sobrecalienta: limpia ventiladores y disipadores con aire comprimido cada 6 meses. Reaplica pasta térmica en el procesador. Verifica que el disipador esté correctamente montado. Usa HWMonitor para ver temperaturas en tiempo real.',
 '{"components": ["CPU cooler", "Pasta térmica", "Ventiladores"], "tools_required": ["HWMonitor", "Pasta térmica"], "severity": "alta"}'
),
('Temperatura', NULL, NULL,
 'Para mejorar el flujo de aire: organiza los cables internos para no obstruir el paso de aire. Agrega ventiladores de chasis (entrada por frente, salida por atrás/arriba). Monitorea con HWiNFO en tiempo real para identificar el componente más caliente.',
 '{"components": ["Gabinete", "Ventiladores de chasis"], "tools_required": ["HWiNFO"], "severity": "media"}'
),
-- USB genérico
('USB', NULL, NULL,
 'Si un puerto USB no reconoce dispositivos: prueba el dispositivo en otro puerto. Abre Administrador de dispositivos → Controladores de bus serie universal, desinstala todos y reinicia para auto-reinstalar. Verifica que los conectores del panel frontal estén bien conectados a la placa.',
 '{"components": ["Controladores USB", "Panel frontal"], "severity": "media"}'
),
('USB', NULL, NULL,
 'Para "Power Surge on USB Port" o desconexiones aleatorias: deshabilita el apagado selectivo USB en las opciones de energía de Windows. Si el problema es en puertos traseros, puede indicar un controlador USB dañado en la placa madre.',
 '{"components": ["PSU", "Controlador USB", "Opciones de energía"], "severity": "media"}'
),
-- Drivers genérico
('Drivers', NULL, NULL,
 'Para drivers faltantes o con error: abre devmgmt.msc y busca dispositivos con triángulo amarillo. Descarga drivers directamente desde el sitio oficial del fabricante del hardware. Evita sitios de terceros. Usa la opción "Buscar actualizaciones" de Windows como alternativa.',
 '{"components": ["Drivers del sistema", "Administrador de dispositivos"], "severity": "media"}'
),
('Drivers', NULL, NULL,
 'Para BSOD causados por drivers: usa DDU (Display Driver Uninstaller) en modo seguro para limpiar completamente los drivers de GPU antes de reinstalar. Usa WhoCrashed para identificar qué driver causó el BSOD. Para revertir: Administrador de dispositivos → Propiedades → Controlador → Revertir.',
 '{"components": ["Drivers GPU", "Windows Update", "Modo seguro"], "tools_required": ["DDU", "WhoCrashed"], "severity": "alta"}'
);

-- ============================================================
-- DATOS: Soluciones específicas por marca — DELL
-- ============================================================

INSERT INTO catalog_solutions (category, brand, series, solution_text, hardware_specs) VALUES

('Temperatura', 'Dell', NULL,
 'En laptops Dell con thermal throttling: instala Dell Power Manager y configura el perfil de batería en "Rendimiento máximo". Para laptops XPS con sobrecalentamiento severo considera reemplazar la pasta térmica por pasta de metal líquido (Thermal Grizzly Conductonaut). Verifica en BIOS: Performance → Thermal Management → "Ultra Performance". Usa Dell SupportAssist para diagnóstico.',
 '{"tools_required": ["Dell Power Manager", "Dell SupportAssist", "Pasta metal líquido"], "severity": "alta", "brand_note": "Dell XPS 15/17 conocidos por throttling bajo carga sostenida"}'
),
('Temperatura', 'Dell', 'XPS',
 'El Dell XPS 15/17 tiene un perfil térmico conservador por diseño ultradelgado. Pasos específicos: 1) Instala Dell Thermal Event Viewer. 2) En Dell Power Manager activa "Optimized". 3) Undervolting con Throttlestop puede reducir 15-20°C en el CPU. 4) Reemplaza la pasta térmica original (suele ser de baja calidad) con Thermal Grizzly Kryonaut o metal líquido. 5) Limpia los vanos de ventilación por debajo con aire comprimido.',
 '{"tools_required": ["Dell Power Manager", "Throttlestop", "Thermal Grizzly"], "severity": "alta", "brand_note": "XPS 15 9500/9510/9520 afectados frecuentemente"}'
),
('Video', 'Dell', NULL,
 'Para problemas de video en laptops Dell: descarga los drivers gráficos desde dell.com/support usando tu Service Tag (etiqueta en la parte inferior del equipo). Instala Dell Display Manager para configurar monitores externos. Para laptops con pantalla OLED (XPS 9500+), actualiza el firmware del panel desde el catálogo de drivers Dell. En Alienware, usa Alienware Command Center para cambiar entre GPU integrada y dedicada.',
 '{"tools_required": ["Dell Display Manager", "Alienware Command Center"], "severity": "media", "brand_note": "Usar Service Tag en dell.com/support para drivers exactos del modelo"}'
),
('BIOS', 'Dell', NULL,
 'Para problemas de BIOS en Dell: presiona F2 al iniciar para acceder al Setup. Para diagnósticos de hardware presiona F12 → "Diagnostics" → ejecuta Dell Pre-Boot System Assessment (PSA). Para actualizar BIOS: descarga el archivo .exe desde dell.com/support con tu Service Tag y ejecútalo desde Windows. Para resetear: F2 → Maintenance → "Restore Settings" → Factory Defaults.',
 '{"tools_required": ["Dell Pre-Boot PSA", "Dell BIOS Update"], "severity": "media", "brand_note": "Service Tag en sticker inferior o en BIOS Setup → General → System Information"}'
),
('Drivers', 'Dell', NULL,
 'La herramienta oficial para gestión de drivers Dell es Dell Command Update. Instálala desde dell.com/support, detecta automáticamente todos los drivers desactualizados o faltantes del sistema. Alternativamente, ingresa tu Service Tag en dell.com/support → Drivers & Downloads para ver exactamente los drivers de tu modelo. Para reinstalación limpia de drivers GPU: usa DDU en modo seguro antes de instalar el driver Dell.',
 '{"tools_required": ["Dell Command Update", "Service Tag"], "severity": "media"}'
),
('Red', 'Dell', NULL,
 'Para WiFi en laptops Dell: verifica si tu adaptador es Intel, Realtek o Killer (Alienware). Para Intel WiFi 6/6E: descarga el driver desde dell.com/support. Para Killer WiFi (Alienware): instala "Killer Intelligence Center" desde Microsoft Store, que optimiza la red para gaming. Si el WiFi desaparece del Administrador de dispositivos, puede ser un fallo del módulo WiFi físico (requiere reemplazo del módulo M.2).',
 '{"tools_required": ["Killer Intelligence Center", "Dell Command Update"], "severity": "media", "brand_note": "Alienware usa adaptadores Killer Networking con software específico"}'
),
('Audio', 'Dell', NULL,
 'Para audio en laptops Dell: descarga los drivers de audio Realtek desde dell.com/support con tu Service Tag (no de Realtek.com directamente). En laptops Dell con Waves MaxxAudio: reinstala el software Waves desde el catálogo Dell. Si el audio desaparece después de Windows Update, usa Dell Command Update para recuperar el driver correcto. Verifica en Administrador de dispositivos que no haya conflictos.',
 '{"tools_required": ["Waves MaxxAudio", "Dell Command Update"], "severity": "baja"}'
),
('Energia', 'Dell', NULL,
 'Para problemas de carga en laptops Dell: ejecuta el diagnóstico de batería con Dell SupportAssist. Si la batería no carga: 1) Desconecta el adaptador. 2) Mantén presionado el botón de encendido 15 segundos. 3) Vuelve a conectar. Dell usa reconocimiento del adaptador por el tercer pin del conector (chip de ID): un adaptador genérico puede no ser reconocido y cargar solo al 50% o no cargar. Usa siempre adaptadores Dell originales.',
 '{"tools_required": ["Dell SupportAssist"], "severity": "media", "brand_note": "Adaptadores Dell usan chip de autenticación en el conector"}'
),
('Almacenamiento', 'Dell', NULL,
 'Para discos no detectados en Dell: ejecuta Dell Pre-Boot Diagnostics (F12 → Diagnostics → Hard Drive Test). Para SSD NVMe en XPS/Precision: verifica en BIOS → Storage que el modo sea "RAID On" si Windows fue instalado así, o "AHCI" para instalaciones limpias. Para HDD ruidosos: Dell SupportAssist puede hacer un S.M.A.R.T. check. Si el SSD desaparece tras una actualización de BIOS, revierte la BIOS desde dell.com/support.',
 '{"tools_required": ["Dell Pre-Boot Diagnostics", "Dell SupportAssist"], "severity": "alta"}'
),
('USB', 'Dell', NULL,
 'Para puertos USB/Thunderbolt en Dell: actualiza el firmware Thunderbolt desde dell.com/support (busca "Thunderbolt Firmware Update"). Para USB-C que no carga: verifica que el adaptador sea USB-C PD compatible con el voltaje correcto (45W/65W/90W según modelo). En XPS el puerto USB-C trasero es Thunderbolt 4 y el frontal puede ser solo USB 3.2. Desactiva "Thunderbolt Boot Support" en BIOS si hay conflictos de dispositivos.',
 '{"tools_required": ["Thunderbolt Firmware Update", "Dell BIOS"], "severity": "media"}'
);

-- ============================================================
-- DATOS: Soluciones específicas por marca — HP
-- ============================================================

INSERT INTO catalog_solutions (category, brand, series, solution_text, hardware_specs) VALUES

('BIOS', 'HP', NULL,
 'Para problemas de BIOS en HP: presiona F10 al iniciar para acceder al Setup BIOS. HP Sure Start es una tecnología de recuperación automática del BIOS que puede bloquear cambios no autorizados — si el sistema no arranca por Sure Start, presiona Ctrl+Alt+S en el logo HP para acceder al menú de recuperación. Para diagnósticos de hardware antes del sistema operativo: presiona Esc al inicio → F2 para HP PC Hardware Diagnostics UEFI. Para resetear BIOS: F10 → Exit → Restore Defaults.',
 '{"tools_required": ["HP PC Hardware Diagnostics UEFI", "HP Sure Start"], "severity": "alta", "brand_note": "HP Sure Start protege el BIOS contra modificaciones no autorizadas"}'
),
('Temperatura', 'HP', NULL,
 'Para sobrecalentamiento en laptops HP: instala HP Command Center (disponible en Microsoft Store) para controlar el perfil térmico. Activa el modo "Performance" solo cuando lo necesites. HP Cool Sense ajusta los ventiladores según la posición del equipo. Para HP Omen: usa Omen Command Center para configurar manualmente las curvas de ventiladores. Limpia los ventiladores con aire comprimido por las rejillas de ventilación traseras.',
 '{"tools_required": ["HP Command Center", "Omen Command Center"], "severity": "alta", "brand_note": "HP Omen tiene opciones avanzadas de gestión térmica via Omen Command Center"}'
),
('Temperatura', 'HP', 'Omen',
 'Para HP Omen con throttling: 1) Abre Omen Command Center → Performance. 2) Activa "Advanced Mode" en el control de ventiladores. 3) Sube la curva de ventiladores al máximo para cargas sostenidas. 4) Usa el modo "Performance" en el selector de perfil de energía. 5) Reemplaza la pasta térmica original por Thermal Grizzly Kryonaut. 6) Verifica que los thermal pads de la VRAM y VRM no estén degradados. Para reducción de temperatura extrema considera un cooling pad externo.',
 '{"tools_required": ["Omen Command Center", "Thermal Grizzly Kryonaut"], "severity": "alta"}'
),
('Drivers', 'HP', NULL,
 'La herramienta oficial de drivers HP es HP Support Assistant — instálala desde support.hp.com. Detecta automáticamente drivers desactualizados para tu modelo exacto. Alternativamente usa HP SoftPaq Download Manager para descarga masiva de drivers. El número de producto HP (P/N) se encuentra en la etiqueta inferior del equipo y en BIOS: permite descargar exactamente los drivers para tu configuración de hardware.',
 '{"tools_required": ["HP Support Assistant", "HP SoftPaq Download Manager"], "severity": "media"}'
),
('Video', 'HP', NULL,
 'Para problemas de video en HP: descarga los drivers gráficos desde support.hp.com usando tu número de producto (P/N). Para pantallas HP Spectre con OLED o IPS avanzada: HP Display Control ajusta la calibración. HP Omen usa Omen Command Center para gestionar el modo GPU (solo integrada, solo dedicada, híbrido). Para artefactos o flicker en Spectre/Envy, verifica si hay una actualización de firmware del panel en HP Support Assistant.',
 '{"tools_required": ["HP Display Control", "Omen Command Center", "HP Support Assistant"], "severity": "media"}'
),
('Audio', 'HP', NULL,
 'Para audio en laptops HP con Bang & Olufsen: reinstala HP Audio Control desde support.hp.com. Si el software Bang & Olufsen no detecta los altavoces, reinstala los drivers de audio (Realtek) primero y luego el software B&O. Verifica en Administrador de dispositivos → Entradas y salidas de audio que no haya conflictos. Para HP EliteBook con altavoces enterprise: descarga el driver de audio HP específico del catálogo de tu modelo.',
 '{"tools_required": ["HP Audio Control", "Bang & Olufsen Software"], "severity": "baja", "brand_note": "Laptops HP premium usan software Bang & Olufsen sobre drivers Realtek"}'
),
('Red', 'HP', NULL,
 'Para WiFi en laptops HP: verifica el modelo del adaptador en Administrador de dispositivos (Realtek, Intel, Broadcom o Qualcomm Atheros). Descarga el driver desde support.hp.com con tu número de producto. HP Network Check (parte de HP Support Assistant) diagnostica problemas de conectividad. Si el adaptador WiFi desaparece: verifica que el modo avión esté desactivado y que el interruptor físico de WiFi (si existe) esté activado.',
 '{"tools_required": ["HP Support Assistant", "HP Network Check"], "severity": "media"}'
),
('Energia', 'HP', NULL,
 'Para problemas de carga en HP: ejecuta HP Battery Check desde HP Support Assistant para determinar si la batería necesita reemplazo. Si la batería no carga al conectar el adaptador: 1) Apaga el equipo. 2) Desconecta el adaptador y retira la batería (si es removible). 3) Mantén el botón de encendido 15 segundos. 4) Reconecta y enciende solo con adaptador. HP usa adaptadores con identificación smart — adaptadores genéricos pueden cargar más lento o no cargar.',
 '{"tools_required": ["HP Battery Check", "HP Support Assistant"], "severity": "media"}'
),
('USB', 'HP', NULL,
 'Para puertos USB en HP: verifica en Administrador de dispositivos → Controladores de bus serie universal. Reinstala los drivers del controlador USB Hub desde support.hp.com. Para HP EliteBook con docking station: actualiza el firmware del dock desde HP Support Assistant. Si el USB-C/Thunderbolt no carga: el adaptador debe ser compatible con USB-C PD al voltaje correcto del modelo.',
 '{"tools_required": ["HP Support Assistant", "HP Dock Firmware"], "severity": "media"}'
),
('Almacenamiento', 'HP', NULL,
 'Para discos no detectados en HP: ejecuta HP PC Hardware Diagnostics UEFI (Esc → F2 → Component Tests → Hard Disk Test) para verificar el estado del disco sin sistema operativo. Para SSD en HP EliteBook/ProBook con cifrado HP DriveLock activo: necesitas la clave maestra para desbloquear. Si el SSD M.2 no aparece en BIOS: verifica que el slot M.2 esté habilitado en BIOS → Advanced → Disk Options.',
 '{"tools_required": ["HP PC Hardware Diagnostics UEFI"], "severity": "alta"}'
);

-- ============================================================
-- DATOS: Soluciones específicas por marca — LENOVO
-- ============================================================

INSERT INTO catalog_solutions (category, brand, series, solution_text, hardware_specs) VALUES

('Drivers', 'Lenovo', NULL,
 'La herramienta oficial de Lenovo para gestión de drivers es Lenovo Vantage (disponible en Microsoft Store). Detecta y actualiza drivers, gestiona la batería y personaliza hardware. Para ThinkPad y modelos empresariales usa Lenovo System Update (descarga desde support.lenovo.com). Ingresa el número de serie o Machine Type (7 caracteres en la etiqueta inferior o en BIOS → Main → Machine Type) para obtener drivers exactos.',
 '{"tools_required": ["Lenovo Vantage", "Lenovo System Update"], "severity": "media", "brand_note": "ThinkPad usa Machine Type de 7 caracteres para identificar el modelo exacto"}'
),
('Temperatura', 'Lenovo', NULL,
 'Para sobrecalentamiento en Lenovo: abre Lenovo Vantage → Power → Smart Standby y configura el perfil de rendimiento. Activa "Conservation Mode" solo cuando uses el equipo enchufado por largo tiempo para proteger la batería (limita carga al 80%). Para Legion: usa Legion Toolkit (herramienta no oficial pero muy usada) o Lenovo Vantage para control total de ventiladores. Verifica que las rejillas de ventilación laterales y traseras no estén obstruidas.',
 '{"tools_required": ["Lenovo Vantage", "Legion Toolkit"], "severity": "alta", "brand_note": "Lenovo Legion tiene problemas conocidos de throttling en modo Balanced — usar Performance Mode"}'
),
('Temperatura', 'Lenovo', 'Legion',
 'Lenovo Legion con throttling severo: 1) En Lenovo Vantage → Power Plan activa "Performance Mode". 2) Instala Legion Toolkit (GitHub) para control total de ventiladores y desactivar el límite de potencia. 3) En BIOS (F2 al iniciar): habilita "Overboost" si está disponible. 4) Para reducir temperatura del CPU: undervolting con Throttlestop (-100mV en CPU core/cache es seguro en mayoría de Legion). 5) Aplica pasta térmica Thermal Grizzly Kryonaut. El Legion tiene thermal pads entre CPU/GPU y disipador que pueden necesitar reemplazo.',
 '{"tools_required": ["Legion Toolkit", "Throttlestop", "Lenovo Vantage"], "severity": "alta"}'
),
('Audio', 'Lenovo', NULL,
 'Para audio en Lenovo con Dolby Atmos: reinstala Dolby Atmos desde la tienda Lenovo o Microsoft Store. Si los altavoces no suenan tras reinstalar Windows: descarga el driver de audio específico de support.lenovo.com (número de serie o Machine Type). Lenovo usa altavoces Harman en algunos modelos (IdeaPad) — reinstala el software Harman Audio. Para ThinkPad, el driver de audio viene incluido en el paquete de drivers ThinkPad del sitio Lenovo.',
 '{"tools_required": ["Dolby Atmos", "Lenovo System Update"], "severity": "baja", "brand_note": "Modelos premium Lenovo usan Dolby Atmos o Harman Audio según la serie"}'
),
('BIOS', 'Lenovo', NULL,
 'Para acceder al BIOS Lenovo: F1 o F2 durante el inicio en la mayoría de modelos. Para IdeaPad y Yoga con el botón Novo (pequeño agujero en el costado): usa un alfiler y selecciona "BIOS Setup" en el menú Novo. Para actualizar BIOS: Lenovo Vantage → System Update detecta actualizaciones de firmware. En ThinkPad: el BIOS puede actualizarse desde bootable USB con la imagen de Lenovo. Para recuperar BIOS corrupto en ThinkPad: usa la combinación Fn+R al encender.',
 '{"tools_required": ["Lenovo Vantage", "Botón Novo"], "severity": "media", "brand_note": "IdeaPad/Yoga tienen botón Novo físico para recovery y BIOS"}'
),
('Video', 'Lenovo', NULL,
 'Para problemas de video en Lenovo con GPU híbrida (Intel + NVIDIA/AMD): usa Lenovo Vantage → Display para cambiar entre GPU integrada, dedicada o híbrida. En modo "Discreta solo" (require reinicio) toda la carga va a la GPU dedicada, ideal para gaming. Si el monitor externo no funciona: verifica en qué puerto está conectado — algunos puertos en laptops van directo a la GPU integrada y otros a la dedicada. Descarga drivers gráficos desde support.lenovo.com específicos para tu modelo.',
 '{"tools_required": ["Lenovo Vantage", "Support.lenovo.com"], "severity": "media"}'
),
('Red', 'Lenovo', NULL,
 'Para WiFi en Lenovo: verifica si usas adaptador Intel, Realtek o Qualcomm. Para Intel AX200/AX201 (común en ThinkPad y Legion): descarga el driver Intel desde support.lenovo.com. El Intel AX200 tiene problemas conocidos con desconexión frecuente en Windows 11 — actualiza el driver a la versión más reciente. En Lenovo Vantage: Network Booster puede optimizar la prioridad de red. Para ThinkPad con WWAN (4G/5G): el módulo requiere activación en BIOS.',
 '{"tools_required": ["Lenovo Vantage", "Intel WiFi Driver"], "severity": "media", "brand_note": "Intel AX200 tiene driver crítico — descargar siempre desde support.lenovo.com, no desde Intel directamente"}'
),
('USB', 'Lenovo', NULL,
 'Para problemas USB en Lenovo: en ThinkPad con docking station (USB-C o Thunderbolt), actualiza el firmware del dock desde support.lenovo.com. Para puertos USB que no dan energía: verifica en Lenovo Vantage → Power → USB Charging si está habilitada la carga USB en modo suspensión. Para ThinkPad con Ultra Dock: el driver de la dock se instala desde el paquete de drivers ThinkPad. Si el touchpad Synaptics no responde: desinstala y reinstala el driver Synaptics desde support.lenovo.com.',
 '{"tools_required": ["Lenovo Vantage", "ThinkPad Dock Firmware"], "severity": "media"}'
),
('Energia', 'Lenovo', NULL,
 'Para batería en Lenovo: Lenovo Vantage → Power tiene el modo Conservation Mode (limita carga al 80% para prolongar vida útil) y el modo "Rapid Charge" (carga rápida al 80% en ~1 hora). Para calibrar la batería: descarga y conecta ciclos completos 3 veces. Si la batería no carga, verifica en BIOS que la batería esté habilitada. Para ThinkPad con batería integrada: usa Lenovo Vantage para el diagnóstico de estado de la batería.',
 '{"tools_required": ["Lenovo Vantage"], "severity": "media", "brand_note": "Conservation Mode a 80% extiende vida útil de la batería significativamente"}'
),
('Almacenamiento', 'Lenovo', NULL,
 'Para SSD no detectado en Lenovo: verifica en BIOS (F1/F2) → Configuration → Storage que el slot M.2 esté habilitado. En modelos con dos slots M.2: el secundario puede requerir activación manual en BIOS. Para ThinkPad con SSD cifrado (Opal): la BIOS ThinkPad tiene soporte nativo de cifrado que puede bloquear el acceso si se cambia la BIOS/motherboard. Usa Lenovo System Update para mantener el firmware del SSD actualizado.',
 '{"tools_required": ["BIOS ThinkPad", "Lenovo System Update"], "severity": "alta"}'
);

-- ============================================================
-- DATOS: Soluciones específicas por marca — ASUS
-- ============================================================

INSERT INTO catalog_solutions (category, brand, series, solution_text, hardware_specs) VALUES

('Drivers', 'ASUS', NULL,
 'Para gestión de drivers en ASUS: usa MyASUS (para VivoBook/ZenBook/ExpertBook) o Armoury Crate (para ROG/TUF) disponibles en Microsoft Store. Si Armoury Crate causa BSOD o conflictos: desinstálalo completamente con Armoury Crate Uninstall Tool (disponible en asus.com), reinicia en modo seguro y reinstala la versión más reciente. Descarga drivers específicos de asus.com/support ingresando el modelo exacto (ej: ROG Zephyrus G14 GA401).',
 '{"tools_required": ["MyASUS", "Armoury Crate", "Armoury Crate Uninstall Tool"], "severity": "media", "brand_note": "Armoury Crate tiene historial de conflictos — reinstalar con Uninstall Tool completo si hay BSOD"}'
),
('Temperatura', 'ASUS', NULL,
 'Para temperatura en ASUS: en MyASUS activa "Fan Boost Mode" para carga máxima o programa curvas de ventilador manuales. Para ROG/TUF: Armoury Crate → Manual Mode permite control completo de ventiladores. ASUS GameFirst V optimiza la latencia de red, no olvidar GPU Mode. La función "Whisper Mode" en ASUS ROG prioriza silencio sobre rendimiento — cambia a "Performance" o "Turbo" para gaming. Verifica que las rejillas de ventilación no estén obstruidas.',
 '{"tools_required": ["Armoury Crate", "MyASUS", "Fan Xpert"], "severity": "alta"}'
),
('Temperatura', 'ASUS', 'ROG',
 'ASUS ROG con throttling: 1) Armoury Crate → System → Fan Profile → Manual: sube la curva de ventiladores al máximo. 2) Activa el modo "Turbo" en el selector de escenario. 3) Usa el MUX Switch en BIOS (si disponible) para activar GPU dedicada directamente y reducir latencia. 4) Reemplaza la pasta térmica (los ROG Zephyrus usan liquid metal de fábrica en algunos modelos — verifica antes de abrir). 5) ASUS ROG Zephyrus tiene un thermal pad en la VRAM que se degrada: reemplaza con pad de 1.5mm de espesor.',
 '{"tools_required": ["Armoury Crate", "MUX Switch"], "severity": "alta", "brand_note": "Algunos ROG Zephyrus usan liquid metal de fábrica en CPU — no limpiar con pasta normal"}'
),
('Video', 'ASUS', NULL,
 'Para video en ASUS con GPU híbrida: Armoury Crate o MyASUS permite cambiar entre GPU integrada, dedicada y modo automático (Optimus). El MUX Switch en BIOS (modelos ROG 2022+) permite conectar la pantalla directamente a la GPU dedicada eliminando la latencia de Optimus. Descarga drivers gráficos desde asus.com/support específicos para tu modelo. DisplayWidget Centre gestiona monitores externos en laptops ASUS.',
 '{"tools_required": ["Armoury Crate", "MUX Switch BIOS", "DisplayWidget Centre"], "severity": "media"}'
),
('USB', 'ASUS', NULL,
 'Para touchpad y USB en ASUS: el touchpad Precision/ELAN de ASUS requiere driver específico del modelo — descarga desde asus.com/support. Si el touchpad no responde: Fn+F9 activa/desactiva el touchpad en la mayoría de ASUS. Para ROG con hub USB interno (Armoury Crate controla los puertos): reinstala Armoury Crate si los puertos dejan de funcionar. Para USB-C/Thunderbolt: actualiza el firmware Thunderbolt desde ASUS Support.',
 '{"tools_required": ["Driver touchpad ASUS", "Armoury Crate"], "severity": "media", "brand_note": "Fn+F9 activa/desactiva touchpad en casi todos los modelos ASUS"}'
),
('BIOS', 'ASUS', NULL,
 'Para BIOS ASUS: presiona F2 al iniciar (Del en placas de escritorio). ASUS EZ Flash 3 permite actualizar el BIOS directamente desde un USB con el archivo .CAP descargado de asus.com. Para resetear BIOS: F9 en la pantalla de BIOS o el botón ClearCMOS en la placa. ASUS BIOS tiene modo EZ (simple) y Advanced — F7 para cambiar. El modo "Resizable BAR" (útil para GPU) se activa en BIOS → Boot → Above 4G Decoding + Resizable BAR.',
 '{"tools_required": ["ASUS EZ Flash 3", "BIOS ASUS"], "severity": "media"}'
),
('Audio', 'ASUS', NULL,
 'Para audio en ASUS: instala ASUS AudioWizard (MyASUS) o Sonic Studio III (ROG/TUF) desde asus.com/support. Si el audio desaparece tras actualización: reinstala el driver de audio Realtek específico para ASUS desde asus.com (no Realtek.com). Para ROG con sistema de altavoces: Sonic Studio controla el ecualizador y efectos espaciales. Si el micrófono de la webcam tiene ruido: activa la cancelación de ruido en Sonic Studio.',
 '{"tools_required": ["ASUS AudioWizard", "Sonic Studio III"], "severity": "baja"}'
),
('Energia', 'ASUS', NULL,
 'Para batería en ASUS: MyASUS → Battery Health Charging tiene tres modos: Full Capacity (100%), Balanced (80%) y Maximum Lifespan (60%). El modo Balanced o Maximum Lifespan protege la batería a largo plazo. Si la batería no carga con el adaptador original: verifica que el conector USB-C PD sea suficiente para tu modelo (algunos requieren 100W o 140W). ASUS ROG usa conectores propietarios barrel o USB-C PD de alta potencia.',
 '{"tools_required": ["MyASUS Battery Health Charging"], "severity": "media"}'
);

-- ============================================================
-- DATOS: Soluciones específicas por marca — ACER
-- ============================================================

INSERT INTO catalog_solutions (category, brand, series, solution_text, hardware_specs) VALUES

('Temperatura', 'Acer', NULL,
 'Para temperatura en laptops Acer: instala Acer Care Center desde el sitio oficial o Microsoft Store. Para Nitro/Predator: usa PredatorSense para control manual de ventiladores y perfiles térmicos — activa el modo "Turbo" para cargas altas. Acer Cool Boost activa los ventiladores al máximo en equipos sin PredatorSense. Verifica que las rejillas de ventilación laterales y traseras no estén bloqueadas. Limpia con aire comprimido cada 6 meses.',
 '{"tools_required": ["PredatorSense", "Acer Care Center", "Acer Cool Boost"], "severity": "alta"}'
),
('Temperatura', 'Acer', 'Predator',
 'Acer Predator con temperatura crítica: 1) PredatorSense → Fan Control → Manual: sube los ventiladores al máximo. 2) Activa el modo "Turbo" (Fn+F5) que activa los ventiladores al 100% y sube los límites de potencia. 3) Reemplaza la pasta térmica con Thermal Grizzly Kryonaut o Conductonaut (metal líquido). 4) Los modelos Predator Helios 300 tienen thermal pad deficiente en la VRAM — reemplaza con pad 1mm grosor. 5) Un cooling pad externo puede reducir 5-10°C adicionales.',
 '{"tools_required": ["PredatorSense", "Thermal Grizzly Kryonaut"], "severity": "alta"}'
),
('Red', 'Acer', NULL,
 'Para WiFi en Acer: verifica el modelo del adaptador (Intel, Qualcomm Atheros, Mediatek o Realtek). Para Atheros/Qualcomm: descarga el driver desde acer.com/support ingresando el número de serie. Si el WiFi se desconecta frecuentemente: en Propiedades del adaptador → Administración de energía → desactiva "Permitir que el equipo apague este dispositivo para ahorrar energía". Acer Care Center → Diagnósticos de red puede identificar el problema específico.',
 '{"tools_required": ["Acer Care Center", "Driver WiFi específico"], "severity": "media"}'
),
('Drivers', 'Acer', NULL,
 'Para gestión de drivers en Acer: usa Acer Care Center → Actualizar para detectar drivers desactualizados. Descarga drivers desde acer.com/support ingresando el número de serie (etiqueta inferior del equipo o en BIOS → Main → Product Information). Acer tiene perfiles de drivers por región — asegúrate de descargar para la región correcta. Para reinstalación limpia tras formatear: el número de serie en acer.com muestra exactamente los drivers necesarios.',
 '{"tools_required": ["Acer Care Center", "acer.com/support"], "severity": "media"}'
),
('Video', 'Acer', NULL,
 'Para video en Acer con GPU híbrida: los modelos Nitro/Predator tienen interruptor MUX en BIOS para activar GPU dedicada directamente. Acer Display Widget gestiona monitores externos. Para Predator XB o Nitro con pantalla de alta tasa de refresco: verifica en Propiedades de la pantalla → Tasa de actualización que esté configurada al máximo (144Hz, 165Hz, etc.) — puede estar en 60Hz por defecto.',
 '{"tools_required": ["Acer Display Widget", "Acer BIOS MUX Switch"], "severity": "media"}'
),
('Energia', 'Acer', NULL,
 'Para batería en Acer: Acer Care Center → Gestión de energía → Battery Care Mode limita la carga al 80% para prolongar la vida útil. Si la batería se hincha (bulge): es urgente reemplazarla, puede dañar la estructura del equipo. Para calibrar la batería en Acer: descarga hasta el 5%, luego carga ininterrumpidamente al 100%. Si el adaptador no es reconocido: Acer usa adaptadores con identificación en el pin central, los genéricos pueden no ser aceptados.',
 '{"tools_required": ["Acer Care Center"], "severity": "media"}'
),
('BIOS', 'Acer', NULL,
 'Para BIOS Acer: presiona F2 al iniciar para BIOS Setup, F12 para el menú de arranque. Para actualizar BIOS: descarga el archivo de actualización desde acer.com/support → guárdalo en un USB FAT32 → al iniciar presiona F2 → selecciona el archivo. Para resetear BIOS a valores de fábrica: F2 → F9 (Load Defaults) o Main → Restore Defaults. Si el equipo no arranca: Acer eRecovery permite reinstalar el sistema desde partición oculta (Alt+F10 al iniciar).',
 '{"tools_required": ["Acer BIOS Update", "Acer eRecovery"], "severity": "media"}'
);

-- ============================================================
-- DATOS: Soluciones específicas por marca — MSI
-- ============================================================

INSERT INTO catalog_solutions (category, brand, series, solution_text, hardware_specs) VALUES

('Temperatura', 'MSI', NULL,
 'Para temperatura en laptops MSI: instala MSI Center (reemplaza a Dragon Center) desde msi.com/support. En MSI Center → User Scenario: activa el modo "Extreme Performance" para máxima potencia o "Super Battery" para ahorro. Para control manual de ventiladores usa MSI Center → Cooler Boost (máximo rendimiento térmico con ventiladores al 100%). En modelos de alto rendimiento (GE/GT): verifica que el modo "Optimus" o "Discrete Only" esté configurado según el uso.',
 '{"tools_required": ["MSI Center", "Cooler Boost"], "severity": "alta", "brand_note": "Dragon Center fue reemplazado por MSI Center — instala la versión más reciente"}'
),
('Temperatura', 'MSI', 'GE Series',
 'MSI GE con throttling: 1) MSI Center → User Scenario → Extreme Performance. 2) Activa Cooler Boost (Fn+F7) para ventiladores al 100%. 3) GPU Mode: en BIOS (Del) → Advanced → Optimus: cambia a "Discrete Only" para eliminar la latencia de Optimus y mejorar rendimiento. 4) Reemplaza la pasta térmica — MSI GE usa pasta de alta conductividad pero se degrada a los 2-3 años. 5) Los GE series tienen thermal pads entre GPU y disipador que requieren grosor exacto (1mm-1.5mm) al reemplazar.',
 '{"tools_required": ["MSI Center", "Cooler Boost"], "severity": "alta"}'
),
('Video', 'MSI', NULL,
 'Para GPU en laptops MSI con NVIDIA Optimus: MSI Center gestiona el modo GPU (Optimus automático, iGPU solo, dGPU solo). En BIOS (Del al iniciar) → Advanced → Optimus: "MS Hybrid" activa Optimus, "Discrete" usa solo la GPU dedicada (mejor rendimiento, más consumo). Para artefactos de video: actualiza los drivers NVIDIA desde MSI Center o desde msi.com/support (versión específica para tu modelo, no siempre la más reciente es la mejor).',
 '{"tools_required": ["MSI Center", "BIOS MSI Optimus"], "severity": "media"}'
),
('Drivers', 'MSI', NULL,
 'Para drivers en MSI: usa MSI Center → Support → Live Update para actualizar todos los drivers y software del sistema. Descarga drivers desde msi.com/support ingresando el modelo exacto (ej: MSI GF65 Thin 10UE). Si MSI Center causa conflictos (BSOD, congeladas): desinstálalo completamente usando el MSI App Player Uninstaller y reinstala desde cero. Para drivers gráficos NVIDIA: descarga la versión certificada para MSI desde la página de tu modelo específico.',
 '{"tools_required": ["MSI Center", "MSI Live Update"], "severity": "media"}'
),
('Audio', 'MSI', NULL,
 'Para audio en MSI con Nahimic: si el sonido tiene distorsión o la tecnología espacial no funciona, reinstala Nahimic desde MSI Center → Support o desde nahimic.com. Si el audio desaparece: verifica en Administrador de dispositivos que Realtek Audio no tenga conflictos con el driver Nahimic. Para MSI con altavoces Dynaudio: instala el software Dynaudio específico del modelo desde msi.com. Si el conector de audio frontal del chasis no funciona en PC de escritorio MSI: verifica el cable HD Audio en la placa.',
 '{"tools_required": ["Nahimic", "MSI Center"], "severity": "baja"}'
),
('USB', 'MSI', NULL,
 'Para USB en MSI: algunos modelos tienen un hub USB interno gestionado por MSI Center — si los puertos no funcionan, reinicia el hub desde MSI Center → System. Para puertos USB-C/Thunderbolt: actualiza el firmware Thunderbolt desde msi.com/support. Si el controlador USB aparece con error en Administrador de dispositivos: reinstala el chipset Intel desde MSI Center → Live Update. El puerto USB-C en algunos MSI no soporta carga (solo datos) — verifica las especificaciones del modelo.',
 '{"tools_required": ["MSI Center", "Intel Thunderbolt Firmware"], "severity": "media"}'
),
('Energia', 'MSI', NULL,
 'Para batería en MSI: MSI Center → Battery Master permite configurar el umbral de carga (60%, 80% o 100%) para proteger la batería en uso prolongado enchufado. Si la batería no carga más del 80%: verifica que Battery Master no tenga activado el modo "Best for Battery". Los adaptadores MSI usan conectores propietarios de 7.4mm o 5.5mm — no son intercambiables entre familias. Si el adaptador no es reconocido: el sistema puede limitar el rendimiento de la GPU para protegerse.',
 '{"tools_required": ["MSI Center Battery Master"], "severity": "media"}'
);
