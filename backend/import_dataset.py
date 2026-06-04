"""
import_dataset.py — Importa el CSV de diagnósticos al sistema.

Produce:
  1. extra_training_data.py  — ejemplos de entrenamiento para el modelo ML
  2. Inserta marcas nuevas, series y soluciones en Supabase (si está configurado)

Uso:
  python import_dataset.py [ruta_csv]

  Si no se pasa ruta, usa la ubicación por defecto.
"""

import csv
import os
import sys
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
DEFAULT_CSV = os.path.join(
    os.path.dirname(__file__), "..", "data", "dataset_diagnosticos_equipos.csv"
)
OUTPUT_PY   = os.path.join(os.path.dirname(__file__), "extra_training_data.py")

# Mapeo: Componente_Fallido → categoría del modelo
COMPONENT_MAP: dict[str, str] = {
    "Disco Duro/SSD":    "Almacenamiento",
    "RAM":               "BIOS",
    "Motherboard":       "BIOS",
    "Pantalla":          "Video",
    "Batería":           "Energia",
    "Ventilación":       "Temperatura",
    "GPU":               "Video",
    "Teclado":           "USB",
    "Puertos":           "USB",
    "BIOS":              "BIOS",
    "Conectividad":      "Red",
    "Sistema Operativo": "Drivers",
    "Fuente de Poder":   "Energia",
    "Audio":             "Audio",
}

# Marcas del CSV que ya están en nuestra DB (nombre normalizado)
KNOWN_BRANDS = {"Dell", "HP", "Lenovo", "ASUS", "Acer", "MSI", "Generica"}

# Marcas del CSV → nombre normalizado para la DB
BRAND_NORMALIZE: dict[str, str] = {
    "Custom/Genérica": "Generica",
    "Custom/Genérica": "Generica",
}

# Herramientas de soporte por marca (para insertar en tabla brands)
BRAND_META: dict[str, dict] = {
    "Apple":     {"support_tool": "Apple Diagnostics (D al encender)",
                  "diagnostic_tool": "Apple Hardware Test / Apple Diagnostics",
                  "support_url": "https://support.apple.com"},
    "Huawei":    {"support_tool": "PC Manager",
                  "diagnostic_tool": "Huawei PC Manager Diagnostics",
                  "support_url": "https://consumer.huawei.com/support"},
    "Samsung":   {"support_tool": "Samsung Update",
                  "diagnostic_tool": "Samsung Diagnostics",
                  "support_url": "https://www.samsung.com/support"},
    "Toshiba":   {"support_tool": "Toshiba Service Station",
                  "diagnostic_tool": "PC Diagnostic Tool",
                  "support_url": "https://support.dynabook.com"},
    "Microsoft": {"support_tool": "Surface Diagnostic Toolkit",
                  "diagnostic_tool": "Surface Diagnostic Toolkit (F12)",
                  "support_url": "https://support.microsoft.com/surface"},
    "Xiaomi":    {"support_tool": "Mi PC Manager",
                  "diagnostic_tool": "Mi PC Manager Diagnostics",
                  "support_url": "https://www.mi.com/support"},
    "Amazon":    {"support_tool": "Fire Device Self-Service",
                  "diagnostic_tool": "Amazon Device Support",
                  "support_url": "https://www.amazon.com/devicesupport"},
    "Gigabyte":  {"support_tool": "Gigabyte Control Center (GCC)",
                  "diagnostic_tool": "Gigabyte EasyTune / BIOS Q-Flash",
                  "support_url": "https://www.gigabyte.com/support"},
    "Generica":  {"support_tool": None, "diagnostic_tool": None, "support_url": None},
}


def normalize_brand(raw: str) -> str:
    return BRAND_NORMALIZE.get(raw, raw)


def extract_series(model: str) -> str:
    """Extrae el nombre de serie del modelo (primera 1-2 palabras significativas)."""
    words = model.strip().split()
    if not words:
        return "General"
    # Si el primer token es genérico, usar los primeros 2 tokens
    generic_first = {"PC", "Mini", "All", "Mac"}
    if words[0] in generic_first and len(words) > 1:
        return f"{words[0]} {words[1]}"
    return words[0]


def build_prefix(brand: str, model: str) -> str:
    series = extract_series(model)
    return f"[{brand.upper()} {series.upper()}]"


def load_csv(path: str) -> list[dict]:
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def generate_training_examples(rows: list[dict]) -> list[tuple[str, str]]:
    examples: list[tuple[str, str]] = []
    skipped = 0
    for row in rows:
        comp = row.get("Componente_Fallido", "").strip()
        category = COMPONENT_MAP.get(comp)
        if not category:
            skipped += 1
            continue

        error = row.get("Error_Especifico", "").strip().strip('"')
        if not error or len(error) < 5:
            skipped += 1
            continue

        brand  = normalize_brand(row.get("Marca", "").strip())
        model  = row.get("Modelo", "").strip()
        prefix = build_prefix(brand, model)

        examples.append((f"{prefix} {error}", category))

    print(f"  Ejemplos generados : {len(examples)}")
    print(f"  Filas omitidas     : {skipped}")
    return examples


def collect_solutions(rows: list[dict]) -> list[dict]:
    """
    Agrupa soluciones únicas por (brand, category).
    Para cada combinación toma hasta 2 soluciones distintas.
    """
    seen: dict[tuple, set]   = defaultdict(set)
    result: list[dict]       = []

    for row in rows:
        comp = row.get("Componente_Fallido", "").strip()
        category = COMPONENT_MAP.get(comp)
        if not category:
            continue

        brand    = normalize_brand(row.get("Marca", "").strip())
        series   = extract_series(row.get("Modelo", "").strip())
        solution = row.get("Solucion_Recomendada", "").strip()
        diag     = row.get("Diagnostico", "").strip()
        severity = row.get("Severidad", "").strip()

        if not solution or len(solution) < 10:
            continue

        key = (brand, category)
        if solution not in seen[key] and len(seen[key]) < 2:
            seen[key].add(solution)
            result.append({
                "category": category,
                "brand":    brand,
                "series":   None,           # solución aplica a toda la marca
                "solution_text": solution,
                "hardware_specs": {
                    "severity":    severity,
                    "componente":  comp,
                    "source":      "dataset_csv",
                },
            })

    print(f"  Soluciones únicas generadas: {len(result)}")
    return result


def collect_new_brands(rows: list[dict]) -> list[str]:
    """Devuelve marcas del CSV que no están en nuestra DB."""
    all_brands = {normalize_brand(r.get("Marca", "")) for r in rows}
    return sorted(all_brands - KNOWN_BRANDS)


def collect_new_series(rows: list[dict]) -> dict[str, set]:
    """Devuelve series nuevas por marca."""
    by_brand: dict[str, set] = defaultdict(set)
    for row in rows:
        brand  = normalize_brand(row.get("Marca", "").strip())
        series = extract_series(row.get("Modelo", "").strip())
        tipo   = row.get("Tipo", "laptop").strip().lower()
        device = row.get("Dispositivo", "Laptop").strip().lower()
        # Mapeo a tipos conocidos
        type_map = {"2 en 1": "laptop", "ultrabook": "laptop", "gaming": "gaming",
                    "workstation": "workstation", "económica": "laptop",
                    "premium": "laptop", "empresarial": "laptop",
                    "estándar": "laptop", "profesional": "laptop",
                    "educacional": "laptop", "chromebook": "laptop",
                    "ereader": "laptop", "sff": "desktop", "mini pc": "desktop",
                    "micro": "desktop", "torre": "desktop", "all-in-one": "desktop",
                    "servidor": "desktop"}
        canonical_type = type_map.get(tipo, "desktop" if device == "computadora" else "laptop")
        by_brand[brand].add((series, canonical_type))
    return by_brand


def write_training_file(examples: list[tuple[str, str]], output: str) -> None:
    with open(output, "w", encoding="utf-8") as f:
        f.write('"""\n')
        f.write("extra_training_data.py — Generado automáticamente por import_dataset.py\n")
        f.write(f"Total ejemplos: {len(examples)}\n")
        f.write('"""\n\n')
        f.write("EXTRA_TRAINING_DATA: list[tuple[str, str]] = [\n")
        for text, cat in examples:
            safe_text = text.replace("\\", "\\\\").replace('"', '\\"')
            f.write(f'    ("{safe_text}", "{cat}"),\n')
        f.write("]\n")
    print(f"  Archivo generado   : {output}")


def insert_to_supabase(
    new_brands: list[str],
    new_series: dict[str, set],
    solutions: list[dict],
) -> None:
    from dotenv import load_dotenv
    load_dotenv()
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        print("\n  [!] Supabase no configurado — omitiendo carga a BD.")
        print("      Configura SUPABASE_URL y SUPABASE_KEY en .env para cargar.")
        return

    from supabase import create_client
    sb = create_client(url, key)

    # 1. Insertar marcas nuevas
    brands_inserted = 0
    for brand in new_brands:
        meta = BRAND_META.get(brand, {})
        try:
            sb.table("brands").upsert({
                "name":             brand,
                "display_name":     brand,
                "support_tool":     meta.get("support_tool"),
                "diagnostic_tool":  meta.get("diagnostic_tool"),
                "support_url":      meta.get("support_url"),
            }).execute()
            brands_inserted += 1
        except Exception as e:
            print(f"  [!] Error insertando marca {brand}: {e}")
    print(f"  Marcas insertadas  : {brands_inserted}")

    # 2. Insertar series nuevas
    series_inserted = 0
    for brand, series_set in new_series.items():
        if brand not in new_brands and brand not in KNOWN_BRANDS:
            continue
        for (series_name, series_type) in series_set:
            try:
                # Verificar si ya existe
                r = sb.table("model_series").select("id") \
                    .eq("brand_name", brand).eq("series", series_name).execute()
                if not r.data:
                    sb.table("model_series").insert({
                        "brand_name":  brand,
                        "series":      series_name,
                        "type":        series_type,
                        "description": f"Serie {series_name} de {brand}",
                    }).execute()
                    series_inserted += 1
            except Exception as e:
                print(f"  [!] Error insertando serie {brand}/{series_name}: {e}")
    print(f"  Series insertadas  : {series_inserted}")

    # 3. Insertar soluciones (en lotes de 50)
    solutions_inserted = 0
    batch = []
    for sol in solutions:
        batch.append({
            "category":       sol["category"],
            "brand":          sol["brand"],
            "series":         sol["series"],
            "solution_text":  sol["solution_text"],
            "hardware_specs": sol["hardware_specs"],
        })
        if len(batch) == 50:
            try:
                sb.table("catalog_solutions").insert(batch).execute()
                solutions_inserted += len(batch)
            except Exception as e:
                print(f"  [!] Error en lote: {e}")
            batch = []
    if batch:
        try:
            sb.table("catalog_solutions").insert(batch).execute()
            solutions_inserted += len(batch)
        except Exception as e:
            print(f"  [!] Error en último lote: {e}")
    print(f"  Soluciones cargadas: {solutions_inserted}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV

    if not os.path.exists(csv_path):
        print(f"[ERROR] No se encontró el CSV en: {csv_path}")
        sys.exit(1)

    print(f"\n=== Importando dataset: {csv_path} ===\n")

    rows = load_csv(csv_path)
    print(f"Filas totales: {len(rows)}")

    print("\n[1/4] Generando ejemplos de entrenamiento...")
    examples = generate_training_examples(rows)

    print("\n[2/4] Recopilando soluciones únicas por marca+categoría...")
    solutions = collect_solutions(rows)

    print("\n[3/4] Detectando marcas y series nuevas...")
    new_brands = collect_new_brands(rows)
    new_series = collect_new_series(rows)
    print(f"  Marcas nuevas      : {new_brands}")
    print(f"  Total marcas en CSV: {len(set(normalize_brand(r.get('Marca','')) for r in rows))}")

    print("\n[4/4] Escribiendo archivo de entrenamiento...")
    write_training_file(examples, OUTPUT_PY)

    print("\n[5/5] Cargando a Supabase...")
    insert_to_supabase(new_brands, new_series, solutions)

    print("\n=== Proceso completado ===")
    print(f"  extra_training_data.py contiene {len(examples)} nuevos ejemplos.")
    print("  Reinicia el backend para que el modelo use los nuevos datos.")


if __name__ == "__main__":
    main()
