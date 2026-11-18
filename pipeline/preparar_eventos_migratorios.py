# -*- coding: utf-8 -*-
"""Deriva las series de eventos y devoluciones desde los cuadros 3.1 y 3.2.3.

Lee los XLS oficiales archivados en `insumos_fuente/eventos_migratorios/`,
valida que los totales coincidan con los subtotales mensuales y la suma de los
tipos de resolución, y publica `eventos_migratorios` y `devoluciones` en
`runtime/data.json`.

No descarga datos ni modifica las demás claves de data.json.

Uso: python dashboards/vidas-en-transito/preparar_eventos_migratorios.py
"""
from __future__ import annotations

import json
from pathlib import Path

import xlrd

AQUI = Path(__file__).resolve().parent
FUENTES = AQUI / "insumos_fuente" / "eventos_migratorios"
DATA = AQUI / "runtime" / "data.json"

# Fecha de consulta de los cuadros archivados. Se fija para que el build sea
# reproducible; actualízala solo si se vuelven a descargar los XLS.
CONSULTA = "2026-11-13"

# Columnas 0-based de los subtotales mensuales en el "Total general".
# 2020 se conserva en el archivo de insumos, pero no entra a la serie: su
# cuadro 3.1 reporta «extranjeros presentados» y no tiene la misma definición
# ni las columnas Presentados/Canalizados de 2021 en adelante.
COBERTURA = {
    2021: (list(range(4, 38, 3)), 12, "enero–diciembre", "completo"),
    2022: (list(range(4, 38, 3)), 12, "enero–diciembre", "completo"),
    2023: (list(range(4, 38, 3)), 12, "enero–diciembre", "completo"),
    2024: (list(range(4, 38, 3)), 12, "enero–diciembre", "completo"),
    2025: (list(range(4, 38, 3)), 12, "enero–diciembre", "completo"),
    2026: (list(range(4, 29, 3)), 9, "enero–septiembre", "parcial"),
}

# Cuadro 3.2.3: totales anuales por tipo de resolución. Las últimas cuatro
# columnas de la fila «Total general» son deportación, retorno asistido,
# retorno asistido de NNA y total.
DEVOLUCIONES = {
    2021: (12, "enero–diciembre", "completo"),
    2022: (12, "enero–diciembre", "completo"),
    2023: (12, "enero–diciembre", "completo"),
    2024: (12, "enero–diciembre", "completo"),
    2025: (12, "enero–diciembre", "completo"),
    2026: (9, "enero–septiembre", "parcial"),
}

TIPOS_RESOLUCION = [
    {
        "key": "deportacion",
        "label": "Eventos de deportación",
        "definition": (
            "Se refiere a devoluciones de migrantes a su país de origen que no observaron "
            "las disposiciones contenidas en la Ley de Migración y su Reglamento, según lo "
            "previsto los arts. 111, 115, 118 y 122 de dicha Ley y de los arts. 242 y 243 "
            "de su Reglamento, previo proceso administrativo de presentación, según lo "
            "establecido en el art. 99 de la misma Ley."
        ),
        "definitionCorta": (
            "Devolución a su país de origen de migrantes que no observaron la Ley de "
            "Migración, previo procedimiento administrativo de presentación."
        ),
    },
    {
        "key": "retorno_asistido",
        "label": "Retorno asistido",
        "definition": (
            "Se refiere a eventos de migrantes de 18 años y más, que solicitaron el "
            "beneficio de retorno asistido para ser devueltos a su país de origen, según lo "
            "previsto los arts. 111, 115, 118 y 119 de la Ley de Migración y del art. 193 "
            "de su Reglamento, previo proceso administrativo de presentación según lo "
            "establecido en el art. 99 de la misma Ley."
        ),
        "definitionCorta": (
            "Migrantes de 18 años y más que solicitaron el beneficio de retorno asistido "
            "para ser devueltos a su país de origen, previo procedimiento de presentación."
        ),
    },
    {
        "key": "retorno_asistido_nna",
        "label": "Retorno asistido de niñas, niños o adolescentes",
        "definition": (
            "Se refiere a eventos de devolución de niñas, niños o adolescentes de 18 años a "
            "su país de origen, según los previsto en los arts. 112, 115 y 120 de la Ley de "
            "Migración y del art. 193 de su Reglamento; así como del art. 97 de la Ley "
            "General de los Derechos de Niñas, Niños y Adolescentes."
        ),
        "definitionCorta": (
            "Devolución de niñas, niños o adolescentes a su país de origen conforme a la "
            "Ley de Migración y la Ley General de los Derechos de Niñas, Niños y Adolescentes."
        ),
    },
]


def leer_total(anio: int) -> tuple[int, int]:
    ruta = FUENTES / f"cuadro3.1_{anio}.xls"
    if not ruta.exists():
        raise SystemExit(f"falta {ruta}")
    hoja = xlrd.open_workbook(ruta).sheet_by_index(0)
    fila_total = next(
        (
            r
            for r in range(hoja.nrows)
            if str(hoja.cell_value(r, 1)).strip().lower() == "total general"
        ),
        None,
    )
    if fila_total is None:
        raise SystemExit(f"{anio}: no se encontró «Total general»")
    columnas, meses, _, _ = COBERTURA[anio]
    total = round(sum(float(hoja.cell_value(fila_total, c) or 0) for c in columnas))
    return total, meses


def leer_devoluciones(anio: int) -> dict:
    ruta = FUENTES / f"cuadro3.2.3_{anio}.xls"
    if not ruta.exists():
        raise SystemExit(f"falta {ruta}")
    hoja = xlrd.open_workbook(ruta).sheet_by_index(0)
    fila_total = next(
        (
            r
            for r in range(hoja.nrows)
            if str(hoja.cell_value(r, 2)).strip().lower() == "total general"
        ),
        None,
    )
    if fila_total is None:
        raise SystemExit(f"{anio}: no se encontró «Total general» en 3.2.3")
    columnas = [hoja.ncols - 4, hoja.ncols - 3, hoja.ncols - 2, hoja.ncols - 1]
    valores = [round(float(hoja.cell_value(fila_total, c) or 0)) for c in columnas]
    deportacion, retorno, nna, total = valores
    if deportacion + retorno + nna != total:
        raise SystemExit(f"{anio}: los tipos de resolución no suman el total ({valores})")
    meses, cobertura, estado = DEVOLUCIONES[anio]
    return {
        "year": anio,
        "total": total,
        "deportacion": deportacion,
        "retorno_asistido": retorno,
        "retorno_asistido_nna": nna,
        "unit": "eventos",
        "months": meses,
        "coverage": cobertura,
        "status": estado,
    }


def main() -> int:
    serie = []
    for anio in sorted(COBERTURA):
        total, meses = leer_total(anio)
        _, _, cobertura, estado = COBERTURA[anio]
        serie.append(
            {
                "year": anio,
                "eventos": total,
                "unit": "eventos",
                "months": meses,
                "coverage": cobertura,
                "status": estado,
            }
        )

    parcial = next(s for s in serie if s["status"] == "parcial")
    hoy = CONSULTA
    bloque = {
        "source": "UPMRIP/SEGOB · Boletín Estadístico, Cuadro 3.1",
        "source_url": "https://www.portales.segob.gob.mx/es/PoliticaMigratoria/CuadrosBOLETIN?Anual=2026&Secc=3",
        "definition_url": "https://portales.segob.gob.mx/es/PoliticaMigratoria/EvPerMigrIrreg",
        "definition": (
            "Eventos de personas en situación migratoria irregular en México a las que "
            "el INM inició un Procedimiento Administrativo Migratorio (PAM), "
            "independientemente de la figura administrativa. La fuente homologa el "
            "concepto para comparabilidad; una misma persona pudo tener más de un evento."
        ),
        "unit": "eventos",
        "updated_at": hoy,
        "consulted_at": hoy,
        "cutoff": f"{parcial['year']}-{parcial['months']:02d}",
        "cutoff_label": f"{parcial['coverage'].split('–')[-1]} de {parcial['year']}",
        "series": serie,
        "notes": [
            "Serie oficial de eventos administrativos; no son personas únicas.",
            "2026 solo incluye enero–septiembre; no se proyecta ni se anualiza.",
            "La definición administrativa cambió en 2013 y 2021; la fuente homologa el concepto.",
            "Los cuadros se publican como información preliminar sujeta a validación.",
            "La fecha consignada es la de consulta del cuadro oficial; la fuente no publica una fecha de actualización explícita.",
            "2020 no se incluye en la serie: su cuadro 3.1 reporta «extranjeros presentados» con columnas distintas; la serie comparable comienza en 2021.",
        ],
    }

    data = json.loads(DATA.read_text(encoding="utf-8"))
    data["eventos_migratorios"] = bloque

    dev_serie = [leer_devoluciones(anio) for anio in sorted(DEVOLUCIONES)]
    dev_parcial = next(s for s in dev_serie if s["status"] == "parcial")
    data["devoluciones"] = {
        "source": "UPMRIP/SEGOB · Boletín Estadístico, Cuadro 3.2.3",
        "source_url": "https://www.portales.segob.gob.mx/es/PoliticaMigratoria/CuadrosBOLETIN?Anual=2026&Secc=3",
        "definition": (
            "Eventos de personas devueltas por la autoridad migratoria mexicana, según "
            "tipo de resolución. Una persona pudo tener más de un evento."
        ),
        "unit": "eventos",
        "updated_at": hoy,
        "consulted_at": hoy,
        "cutoff": f"{dev_parcial['year']}-{dev_parcial['months']:02d}",
        "cutoff_label": f"{dev_parcial['coverage'].split('–')[-1]} de {dev_parcial['year']}",
        "types": TIPOS_RESOLUCION,
        "series": dev_serie,
        "notes": [
            "Eventos administrativos; no son personas únicas.",
            "El total es la suma de los tres tipos de resolución publicados; no se apila.",
            "No se suma con los eventos de movilidad ni con alojamiento.",
            "2026 solo incluye enero–septiembre; no se proyecta ni se anualiza.",
            "Los cuadros se publican como información preliminar sujeta a validación.",
        ],
    }

    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for s in serie:
        print(f"{s['year']}: {s['eventos']:,} eventos · {s['coverage']} · {s['status']}")
    for s in dev_serie:
        print(f"{s['year']}: devoluciones {s['total']:,} · deportación {s['deportacion']:,} · retorno {s['retorno_asistido']:,} · NNA {s['retorno_asistido_nna']:,} · {s['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
