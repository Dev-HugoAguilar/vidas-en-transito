"""Herramienta offline: normaliza los cuadros públicos del EAAF para el tablero.

Los valores de entrada son una transcripción estructurada del PDF citado, no
microdatos. El grano de salida es una observación por indicador, corte, dimensión
de desglose y categoría publicada. Conserva las unidades separadas y no infiere
variables demográficas no publicadas.

Uso, desde la raíz del clon:
    python pipeline/preparar_eaaf.py

Actualiza `web/data.json` y el respaldo EAAF embebido de `web/index.html`.
No forma parte del runtime ni se ejecuta durante `construir.py`; solo se necesita
cuando se revisa o corrige la transcripción. No altera `missing_search_aggregates`
para no cambiar los cinco indicadores del Panorama: el total de 406
identificaciones vive en `eaaf_public_detail` y el explorador lo lee de ahí.
"""
from __future__ import annotations

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RUNTIME = RAIZ / "web"
DATA_PATH = RUNTIME / "data.json"
HTML_PATH = RUNTIME / "index.html"
SOURCE_URL = (
    "https://eaaf.org/wp-content/uploads/2025/03/"
    "Estadisticas_Proyecto-Frontera_Generales_28feb2025-2.pdf"
)
CUTOFF = "2025-02-28"

BANK_ROWS = [
    ("El Salvador", 455, 452, 1216),
    ("Honduras", 814, 766, 1872),
    ("Chiapas", 104, 101, 320),
    ("Oaxaca", 122, 120, 325),
    ("Guatemala", 238, 232, 735),
    ("México*", 578, 529, 1448),
    ("Costa Rica", 2, 2, 6),
    ("Ecuador", 7, 7, 12),
    ("Perú", 2, 2, 5),
    ("Brasil", 1, 1, 3),
    ("Nicaragua", 28, 28, 58),
]

MEXICO_STATE_ROWS = [
    ("Ciudad de México", 12, 11, 25),
    ("Estado de México", 28, 26, 91),
    ("Guanajuato", 78, 71, 212),
    ("Michoacán", 22, 20, 61),
    ("Veracruz", 13, 13, 41),
    ("Sinaloa", 55, 55, 156),
    ("Jalisco", 16, 16, 37),
    ("San Luis Potosí", 27, 26, 73),
    ("Puebla", 29, 29, 81),
    ("Guerrero", 7, 6, 15),
    ("Tamaulipas", 255, 224, 575),
    ("Zacatecas", 2, 2, 7),
    ("Hidalgo", 7, 6, 19),
    ("Coahuila", 2, 2, 4),
    ("Tlaxcala", 2, 2, 8),
    ("Chihuahua", 6, 5, 14),
    ("Sonora", 4, 4, 10),
    ("Querétaro", 1, 1, 1),
    ("Aguascalientes", 9, 7, 12),
    ("Nayarit", 1, 1, 2),
    ("Colima", 1, 1, 0),
    ("Tabasco", 1, 1, 4),
]

CASES_BY_YEAR = [82, 155, 220, 173, 84, 110, 197, 116, 144, 137, 19, 206, 347, 189, 167, 5]
DONORS_BY_YEAR = [188, 412, 678, 440, 254, 259, 524, 321, 336, 327, 45, 479, 833, 482, 408, 14]
IDENTIFICATIONS_BY_YEAR = [3, 12, 41, 9, 23, 45, 25, 29, 25, 21, 22, 34, 46, 64, 7]
IDENTIFICATIONS_BY_BANK = [
    ("El Salvador", 80), ("Honduras", 85), ("Chiapas", 26), ("Oaxaca", 19),
    ("Guatemala", 68), ("México*", 118), ("Otros países", 10),
]
IDENTIFICATIONS_BY_FIND_COUNTRY = [("Estados Unidos", 280), ("México", 125), ("Guatemala", 1)]

METRICS = {
    "mnl_cases": ("Casos de migrantes no localizados", "casos"),
    "families": ("Familias participantes", "familias"),
    "dna_donors": ("Donantes de ADN reportados", "donantes"),
    "identifications": ("Identificaciones", "identificaciones"),
}


def observation(metric, value, dimension, level, category, parent=None, start="2010", end="2025"):
    label, unit = METRICS[metric]
    return {
        "metric_key": metric,
        "metric_label": label,
        "unit": unit,
        "value": value,
        "operator": "=",
        "cutoff_date": CUTOFF,
        "period_start": start,
        "period_end": end,
        "breakdown_dimension": dimension,
        "breakdown_level": level,
        "category": category,
        "parent_category": parent,
        "source_id": "eaaf_proyecto_frontera_public_aggregates",
        "source_url": SOURCE_URL,
    }


def build_records():
    records = []
    totals = {"mnl_cases": 2351, "families": 2240, "dna_donors": 6000, "identifications": 406}
    for metric, value in totals.items():
        records.append(observation(metric, value, "total", "corredor", "Corredor Centroamérica–México–Estados Unidos"))

    for category, cases, families, donors in BANK_ROWS:
        for metric, value in zip(("mnl_cases", "families", "dna_donors"), (cases, families, donors)):
            records.append(observation(metric, value, "banco_mecanismo", "banco/mecanismo", category))

    for year, value in zip(range(2010, 2026), CASES_BY_YEAR):
        records.append(observation("mnl_cases", value, "year", "año de toma/registro", str(year)))
    for year, value in zip(range(2010, 2026), DONORS_BY_YEAR):
        records.append(observation("dna_donors", value, "year", "año de recolección", str(year)))
    for year, value in zip(range(2011, 2026), IDENTIFICATIONS_BY_YEAR):
        records.append(observation("identifications", value, "year", "año de identificación", str(year), start="2011"))

    for category, value in IDENTIFICATIONS_BY_BANK:
        records.append(observation("identifications", value, "banco_mecanismo", "banco/mecanismo", category))
    for category, value in IDENTIFICATIONS_BY_FIND_COUNTRY:
        records.append(observation("identifications", value, "place_found_country", "país de hallazgo", category))

    for category, cases, families, donors in MEXICO_STATE_ROWS:
        for metric, value in zip(("mnl_cases", "families", "dna_donors"), (cases, families, donors)):
            records.append(observation(metric, value, "state_mexico", "entidad federativa", category, parent="México*"))
    return records


def main():
    records = build_records()
    checks = {
        "cases_by_bank": sum(row[1] for row in BANK_ROWS),
        "families_by_bank": sum(row[2] for row in BANK_ROWS),
        "donors_by_bank": sum(row[3] for row in BANK_ROWS),
        "cases_by_year": sum(CASES_BY_YEAR),
        "donors_by_year": sum(DONORS_BY_YEAR),
        "identifications_by_year": sum(IDENTIFICATIONS_BY_YEAR),
        "identifications_by_bank": sum(value for _, value in IDENTIFICATIONS_BY_BANK),
        "identifications_by_place_found": sum(value for _, value in IDENTIFICATIONS_BY_FIND_COUNTRY),
        "mexico_cases_by_state": sum(row[1] for row in MEXICO_STATE_ROWS),
        "mexico_families_by_state": sum(row[2] for row in MEXICO_STATE_ROWS),
        "mexico_donors_by_state": sum(row[3] for row in MEXICO_STATE_ROWS),
    }
    expected = {
        "cases_by_bank": 2351, "families_by_bank": 2240, "donors_by_bank": 6000,
        "cases_by_year": 2351, "donors_by_year": 6000, "identifications_by_year": 406,
        "identifications_by_bank": 406, "identifications_by_place_found": 406,
        "mexico_cases_by_state": 578, "mexico_families_by_state": 529,
        "mexico_donors_by_state": 1448,
    }
    if checks != expected:
        raise ValueError(f"La transcripción no reconcilia con los totales publicados: {checks}")

    detail = {
        "schema_version": "1.0.0",
        "source_id": "eaaf_proyecto_frontera_public_aggregates",
        "source_url": SOURCE_URL,
        "cutoff_date": CUTOFF,
        "period_start": "2010",
        "period_end": "2025",
        "grain": "una observación por indicador × corte × dimensión de desglose × categoría publicada",
        "records": records,
        "dimension_notes": {
            "year": "Año de toma/registro o recolección según la gráfica fuente; no es fecha de desaparición. La serie de identificaciones comienza en 2011.",
            "banco_mecanismo": "Banco forense o mecanismo que registra/toma el dato; no es nacionalidad ni lugar de desaparición.",
            "place_found_country": "País de hallazgo de restos para identificaciones; separado del banco/mecanismo.",
            "state_mexico": "Desglose de México* por entidad listado en el cuadro EAAF. Las entidades ausentes no se imputan a cero.",
        },
        "methodology_notes": [
            "Casos, familias, donantes e identificaciones conservan unidades distintas y no se suman entre sí.",
            "El resumen del PDF también describe el total de 6,000 como perfiles genéticos de donantes; los desgloses anuales y por banco lo titulan donantes de ADN. Se conserva la etiqueta de los desgloses y no se interpreta como familiares únicos.",
            "El corte 2026-08-14 contiene solo agregados >2,500 casos y >490 identificaciones; permanece como snapshot independiente y no se conecta a esta serie detallada.",
            "El reporte no publica desglose de estos indicadores por edad, sexo ni nacionalidad; no se derivan esas variables.",
            "Los casos por año describen año de toma/registro publicado, no el año en que ocurrió la desaparición.",
            "México* incluye casos ingresados dentro de México fuera de Chiapas y Oaxaca, donde operan bancos forenses.",
        ],
        "reconciliation": checks,
        "review_status": "transcrito del PDF oficial; pendiente segunda revisión humana",
    }

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    data["eaaf_public_detail"] = detail
    # No se duplica el total de 406 en missing_search_aggregates: el Panorama
    # conserva sus cinco indicadores y el explorador toma el total del detalle.
    aggregates = data.get("missing_search_aggregates", [])
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    html_path = HTML_PATH
    html = html_path.read_text(encoding="utf-8")
    begin = "<!-- EAAF_INLINE_DATA_BEGIN -->"
    end = "<!-- EAAF_INLINE_DATA_END -->"
    if begin not in html or end not in html:
        raise ValueError("No se encontraron los marcadores de datos de respaldo en index.html")
    fallback = {
        "detail": detail,
        "aggregates": [row for row in aggregates if row.get("cutoff_date") in (CUTOFF, "2026-08-14")],
    }
    embedded = json.dumps(fallback, ensure_ascii=False, separators=(",", ":"))
    embedded = embedded.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    content_start = html.index(begin) + len(begin)
    content_end = html.index(end, content_start)
    slot = f'\n<script id="eaaf-inline-data" type="application/json">{embedded}</script>\n'
    html = html[:content_start] + slot + html[content_end:]
    html_path.write_text(html, encoding="utf-8")
    print(f"Escritas {len(records)} observaciones normalizadas en {DATA_PATH}")
    print(f"Actualizado respaldo embebido en {html_path}")
    print(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
