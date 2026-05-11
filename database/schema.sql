-- ============================================================
-- Asistente Inteligente de Soporte Técnico — Schema SQL
-- Base de datos: Supabase (PostgreSQL)
-- ============================================================

-- Habilitar extensión para UUID
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ------------------------------------------------------------
-- Tabla: catalog_solutions
-- Almacena el catálogo de soluciones técnicas por categoría.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS catalog_solutions (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    category        VARCHAR(50) NOT NULL,           -- 'Energia', 'Video', 'BIOS', 'Almacenamiento'
    solution_text   TEXT        NOT NULL,           -- Descripción detallada de la solución
    hardware_specs  JSONB       DEFAULT '{}',       -- Especificaciones de hardware relacionadas
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Índice para búsquedas por categoría
CREATE INDEX IF NOT EXISTS idx_catalog_solutions_category
    ON catalog_solutions (category);

-- ------------------------------------------------------------
-- Tabla: diagnosis_logs
-- Registra cada diagnóstico realizado por el asistente.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS diagnosis_logs (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_query          TEXT        NOT NULL,           -- Mensaje original del usuario
    predicted_category  VARCHAR(50) NOT NULL,           -- Categoría predicha por el modelo
    accuracy            NUMERIC(5,4),                   -- Confianza de la predicción (0.0 - 1.0)
    solution_provided   TEXT,                           -- Solución que se devolvió al usuario
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Índice para análisis temporal de logs
CREATE INDEX IF NOT EXISTS idx_diagnosis_logs_created_at
    ON diagnosis_logs (created_at DESC);

-- Índice para filtrar por categoría predicha
CREATE INDEX IF NOT EXISTS idx_diagnosis_logs_category
    ON diagnosis_logs (predicted_category);

-- ============================================================
-- Datos iniciales del catálogo de soluciones
-- ============================================================

INSERT INTO catalog_solutions (category, solution_text, hardware_specs) VALUES

-- Categoría: Energia
('Energia',
 'Verifica que el cable de alimentación esté correctamente conectado. Comprueba el fusible de la fuente de poder (PSU) y usa un multímetro para medir los voltajes (+12V, +5V, +3.3V). Si la PSU no responde, prueba con otra unidad. Asegúrate de que el botón de encendido de la motherboard esté correctamente conectado al header del panel frontal.',
 '{"components": ["PSU", "Motherboard", "Cable de poder"], "tools_required": ["Multímetro"], "severity": "alta"}'
),

('Energia',
 'Si el equipo enciende pero se apaga inmediatamente, limpia los ventiladores y disipadores de polvo. Aplica pasta térmica nueva al procesador. Verifica que los ventiladores del CPU y chasis estén funcionando. El sobrecalentamiento es una causa frecuente de apagados repentinos.',
 '{"components": ["CPU", "Disipador", "Pasta térmica", "Ventiladores"], "tools_required": ["Pasta térmica", "Limpiador de aire"], "severity": "media"}'
),

-- Categoría: Video
('Video',
 'Si no hay señal de video, verifica que el monitor esté conectado al puerto correcto (GPU dedicada, no tarjeta integrada). Reinserta la GPU en el slot PCIe, limpiando los contactos con alcohol isopropílico. Comprueba los conectores de alimentación PCIe de la GPU (6-pin o 8-pin). Prueba con otro monitor o cable.',
 '{"components": ["GPU", "Monitor", "Cable HDMI/DisplayPort", "PCIe"], "tools_required": ["Alcohol isopropílico", "Borrador"], "severity": "alta"}'
),

('Video',
 'Para artefactos visuales o pantalla con distorsión: actualiza o reinstala los drivers de la GPU. Si el problema persiste, puede indicar VRAM dañada o GPU sobrecalentada. Usa herramientas como GPU-Z para monitorear temperatura y MSI Kombustor para stress test.',
 '{"components": ["GPU", "Drivers", "VRAM"], "tools_required": ["GPU-Z", "MSI Kombustor"], "severity": "media"}'
),

-- Categoría: BIOS
('BIOS',
 'Si el sistema no supera el POST (Power-On Self-Test) o muestra pantalla de BIOS: verifica que la RAM esté correctamente insertada en los slots indicados por el manual (generalmente A2/B2 para dual channel). Limpia los slots de RAM. Prueba con un solo módulo a la vez para identificar módulos defectuosos.',
 '{"components": ["RAM", "BIOS", "Motherboard", "Slots DIMM"], "tools_required": ["Manual de motherboard"], "severity": "alta"}'
),

('BIOS',
 'Para restablecer configuraciones de BIOS: localiza el jumper CMOS en la motherboard (consulta el manual) y cortocircuítalo por 10 segundos con el equipo desconectado, o retira la pila CR2032 por 5 minutos. Esto restablece la configuración de fábrica del BIOS.',
 '{"components": ["BIOS", "CMOS", "Pila CR2032", "Jumper"], "tools_required": ["Destornillador", "Pinzas"], "severity": "baja"}'
),

-- Categoría: Almacenamiento
('Almacenamiento',
 'Si el disco duro o SSD no es detectado: verifica los cables SATA y la alimentación. En el BIOS, confirma que el puerto SATA esté habilitado y en modo AHCI. Usa CrystalDiskInfo para verificar el estado S.M.A.R.T. del disco. Un valor de reallocated sectors alto indica fallas inminentes.',
 '{"components": ["HDD/SSD", "Cable SATA", "BIOS AHCI", "S.M.A.R.T."], "tools_required": ["CrystalDiskInfo"], "severity": "alta"}'
),

('Almacenamiento',
 'Para errores del sistema de archivos o lentitud extrema: ejecuta chkdsk /f /r en Windows o fsck en Linux. Si el SSD muestra bajo rendimiento, verifica que esté conectado a un puerto SATA III (6Gbps) o M.2 PCIe. Considera clonar el disco a uno nuevo si los errores S.M.A.R.T. son críticos.',
 '{"components": ["HDD/SSD", "Sistema de archivos", "SATA III", "M.2 NVMe"], "tools_required": ["chkdsk", "fsck", "CrystalDiskInfo"], "severity": "media"}'
);
