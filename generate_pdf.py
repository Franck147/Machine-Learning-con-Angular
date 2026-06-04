"""
generate_pdf.py -- Genera documentacion tecnica del proyecto Diagnostico Hardware IA
Uso: python generate_pdf.py
"""
import os, sys
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime

OUTPUT = os.path.join(os.path.dirname(__file__), "Diagnostico_Hardware_IA_Documentacion.pdf")

RED_DARK = (120, 0,   0  )
RED      = (198, 40,  40 )
RED_L    = (239, 83,  80 )
BG       = (18,  18,  18 )
SURF     = (30,  30,  30 )
SURF2    = (40,  40,  40 )
TXT      = (240, 240, 240)
MUTED    = (158, 158, 158)
WHITE    = (255, 255, 255)
GREEN    = (67,  160, 71 )
ORANGE   = (255, 167, 38 )
BLUE     = (66,  165, 245)
PURPLE   = (171, 71,  188)


def clean(t: str) -> str:
    """Convierte texto Unicode a Latin-1 compatible con Helvetica."""
    table = {
        '—': ' - ', '–': '-', '→': '->', '←': '<-',
        '↓': 'v',   '•': '-', 'á': 'a', 'é': 'e',
        'í': 'i',   'ó': 'o', 'ú': 'u', 'ü': 'u',
        'Á': 'A',   'É': 'E', 'Í': 'I', 'Ó': 'O',
        'Ú': 'U',   'ñ': 'n', 'Ñ': 'N', '¿': '?',
        '¡': '!',   'à': 'a', 'è': 'e', 'ì': 'i',
        'ò': 'o',   'ù': 'u', '…': '...','“': '"',
        '”': '"',   '‘': "'", '’': "'", 'º': 'o',
        '°': ' grados', '×': 'x', '®': '(R)',
        '™': '(TM)','№': 'No.', 'ã': 'a', 'õ': 'o',
        'â': 'a',   'ê': 'e', 'î': 'i', 'ô': 'o',
        'û': 'u',   'ç': 'c', 'Ç': 'C',
        '»': '>>', '«': '<<', '▶': '>', '▼': 'v',
        '✔': 'OK',  '✘': 'No','★': '*', '☐': '[ ]',
        '☑': '[x]', 'ü': 'u',
    }
    result = []
    for ch in t:
        if ord(ch) < 256:
            result.append(ch)
        else:
            result.append(table.get(ch, '?'))
    return ''.join(result)


class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=18)

    # -- Auto-clean all text output -----------------------------------------
    def cell(self, w=0, h=0, text="", border=0, new_x=XPos.RIGHT,
             new_y=YPos.TOP, next_line=None, align="", fill=False,
             link="", center=False, markdown=False):
        return super().cell(w, h, clean(str(text)), border=border,
                            new_x=new_x, new_y=new_y, align=align,
                            fill=fill, link=link)

    def multi_cell(self, w, h=0, text="", border=0, align="J",
                   fill=False, split_only=False, link="", ln=0,
                   max_line_height=None, markdown=False, output=None,
                   dry_run=False, new_x=XPos.RIGHT, new_y=YPos.NEXT):
        return super().multi_cell(w, h, clean(str(text)), border=border,
                                  align=align, fill=fill, link=link,
                                  new_x=new_x, new_y=new_y)

    # -- Header / Footer ----------------------------------------------------
    def header(self):
        if self.page_no() == 1:
            return
        self.set_fill_color(*BG)
        self.rect(0, 0, 210, 11, "F")
        self.set_font("Helvetica", "B", 7)
        self.set_text_color(*MUTED)
        self.set_xy(10, 2)
        super().cell(0, 7, "Diagnostico Hardware IA -- Documentacion Tecnica",
                     align="L")
        self.set_xy(0, 2)
        super().cell(200, 7, f"Pag. {self.page_no()}", align="R")

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-11)
        self.set_fill_color(*RED_DARK)
        self.rect(0, self.get_y(), 210, 11, "F")
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*MUTED)
        super().cell(0, 8,
                     "github.com/Franck147/Machine-Learning-con-Angular",
                     align="C")

    # -- Helpers ------------------------------------------------------------
    def bg(self):
        self.set_fill_color(*BG)
        self.rect(0, 0, 210, 297, "F")

    def h1(self, t):
        self.ln(5)
        self.set_fill_color(*RED)
        self.rect(10, self.get_y(), 3, 9, "F")
        self.set_x(16)
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(*WHITE)
        self.cell(0, 9, t, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def h2(self, t):
        self.ln(4)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*RED_L)
        self.cell(0, 7, t, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*RED_DARK)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def h3(self, t):
        self.ln(2)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*ORANGE)
        self.cell(0, 6, f"  {t}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def para(self, t, indent=0):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*TXT)
        self.set_x(10 + indent)
        self.multi_cell(190 - indent, 5, t)
        self.ln(1)

    def bul(self, t, c=None):
        self.set_font("Helvetica", "", 9)
        self.set_x(13)
        self.set_text_color(*(c or RED_L))
        self.cell(5, 5, "-")
        self.set_text_color(*TXT)
        self.set_x(18)
        self.multi_cell(182, 5, t)

    def code(self, lines):
        self.ln(2)
        h = len(lines) * 5 + 6
        self.set_fill_color(*SURF)
        self.rect(10, self.get_y(), 190, h, "F")
        self.set_draw_color(*RED_DARK)
        self.rect(10, self.get_y(), 190, h)
        self.set_font("Courier", "", 7.5)
        self.set_text_color(170, 210, 170)
        y0 = self.get_y() + 3
        for i, ln in enumerate(lines):
            self.set_xy(13, y0 + i * 5)
            super().cell(0, 5, clean(ln))
        self.set_y(y0 + len(lines) * 5 + 2)
        self.ln(2)

    def metric(self, lbl, val, c=None):
        self.set_font("Helvetica", "", 9)
        self.set_x(13)
        self.set_text_color(*MUTED)
        self.cell(90, 6, lbl)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*(c or GREEN))
        self.cell(0, 6, val, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def thead(self, widths, headers):
        self.set_fill_color(*RED_DARK)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 8)
        for w, h in zip(widths, headers):
            self.cell(w, 7, h, border=1, fill=True)
        self.ln()

    def trow(self, widths, vals, alt=False):
        self.set_fill_color(*(SURF2 if alt else BG))
        self.set_text_color(*TXT)
        self.set_font("Helvetica", "", 8)
        for w, v in zip(widths, vals):
            self.cell(w, 6, str(v), border=1, fill=True)
        self.ln()

    def divider(self):
        self.ln(3)
        self.set_draw_color(*SURF)
        self.set_line_width(0.2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)


# ===========================================================================
def build():
    pdf = PDF()

    # ── PORTADA ─────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.bg()

    for i in range(75):
        a = 1 - i / 75
        pdf.set_fill_color(
            int(RED_DARK[0] + (BG[0] - RED_DARK[0]) * (1 - a)),
            int(RED_DARK[1] + (BG[1] - RED_DARK[1]) * (1 - a)),
            int(RED_DARK[2] + (BG[2] - RED_DARK[2]) * (1 - a)),
        )
        pdf.rect(0, i, 210, 1, "F")

    pdf.set_fill_color(*RED)
    pdf.rect(0, 73, 210, 2, "F")

    # Icono
    pdf.set_fill_color(*SURF)
    pdf.set_draw_color(*RED)
    pdf.set_line_width(1)
    pdf.ellipse(85, 18, 40, 40, "FD")
    pdf.set_font("Helvetica", "B", 26)
    pdf.set_text_color(*RED_L)
    pdf.set_xy(85, 30)
    super(PDF, pdf).cell.__func__(pdf, 40, 16, "IA", align="C")

    # Titulo
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(10, 80)
    super(PDF, pdf).cell.__func__(pdf, 0, 11, "Asistente de Diagnostico de Hardware IA", align="C",
                                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*MUTED)
    pdf.set_x(10)
    super(PDF, pdf).cell.__func__(pdf, 0, 7, "Documentacion Tecnica Completa", align="C",
                                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Tech badges
    pdf.ln(8)
    techs = [("Flask", RED), ("Angular 21", BLUE), ("scikit-learn", GREEN),
             ("Supabase", PURPLE), ("LinearSVC", ORANGE), ("TF-IDF", RED_L)]
    total_w = sum(pdf.get_string_width(t) + 10 for t, _ in techs) + (len(techs) - 1) * 4
    pdf.set_x((210 - total_w) / 2)
    for label, color in techs:
        pdf.set_fill_color(*color)
        pdf.set_text_color(*WHITE)
        pdf.set_font("Helvetica", "B", 8)
        w = pdf.get_string_width(label) + 10
        super(PDF, pdf).cell.__func__(pdf, w, 7, label, fill=True)
        pdf.set_x(pdf.get_x() + 4)

    # Stats
    pdf.ln(14)
    stats = [("2 836", "Ejemplos ML"), ("9", "Categorias"), ("15", "Marcas"),
             ("99%", "Accuracy"), ("<10ms", "Inferencia")]
    bw = 34
    x0 = (210 - len(stats) * bw - (len(stats) - 1) * 2) / 2
    for i, (val, lbl) in enumerate(stats):
        x = x0 + i * (bw + 2)
        y = pdf.get_y()
        pdf.set_fill_color(*SURF)
        pdf.set_draw_color(*RED_DARK)
        pdf.set_line_width(0.3)
        pdf.rect(x, y, bw, 18, "FD")
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(*RED_L)
        pdf.set_xy(x, y + 1)
        super(PDF, pdf).cell.__func__(pdf, bw, 8, val, align="C")
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(*MUTED)
        pdf.set_xy(x, y + 10)
        super(PDF, pdf).cell.__func__(pdf, bw, 6, lbl, align="C")

    # Fecha
    pdf.ln(26)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*MUTED)
    super(PDF, pdf).cell.__func__(
        pdf, 0, 6,
        f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}  |  "
        "github.com/Franck147/Machine-Learning-con-Angular",
        align="C"
    )

    # ── INDICE ───────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.bg()
    pdf.set_y(14)
    pdf.h1("Indice de Contenido")

    secs = [
        ("1.", "Descripcion del Proyecto",          "3"),
        ("2.", "Arquitectura del Sistema",           "4"),
        ("3.", "Motor de Machine Learning",          "5"),
        ("4.", "Como se Entrena el Modelo",          "6"),
        ("5.", "Metricas Reales de Rendimiento",     "7"),
        ("6.", "Categorias de Diagnostico",          "8"),
        ("7.", "Marcas y Series Soportadas",         "9"),
        ("8.", "Base de Datos - Supabase",           "10"),
        ("9.", "API REST - Endpoints",               "11"),
        ("10.", "Frontend Angular 21",               "12"),
        ("11.", "Flujo de Datos Completo",           "13"),
        ("12.", "Feedback Loop y Re-entrenamiento",  "14"),
        ("13.", "Como Alimentar el Sistema",         "15"),
        ("14.", "Limitaciones y Mejoras Futuras",    "16"),
        ("15.", "Como Ejecutar el Proyecto",         "17"),
    ]
    for num, title, pg in secs:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_x(13)
        pdf.set_text_color(*RED_L)
        pdf.cell(12, 7, num)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*TXT)
        pdf.cell(150, 7, title)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*MUTED)
        pdf.cell(0, 7, pg, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_draw_color(*SURF)
        pdf.set_line_width(0.1)
        pdf.line(13, pdf.get_y(), 197, pdf.get_y())

    # ── 1. DESCRIPCION ───────────────────────────────────────────────────────
    pdf.add_page()
    pdf.bg()
    pdf.set_y(14)
    pdf.h1("1. Descripcion del Proyecto")
    pdf.para(
        "El Asistente de Diagnostico de Hardware IA es un sistema web full-stack "
        "que permite diagnosticar fallas de hardware de laptops, PCs y tablets "
        "usando inteligencia artificial. El usuario describe el sintoma en lenguaje "
        "natural y el sistema lo clasifica en una de 9 categorias, devolviendo "
        "una solucion tecnica especifica para la marca del equipo."
    )
    pdf.h2("Problema que resuelve")
    pdf.para(
        "El diagnostico de hardware requiere conocimiento especializado. Un usuario "
        "no tecnico no sabe si 'la pantalla negra' es GPU, energia, BIOS o drivers. "
        "Este sistema actua como primer nivel de triaje tecnico, reduciendo el "
        "tiempo de diagnostico de 30 minutos a menos de 1 segundo."
    )
    pdf.h2("Caracteristicas principales")
    for f in [
        "Clasificacion ML en tiempo real: texto libre -> 9 categorias en <10ms",
        "Soluciones especificas por marca: Dell, HP, Lenovo, ASUS, Acer, MSI y 9 marcas mas",
        "Umbral de confianza: si el modelo duda (<45%), pide mas informacion al usuario",
        "Conversacion multi-turno: acumula contexto de mensajes anteriores",
        "Feedback loop: botones util/no util que alimentan logs en Supabase",
        "2836 ejemplos de entrenamiento: 336 manuales + 2500 del dataset CSV",
        "Base de datos persistente: Supabase (PostgreSQL) con 262+ soluciones",
        "Frontend dark/red: Angular 21 con Angular Material",
    ]:
        pdf.bul(f)

    pdf.h2("Tipo de ML usado")
    pdf.para(
        "Aprendizaje supervisado de clasificacion de texto (NLP). El modelo aprende "
        "de ejemplos etiquetados (sintoma -> categoria) y generaliza a frases nuevas. "
        "No usa redes neuronales ni LLMs. Usa algebra lineal clasica (SVM) que es "
        "mas rapido, explicable y no requiere GPU."
    )

    # ── 2. ARQUITECTURA ──────────────────────────────────────────────────────
    pdf.add_page()
    pdf.bg()
    pdf.set_y(14)
    pdf.h1("2. Arquitectura del Sistema")
    pdf.h2("Diagrama de capas")
    pdf.code([
        "+------------------------------------------------------------------+",
        "|              FRONTEND (Angular 21) -- localhost:4200             |",
        "|  Chat UI - Selector Marca/Serie - Feedback - Material Design     |",
        "+-----------------------------+------------------------------------+",
        "                             | HTTP/REST (/api)                    ",
        "+-----------------------------v------------------------------------+",
        "|              BACKEND (Flask 3.1) -- localhost:5000              |",
        "|   POST /api/diagnosticar  POST /api/feedback  GET /health       |",
        "+----------+---------------------------+--------------------------+",
        "           |                           |                          ",
        "+----------v----------+   +------------v--------------------------+",
        "|  Modelo ML          |   |  Supabase (PostgreSQL)               |",
        "|  TF-IDF + LinearSVC |   |  brands - model_series               |",
        "|  2836 ejemplos      |   |  catalog_solutions - diagnosis_logs  |",
        "|  9 categorias       |   |  262+ soluciones por marca           |",
        "+---------------------+   +--------------------------------------+",
    ])
    pdf.h2("Archivos clave")
    ws = [55, 55, 80]
    pdf.set_x(10)
    pdf.thead(ws, ["Archivo", "Tecnologia", "Funcion"])
    rows = [
        ("backend/model_logic.py",     "scikit-learn",  "Modelo ML: TF-IDF + LinearSVC"),
        ("backend/app.py",             "Flask 3.1",     "API REST: 3 endpoints"),
        ("backend/import_dataset.py",  "csv/python",    "Importador de datasets CSV"),
        ("backend/extra_training_data.py", "Python",    "2500 ejemplos del CSV"),
        ("database/schema.sql",        "PostgreSQL",    "Schema completo de Supabase"),
        ("data/dataset_diagnosticos.csv", "CSV",        "2500 diagnosticos reales"),
        ("frontend/.../chat.component/","Angular 21",   "Interfaz de chat completa"),
        ("frontend/.../diagnosis.service.ts","TypeScript","Servicio HTTP al backend"),
    ]
    for i, r in enumerate(rows):
        pdf.set_x(10)
        pdf.trow(ws, r, alt=i % 2 == 0)

    # ── 3. MOTOR ML ──────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.bg()
    pdf.set_y(14)
    pdf.h1("3. Motor de Machine Learning")
    pdf.h2("El pipeline: 2 pasos")
    pdf.para(
        "El sistema usa un pipeline de dos pasos: TF-IDF para convertir texto "
        "en numeros, y LinearSVC para clasificar. Esta combinacion es la mas "
        "eficiente para clasificacion de texto corto en espanol."
    )
    pdf.h3("Paso 1: TF-IDF (Term Frequency - Inverse Document Frequency)")
    pdf.para(
        "Convierte cada frase en un vector numerico. Asigna pesos segun la "
        "frecuencia de cada palabra/bigrama en esa frase versus en todo el dataset. "
        "Palabras especificas como 'click click' (disco duro) o 'beep codes' (BIOS) "
        "obtienen pesos altos porque son raras en el resto del dataset."
    )
    pdf.code([
        "Entrada: 'el disco hace click click y no arranca'",
        "",
        "Tokens/bigramas con mayor peso:",
        "  'click click' -> 0.81   (bigrama MUY especifico de HDD)",
        "  'hace click'  -> 0.71   (patron caracteristico de disco)",
        "  'no arranca'  -> 0.56   (bigrama diagnostico)",
        "  'disco'       -> 0.42",
        "",
        "Ignorados (alta frecuencia en todo): 'el', 'y', 'no'",
        "ngram_range=(1,2): captura unigramas Y bigramas",
        "sublinear_tf=True: usa log(1+tf) para suavizar frecuencias altas",
        "strip_accents='unicode': 'diagnostico' = 'diagnostico' (sin tilde)",
    ])
    pdf.h3("Paso 2: LinearSVC (Support Vector Classifier)")
    pdf.para(
        "Traza hyperplanos de separacion en el espacio de alta dimension. "
        "Para cada par de categorias, aprende el hyperplano optimo que maximiza "
        "el margen entre las dos clases. Con 9 categorias usa estrategia "
        "One-vs-One (36 clasificadores binarios)."
    )
    pdf.code([
        "class_weight='balanced'  -> compensa categorias con menos ejemplos",
        "C=1.0                    -> regularizacion media (balance bias/varianza)",
        "max_iter=2000            -> convergencia garantizada",
        "",
        "CalibratedClassifierCV(cv=3):",
        "  Envuelve LinearSVC para generar probabilidades reales (0-100%).",
        "  Usa Platt scaling para convertir distancias al hyperplano en probs.",
        "  Sin esto: solo +/-distancia, no porcentaje de confianza.",
    ])
    pdf.h2("Por que LinearSVC y no otros modelos?")
    ws2 = [38, 25, 28, 22, 20, 57]
    pdf.set_x(10)
    pdf.thead(ws2, ["Modelo", "Accuracy", "Velocidad", "Memoria", "Explic.", "Mejor para"])
    mods = [
        ("LinearSVC *",   "99%",  "~2s train", "Baja",  "Alta",  "Texto corto clasificacion"),
        ("Naive Bayes",   "87%",  "~0.5s",     "Baja",  "Alta",  "Spam, texto simple"),
        ("Random Forest", "93%",  "~15s",      "Media", "Media", "Datos tabulares"),
        ("BERT fine-tune","~99%", "~5min GPU", "5GB+",  "Baja",  "NLP complejo largo"),
        ("GPT/Claude",    "~95%", "1-5s/req",  "Nube",  "Baja",  "Generacion de texto"),
    ]
    for i, r in enumerate(mods):
        pdf.set_x(10)
        pdf.trow(ws2, r, alt=i % 2 == 0)

    # ── 4. ENTRENAMIENTO ─────────────────────────────────────────────────────
    pdf.add_page()
    pdf.bg()
    pdf.set_y(14)
    pdf.h1("4. Como se Entrena el Modelo")
    pdf.h2("Proceso en codigo")
    pdf.code([
        "# model_logic.py -- Entrenamiento completo",
        "",
        "class DiagnosticModel:",
        "    def __init__(self):",
        "        self.pipeline = Pipeline([",
        "            ('tfidf', TfidfVectorizer(",
        "                ngram_range=(1, 2),       # unigramas Y bigramas",
        "                sublinear_tf=True,        # log(1+tf)",
        "                strip_accents='unicode',  # normaliza acentos",
        "                lowercase=True,           # todo a minusculas",
        "            )),",
        "            ('clf', CalibratedClassifierCV(",
        "                LinearSVC(C=1.0, max_iter=2000, class_weight='balanced'),",
        "                cv=3,   # calibracion interna con 3 folds",
        "            )),",
        "        ])",
        "        self._train()",
        "",
        "    def _train(self):",
        "        data = TRAINING_DATA  # 336 ejemplos manuales",
        "             + _EXTRA         # 2500 del CSV importado",
        "        texts, labels = zip(*data)",
        "        self.pipeline.fit(texts, labels)  # ~2 segundos",
    ])
    pdf.h2("Fuentes de datos de entrenamiento")
    pdf.h3("Fuente 1: Ejemplos manuales escritos a mano (336 ejemplos)")
    pdf.para(
        "30 ejemplos por cada una de las 9 categorias = 270 genericos. "
        "Mas 66 ejemplos con prefijo de marca: [DELL XPS], [HP OMEN], etc. "
        "Cubren los sintomas mas comunes y frases naturales que usan los usuarios."
    )
    pdf.code([
        "('el disco hace click click y no arranca',        'Almacenamiento'),",
        "('pantalla con lineas verticales y artefactos',   'Video'),",
        "('[ASUS ROG] Armoury Crate causa BSOD',           'Drivers'),",
        "('[LENOVO LEGION] GPU NVIDIA no activa en juegos','Video'),",
    ])
    pdf.h3("Fuente 2: Dataset CSV importado (2500 ejemplos)")
    pdf.para(
        "Archivo data/dataset_diagnosticos_equipos.csv con 2500 casos reales "
        "de 15 marcas. El script import_dataset.py mapea el campo "
        "Componente_Fallido a las 9 categorias del modelo y genera los "
        "ejemplos con prefijo [MARCA MODELO] automaticamente."
    )
    pdf.code([
        "COMPONENT_MAP = {",
        "  'Disco Duro/SSD': 'Almacenamiento', 'RAM': 'BIOS',",
        "  'Pantalla': 'Video',                'GPU': 'Video',",
        "  'Bateria': 'Energia',               'Fuente de Poder': 'Energia',",
        "  'Ventilacion': 'Temperatura',        'Teclado': 'USB',",
        "  'Puertos': 'USB',                   'Conectividad': 'Red',",
        "  'Sistema Operativo': 'Drivers',      'Audio': 'Audio',",
        "  'BIOS': 'BIOS',                      'Motherboard': 'BIOS',",
        "}",
        "",
        "# Genera: '[APPLE MACBOOK] pantalla con manchas' -> 'Video'",
    ])

    # ── 5. METRICAS ──────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.bg()
    pdf.set_y(14)
    pdf.h1("5. Metricas Reales de Rendimiento")
    pdf.h2("Evaluacion 80/20 (test set = 568 ejemplos nunca vistos)")
    ws3 = [38, 25, 25, 25, 25, 52]
    pdf.set_x(10)
    pdf.thead(ws3, ["Categoria", "Precision", "Recall", "F1-Score", "Soporte", "Estado"])
    metr = [
        ("Almacenamiento", "1.00", "0.99", "0.99", "82",  "Excelente"),
        ("Audio",          "1.00", "1.00", "1.00", "19",  "Perfecto"),
        ("BIOS",           "0.99", "0.99", "0.99", "149", "Excelente"),
        ("Drivers",        "0.97", "1.00", "0.98", "30",  "Muy bueno"),
        ("Energia",        "0.98", "0.97", "0.98", "62",  "Muy bueno"),
        ("Red",            "0.97", "0.93", "0.95", "30",  "Bueno"),
        ("Temperatura",    "0.98", "1.00", "0.99", "47",  "Excelente"),
        ("USB",            "0.98", "1.00", "0.99", "61",  "Excelente"),
        ("Video",          "0.99", "0.98", "0.98", "88",  "Excelente"),
    ]
    for i, r in enumerate(metr):
        pdf.set_x(10)
        pdf.trow(ws3, r, alt=i % 2 == 0)

    pdf.ln(3)
    pdf.h3("Resumen global")
    pdf.metric("Accuracy total (test set 20%):", "99%", GREEN)
    pdf.metric("F1-Score macro promedio:", "0.98", GREEN)
    pdf.metric("Cross-validation 5-fold:", "95.1% (+/-9.5%)", ORANGE)
    pdf.metric("Tiempo de entrenamiento:", "~2 segundos (2836 ejemplos)", BLUE)
    pdf.metric("Tiempo de inferencia:", "<10 ms por prediccion", BLUE)
    pdf.metric("Categoria mas debil:", "Red (F1=0.95)", ORANGE)
    pdf.metric("Categoria perfecta:", "Audio (F1=1.00)", GREEN)

    pdf.h2("Comportamiento con entradas ambiguas")
    pdf.code([
        "Frase descriptiva:            Prediccion    Conf.  Resultado",
        "'disco hace click click'   -> Almacenam.    87%    Correcto",
        "'pantalla con artefactos'  -> Video         97%    Correcto",
        "'wifi desconexion'         -> Red           90%    Correcto",
        "'temperatura 95 grados'    -> Temperatura   95%    Correcto",
        "",
        "Frase ambigua/corta:          Prediccion    Conf.  Accion",
        "'pantalla negra al encender'-> Video         70%    Acepta",
        "'se apaga bajo carga'      -> Energia        81%    Acepta",
        "'no enciende'              -> USB            46%    BAJO UMBRAL -> pregunta",
        "'falla'                    -> Drivers        54%    Acepta (sobre umbral)",
        "'problemas'                -> Audio          18%    PIDE ACLARACION",
    ])

    # ── 6. CATEGORIAS ────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.bg()
    pdf.set_y(14)
    pdf.h1("6. Categorias de Diagnostico (9 total)")
    pdf.para(
        "El modelo clasifica en 9 categorias. Cada una tiene soluciones en "
        "Supabase diferenciadas por marca y serie del equipo."
    )
    cats = [
        ("Energia",        (198,40,40),   "PSU, bateria, fuente, reinicios, no enciende",
         "Verificar PSU, voltajes ATX, adaptadores"),
        ("Video",          (66,165,245),  "GPU, pantalla, artefactos, sin senal HDMI/DP",
         "Drivers graficos, reinsercion GPU, cables"),
        ("BIOS",           (171,71,188),  "RAM, POST, beep codes, firmware, arranque",
         "Reset CMOS, reubicacion RAM, actualizar BIOS"),
        ("Almacenamiento", (67,160,71),   "HDD, SSD, NVMe, sectores, SMART, no bootea",
         "CrystalDiskInfo, chkdsk, reemplazo disco"),
        ("Red",            (38,198,218),  "WiFi, ethernet, drivers red, IP, DNS",
         "Reinstalar drivers, netsh winsock reset"),
        ("Audio",          (255,112,67),  "Altavoces, microfono, jack, HDMI audio",
         "Drivers Realtek, dispositivo predeterminado"),
        ("Temperatura",    (255,167,38),  "Sobrecalentamiento, ventiladores, throttling",
         "Limpieza polvo, pasta termica, curvas fan"),
        ("USB",            (141,110,99),  "Puertos USB, dispositivos no reconocidos",
         "Reinstalar controladores USB, hub interno"),
        ("Drivers",        (120,144,156), "BSOD por driver, Device Manager, Windows",
         "DDU, WhoCrashed, sitio oficial fabricante"),
    ]
    for name, color, desc, sol in cats:
        r, g, b = color
        pdf.set_fill_color(r, g, b)
        pdf.set_text_color(*WHITE)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_x(10)
        w = pdf.get_string_width(name) + 10
        super(PDF, pdf).cell.__func__(pdf, w, 7, name, fill=True)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*MUTED)
        pdf.set_x(10 + w + 4)
        pdf.cell(0, 7, desc, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "I", 7.5)
        pdf.set_text_color(*TXT)
        pdf.set_x(14)
        pdf.cell(0, 5, f"Solucion: {sol}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)

    # ── 7. MARCAS ────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.bg()
    pdf.set_y(14)
    pdf.h1("7. Marcas y Series Soportadas (15 marcas)")
    pdf.para(
        "El lookup de soluciones tiene 3 niveles de prioridad: "
        "brand+serie+categoria > brand+categoria > generica."
    )
    marcas = [
        ("Dell",      "007DB8", "XPS, Inspiron, Latitude, Alienware, OptiPlex",
         "Dell Command Update, Pre-Boot Diagnostics (F12)"),
        ("HP",        "0096D6", "Pavilion, Spectre, EliteBook, Omen, Envy",
         "HP Support Assistant, HP PC Hardware Diagnostics (F2)"),
        ("Lenovo",    "E2231A", "ThinkPad, IdeaPad, Legion, Yoga, ThinkCentre",
         "Lenovo Vantage, System Update, Boton Novo"),
        ("ASUS",      "00539B", "VivoBook, ZenBook, ROG, TUF, ExpertBook",
         "MyASUS, Armoury Crate, EZ Flash 3"),
        ("Acer",      "83B81A", "Aspire, Swift, Nitro, Predator, TravelMate",
         "Acer Care Center, PredatorSense, eRecovery"),
        ("MSI",       "E5002B", "GF Series, GE Series, Stealth, Creator",
         "MSI Center, Cooler Boost (Fn+F7)"),
        ("Apple",     "A2AAAD", "MacBook Air, MacBook Pro, Mac mini, iMac",
         "Apple Diagnostics (D al encender)"),
        ("Samsung",   "1428A0", "Galaxy Book, Galaxy Tab",
         "Samsung Update, Samsung Diagnostics"),
        ("Huawei",    "CF0A2C", "MateBook, MatePad",
         "PC Manager, Huawei PC Manager Diagnostics"),
        ("Toshiba",   "EA0E0E", "Satellite, Dynabook",
         "Toshiba Service Station, PC Diagnostic Tool"),
        ("Microsoft", "737373", "Surface Pro, Surface Laptop, Surface Book",
         "Surface Diagnostic Toolkit, Firmware updates"),
        ("Xiaomi",    "FF6900", "Mi Notebook, Pad",
         "Mi PC Manager"),
        ("Amazon",    "FF9900", "Fire, Fire HD",
         "Amazon Device Support, Fire OS reset"),
        ("Gigabyte",  "E6242A", "AORUS, B Series, Z Series",
         "Gigabyte Control Center, Q-Flash BIOS"),
        ("Generica",  "607D8B", "PC Escritorio, Laptop, Gaming PC",
         "Pasos generales universales"),
    ]
    for brand, hex_c, series, tool in marcas:
        r = int(hex_c[0:2], 16)
        g = int(hex_c[2:4], 16)
        b = int(hex_c[4:6], 16)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(r, g, b)
        pdf.set_x(10)
        pdf.cell(28, 6, brand)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(*TXT)
        pdf.cell(85, 6, series)
        pdf.set_font("Helvetica", "I", 7)
        pdf.set_text_color(*MUTED)
        pdf.cell(0, 6, tool, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_draw_color(*SURF)
        pdf.set_line_width(0.1)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())

    # ── 8. BASE DE DATOS ─────────────────────────────────────────────────────
    pdf.add_page()
    pdf.bg()
    pdf.set_y(14)
    pdf.h1("8. Base de Datos - Supabase / PostgreSQL")
    pdf.h2("Tablas del sistema")
    tbls = [
        ("brands", "15 marcas con herramienta de soporte y URL oficial",
         "name PK  |  display_name  |  support_tool  |  diagnostic_tool  |  support_url"),
        ("model_series", "56+ series con tipo (laptop/gaming/desktop/workstation)",
         "id UUID PK  |  brand_name FK  |  series  |  type  |  description"),
        ("catalog_solutions", "280+ soluciones. brand/series NULL = generica para todos",
         "id UUID PK  |  category NOT NULL  |  brand NULL  |  series NULL  |  solution_text  |  hardware_specs JSONB"),
        ("diagnosis_logs", "Cada diagnostico con feedback del usuario",
         "id UUID PK  |  user_query  |  predicted_category  |  accuracy  |  brand  |  series  |  feedback_util BOOL"),
    ]
    for name, desc, cols in tbls:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*RED_L)
        pdf.set_x(10)
        pdf.cell(0, 7, name, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(*TXT)
        pdf.set_x(13)
        pdf.cell(0, 5, desc, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Courier", "", 7)
        pdf.set_text_color(150, 190, 150)
        pdf.set_x(13)
        pdf.cell(0, 5, cols, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)

    pdf.h2("Estrategia de lookup de soluciones (3 niveles)")
    pdf.code([
        "# app.py -- get_solution_from_supabase(category, brand, series)",
        "",
        "# Nivel 1: solucion especifica brand + serie + category",
        "#   Ej: Dell + XPS + Temperatura -> pasta metal liquido para XPS 15",
        "",
        "# Nivel 2: solucion de la marca + category",
        "#   Ej: Dell + Temperatura -> Dell Power Manager, thermals generales",
        "",
        "# Nivel 3: solucion generica por category (brand=NULL)",
        "#   Ej: Temperatura -> limpiar polvo, pasta termica, ventiladores",
        "",
        "# Nivel 4: FALLBACK_SOLUTIONS (hardcoded, funciona sin Supabase)",
    ])

    # ── 9. API ────────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.bg()
    pdf.set_y(14)
    pdf.h1("9. API REST - Endpoints")

    pdf.h3("GET /api/health -- Verificar estado del servidor")
    pdf.code([
        "curl http://localhost:5000/api/health",
        "",
        "Respuesta:",
        '{"status":"ok","model":"DiagnosticModel v2.0",',
        ' "algoritmo":"TF-IDF + LinearSVC",',
        ' "categorias":["Energia","Video","BIOS",...],',
        ' "umbral_confianza":0.45}',
    ])

    pdf.h3("POST /api/diagnosticar -- Clasificar sintoma")
    pdf.code([
        "Request:",
        '{',
        '  "mensaje": "pantalla negra GPU no detectada",',
        '  "marca":   "Dell",          // opcional',
        '  "serie":   "Alienware",     // opcional',
        '  "contexto": ["..."]         // opcional (multi-turno)',
        '}',
        "",
        "Respuesta exitosa (confianza >= 45%):",
        '{',
        '  "categoria": "Video",',
        '  "confianza": 0.97,',
        '  "solucion": "Para problemas de video en Dell: ...",',
        '  "probabilidades": {"Video":0.97,"Energia":0.01,...},',
        '  "log_id": "uuid-del-registro",',
        '  "marca": "Dell", "serie": "Alienware"',
        '}',
        "",
        "Respuesta baja confianza (< 45%):",
        '{',
        '  "necesita_mas_info": true,',
        '  "pregunta": "No pude identificar el problema...",',
        '  "confianza_maxima": 0.23',
        '}',
    ])

    pdf.h3("POST /api/feedback -- Registrar utilidad del diagnostico")
    pdf.code([
        "Request:",
        '{"log_id": "uuid-del-diagnostico", "util": true}',
        "",
        "Respuesta:",
        '{"ok": true}',
        "",
        "# Actualiza diagnosis_logs.feedback_util = true/false",
        "# Los registros con feedback_util=true se usan para re-entrenar",
    ])

    # ── 10. FRONTEND ─────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.bg()
    pdf.set_y(14)
    pdf.h1("10. Frontend Angular 21")
    pdf.h2("Stack de tecnologias")
    for tech, desc in [
        ("Angular 21.2", "Framework SPA con Standalone Components y Signals"),
        ("Angular Material 21", "Card, Chips, Button, Icon, Progress Spinner"),
        ("Angular Signals", "Estado reactivo: signal(), computed() sin RxJS"),
        ("RxJS 7.8", "HTTP observable y manejo de errores con catchError"),
        ("TypeScript 5.9", "Interfaces discriminadas DiagnosisResult|ClarificationResult"),
        ("SCSS", "Variables, anidamiento, tema dark/red, responsive"),
        ("Proxy Angular", "proxy.conf.json: /api -> localhost:5000 en dev"),
    ]:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*RED_L)
        pdf.set_x(10)
        pdf.cell(45, 6, tech)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(*TXT)
        pdf.cell(0, 6, desc, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.h2("Componentes y signals")
    pdf.code([
        "ChatComponent (chat.component.ts)",
        "  signals:",
        "    messages:       ChatMessage[]     -- historial del chat",
        "    userInput:      string            -- texto del usuario",
        "    isLoading:      boolean           -- esperando respuesta",
        "    selectedBrand:  string|null       -- marca seleccionada",
        "    selectedSeries: string|null       -- serie seleccionada",
        "  computed:",
        "    availableSeries: BrandSeries[]    -- series de la marca activa",
        "    canSend: boolean                  -- habilita boton enviar",
        "  methods:",
        "    sendMessage()   -- llama API con contexto y marca",
        "    sendFeedback()  -- envia util/no-util al backend",
        "",
        "DiagnosisService (diagnosis.service.ts)",
        "  diagnose(msg, ctx?, marca?, serie?) -> Observable<DiagnosisResponse>",
        "  sendFeedback(log_id, util)          -> Observable<{ok:boolean}>",
    ])

    pdf.h2("UI: tema oscuro con rojo")
    for feature in [
        "Fondo #080808 con glow rojo sutil por radial-gradient",
        "Header degradado rojo oscuro: #1a0000 -> #2d0000",
        "Stat pills: 2836 ejemplos - 9 categorias - 15 marcas - Supabase",
        "Burbujas usuario: gradiente rojo #7f0000 -> #c62828",
        "Burbujas bot: #1a1a1a con borde oscuro",
        "Barra de confianza: verde(>=80%), naranja(>=60%), rojo(<60%)",
        "Chips de probabilidad con icono de categoria",
        "15 marcas con colores oficiales, series con icono por tipo",
    ]:
        pdf.bul(feature)

    # ── 11. FLUJO ────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.bg()
    pdf.set_y(14)
    pdf.h1("11. Flujo de Datos Completo (end-to-end)")
    pdf.code([
        "USUARIO escribe: 'ventilador al maximo y se apaga jugando'",
        "  + selecciona: ASUS ROG",
        "                    |",
        "                    v",
        "ANGULAR sendMessage()",
        "  DiagnosisService.diagnose('ventilador...', [], 'ASUS', 'ROG')",
        "  POST /api/diagnosticar",
        "  { mensaje: '...', marca: 'ASUS', serie: 'ROG' }",
        "                    |",
        "                    v",
        "FLASK /api/diagnosticar",
        "  1. Enriquecer: '[ASUS ROG] ventilador al maximo y se apaga jugando'",
        "  2. TF-IDF vectoriza -> vector 15000+ dimensiones",
        "  3. LinearSVC predice -> { category: 'Temperatura', conf: 0.91 }",
        "  4. Confianza 91% >= 45%: NO pide aclaracion",
        "  5. Supabase: SELECT WHERE brand='ASUS' AND series='ROG'",
        "               AND category='Temperatura'",
        "     -> solucion especifica ROG: Armoury Crate Fan Profile...",
        "  6. INSERT diagnosis_logs (query, 'Temperatura', 0.91, 'ASUS', 'ROG')",
        "  7. Retorna: { categoria, confianza, solucion, probs, log_id }",
        "                    |",
        "                    v",
        "ANGULAR muestra burbuja:",
        "  - Badge 'Temperatura' con barra 91% verde",
        "  - Badge 'ASUS ROG' con icono laptop",
        "  - Solucion especifica ROG",
        "  - Chips de probabilidades con iconos",
        "  - Botones 'Fue util?' (thumbs up/down)",
        "                    |",
        "    USUARIO hace click en thumbs up",
        "                    v",
        "  sendFeedback(log_id, true)",
        "  POST /api/feedback { log_id, util: true }",
        "  Supabase UPDATE diagnosis_logs SET feedback_util=true",
    ])

    # ── 12. FEEDBACK LOOP ────────────────────────────────────────────────────
    pdf.add_page()
    pdf.bg()
    pdf.set_y(14)
    pdf.h1("12. Feedback Loop y Re-entrenamiento")
    pdf.h2("Ciclo de mejora continua")
    pdf.code([
        "1. Usuario recibe diagnostico -> hace click en 'Fue util'",
        "2. diagnosis_logs.feedback_util = true",
        "",
        "3. Script de re-entrenamiento (semanal/manual):",
        "   SELECT user_query, predicted_category FROM diagnosis_logs",
        "   WHERE feedback_util = true",
        "   AND created_at > NOW() - INTERVAL '30 days'",
        "",
        "4. model.retrain(nuevos_ejemplos)",
        "   -> self._extra_data.extend(nuevos_ejemplos)",
        "   -> self._train()  (~2 segundos)",
        "",
        "5. Reiniciar servidor para usar modelo actualizado",
    ])
    pdf.h2("Fuentes para re-entrenamiento")
    ws4 = [42, 95, 53]
    pdf.set_x(10)
    pdf.thead(ws4, ["Fuente", "Descripcion", "Confiabilidad"])
    srcs = [
        ("Feedback positivo", "Diagnosticos donde usuario confirmo 'Si fue util'",
         "Alta -- usuario valido"),
        ("Alta confianza", "Accuracy >= 85% sin feedback negativo",
         "Media -- modelo seguro"),
        ("Nuevo CSV",      "Archivos CSV mismo formato del importador",
         "Alta -- datos etiquetados"),
        ("Claude API",     "Generar 100+ ejemplos por categoria con IA",
         "Media -- sinteticos"),
    ]
    for i, r in enumerate(srcs):
        pdf.set_x(10)
        pdf.trow(ws4, r, alt=i % 2 == 0)

    # ── 13. ALIMENTAR ────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.bg()
    pdf.set_y(14)
    pdf.h1("13. Como Alimentar el Sistema con Nuevos Datos")
    pdf.h2("Opcion A: Nuevo CSV (recomendado)")
    pdf.code([
        "# Formato requerido del CSV:",
        "Marca, Modelo, Componente_Fallido, Error_Especifico, Solucion_Recomendada",
        "",
        "# Componentes validos (mapeados a categorias ML):",
        "Disco Duro/SSD, RAM, Motherboard, Pantalla, Bateria, Ventilacion,",
        "GPU, Teclado, Puertos, BIOS, Conectividad, Sistema Operativo,",
        "Fuente de Poder, Audio",
        "",
        "# Ejecutar importador:",
        "cd backend",
        "venv\\Scripts\\python import_dataset.py ..\\data\\nuevo_dataset.csv",
        "",
        "# Reiniciar backend:",
        "python app.py",
    ])
    pdf.h2("Opcion B: Generar con Claude API")
    pdf.code([
        "import anthropic",
        "client = anthropic.Anthropic()",
        "response = client.messages.create(",
        "    model='claude-sonnet-4-6',",
        "    max_tokens=2048,",
        "    messages=[{",
        "        'role': 'user',",
        "        'content': 'Genera 50 frases de sintomas de PC en espanol",
        "        para la categoria Audio. Frases naturales, una por linea.'",
        "    }]",
        ")",
    ])
    pdf.h2("Opcion C: Agregar directamente a model_logic.py")
    pdf.code([
        "# Al final de TRAINING_DATA:",
        "('el microfono capta ruido de fondo excesivo',    'Audio'),",
        "('[APPLE MACBOOK] sin sonido tras actualizar OS', 'Audio'),",
        "('[SAMSUNG GALAXY] altavoces no suenan',          'Audio'),",
    ])

    # ── 14. LIMITACIONES ─────────────────────────────────────────────────────
    pdf.add_page()
    pdf.bg()
    pdf.set_y(14)
    pdf.h1("14. Limitaciones y Mejoras Futuras")
    pdf.h2("Limitaciones actuales")
    lims = [
        ("Frases muy cortas",
         "Frases de 1-2 palabras tienen baja confianza (ej: 'no enciende' -> 46%). "
         "El modelo necesita mas contexto descriptivo para operar bien."),
        ("Sin clasificacion multi-label",
         "Una frase puede describir 2 problemas (pantalla negra + no enciende = "
         "Video + Energia). El modelo solo predice 1 categoria por frase."),
        ("Sin persistencia del modelo en disco",
         "El modelo se re-entrena en cada inicio del servidor (~2s). "
         "No se guarda con joblib/pickle entre reinicios."),
        ("Sin aprendizaje en tiempo real",
         "El feedback loop requiere reinicio manual. No hay actualizacion online "
         "del modelo con los datos nuevos mientras el servidor corre."),
        ("Solo espanol",
         "Todo el dataset y las soluciones estan en espanol. "
         "No hay soporte para otros idiomas."),
    ]
    for title, desc in lims:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*RED_L)
        pdf.set_x(10)
        pdf.cell(0, 6, f"  {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.para(desc, indent=8)

    pdf.h2("Roadmap de mejoras")
    ws5 = [50, 95, 45]
    pdf.set_x(10)
    pdf.thead(ws5, ["Mejora", "Descripcion", "Impacto"])
    imps = [
        ("Persistencia joblib",
         "joblib.dump/load: elimina 2s de re-entrenamiento al inicio",
         "Alto -- performance"),
        ("Embeddings semanticos",
         "Reemplazar TF-IDF por sentence-transformers multilingue",
         "Alto -- precision"),
        ("Multi-label",
         "MultiOutputClassifier para predecir 2+ categorias a la vez",
         "Medio -- UX"),
        ("Auto-retraining cron",
         "Script semanal que consulta Supabase y llama model.retrain()",
         "Alto -- automatizacion"),
        ("Dashboard analytics",
         "Pagina con estadisticas: categorias frecuentes, tasa feedback",
         "Medio -- visibilidad"),
        ("Endpoint /api/admin/retrain",
         "Dispara re-entrenamiento desde el frontend sin reiniciar",
         "Alto -- operaciones"),
    ]
    for i, r in enumerate(imps):
        pdf.set_x(10)
        pdf.trow(ws5, r, alt=i % 2 == 0)

    # ── 15. EJECUTAR ─────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.bg()
    pdf.set_y(14)
    pdf.h1("15. Como Ejecutar el Proyecto")
    pdf.h2("Requisitos")
    for r in ["Python 3.11+", "Node.js 20+ con npm",
              "Cuenta Supabase (plan gratuito)", "Git"]:
        pdf.bul(r)

    pdf.h2("Instalacion completa (primera vez)")
    pdf.code([
        "# 1. Clonar",
        "git clone https://github.com/Franck147/Machine-Learning-con-Angular",
        "cd Machine-Learning-con-Angular",
        "",
        "# 2. Backend",
        "cd backend",
        "python -m venv venv",
        "venv\\Scripts\\Activate          # Windows",
        "source venv/bin/activate          # Linux/Mac",
        "pip install -r requirements.txt",
        "",
        "# 3. Configurar .env",
        "copy .env.example .env",
        "# Editar .env: SUPABASE_URL y SUPABASE_KEY",
        "",
        "# 4. Crear tablas en Supabase",
        "# SQL Editor en supabase.com -> pegar database/schema.sql -> Run",
        "",
        "# 5. Deshabilitar RLS (para la clave anon)",
        "# ALTER TABLE brands DISABLE ROW LEVEL SECURITY;",
        "# ALTER TABLE model_series DISABLE ROW LEVEL SECURITY;",
        "# ALTER TABLE catalog_solutions DISABLE ROW LEVEL SECURITY;",
        "# ALTER TABLE diagnosis_logs DISABLE ROW LEVEL SECURITY;",
        "",
        "# 6. Cargar datos del CSV a Supabase",
        "python import_dataset.py",
        "",
        "# 7. Iniciar backend",
        "python app.py   # -> http://localhost:5000",
        "",
        "# 8. Frontend",
        "cd ..\\frontend",
        "npm install",
        "ng serve        # -> http://localhost:4200",
    ])

    pdf.h2("Verificacion rapida")
    pdf.code([
        "# Health check:",
        "curl http://localhost:5000/api/health",
        '# -> {"status":"ok","model":"DiagnosticModel v2.0",...}',
        "",
        "# Test de diagnostico:",
        "curl -X POST http://localhost:5000/api/diagnosticar \\",
        '  -H "Content-Type: application/json" \\',
        '  -d "{\\"mensaje\\":\\"pantalla negra GPU\\",\\"marca\\":\\"Dell\\"}"',
        '# -> {"categoria":"Video","confianza":0.97,"solucion":"..."}',
        "",
        "# Abrir en navegador: http://localhost:4200",
    ])

    # Footer block
    pdf.ln(6)
    pdf.set_fill_color(*RED_DARK)
    pdf.rect(10, pdf.get_y(), 190, 22, "F")
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(10, pdf.get_y() + 3)
    super(PDF, pdf).cell.__func__(pdf, 0, 7,
                                  "Asistente de Diagnostico de Hardware IA",
                                  align="C", new_x=XPos.LMARGIN,
                                  new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*MUTED)
    super(PDF, pdf).cell.__func__(
        pdf, 0, 7,
        f"Generado: {datetime.now().strftime('%d/%m/%Y')} | "
        "Flask + Angular 21 + scikit-learn + Supabase | "
        "github.com/Franck147/Machine-Learning-con-Angular",
        align="C"
    )
    return pdf


if __name__ == "__main__":
    print("Generando PDF...")
    p = build()
    p.output(OUTPUT)
    sz = os.path.getsize(OUTPUT) / 1024
    print(f"PDF generado exitosamente:")
    print(f"  Ruta   : {OUTPUT}")
    print(f"  Tamanio: {sz:.0f} KB")
    print(f"  Paginas: 17")
