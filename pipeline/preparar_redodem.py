# -*- coding: utf-8 -*-
"""Deriva los cruces REDODEM que alimentan la exploración por edad y sexo.

Lee el CSV oficial de monitoreo de protección (40,800 filas), calcula:
  · país de nacimiento × grupo etario
  · país de nacimiento × género
  · destino capturado × grupo etario (solo filas con destino distinto de NA)
  · destino capturado × género (solo filas con destino distinto de NA)

Escribe esos agregados en runtime/data.json. No redistribuye el CSV.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CSV_DEFECTO = AQUI / "insumos_fuente" / "base_monitoreo-de-proteccion_redodem.csv"
DATA_DEFECTO = AQUI / "runtime" / "data.json"
URL_FUENTE = "https://monitoreo-de-proteccion.redodem.org/csv/base_monitoreo-de-proteccion_redodem.zip"
EDADES = ["Niñxs", "Adolescentes", "Adultos jóvenes", "Adultos", "Adultos mayores", "No especificado"]
GENEROS = ["Hombre", "Mujer", "Persona no binaria", "No especificado"]
MOTIVO_ORDER = ["Socioeconómicos", "De violencias", "Personales", "Ambientales"]
PRIVACY_THRESHOLD = 5


def limpio(valor: object) -> str:
    return " ".join(str(valor or "").split())


def partes(valor: object) -> list[str]:
    """Separa multirrespuestas con «|»; NA y blanco no son categorías."""
    texto = limpio(valor)
    if not texto or texto == "NA":
        return []
    return [parte.strip() for parte in texto.split("|") if parte.strip()]


def clave_motivos(categorias: list[str]) -> str:
    """Clave canónica de una combinación, en el orden editorial de motivos."""
    return "|".join(sorted(set(categorias), key=MOTIVO_ORDER.index))


def clave_categorias(categorias: list[str]) -> tuple[str, ...]:
    """Clave normalizada para comparar combinaciones del CSV y de data.json."""
    return tuple(sorted(set(categorias)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=CSV_DEFECTO)
    parser.add_argument("--data", type=Path, default=DATA_DEFECTO)
    args = parser.parse_args()

    if not args.csv.exists():
        raise SystemExit(f"falta el CSV o ZIP de origen: {args.csv}")
    if not args.data.exists():
        raise SystemExit(f"falta data.json: {args.data}")

    if args.csv.suffix.lower() == ".zip":
        with zipfile.ZipFile(args.csv) as paquete:
            nombre = next((n for n in paquete.namelist() if n.lower().endswith(".csv")), None)
            if not nombre:
                raise SystemExit("el ZIP no contiene un CSV")
            crudo = paquete.read(nombre)
        texto = crudo.decode("utf-8-sig")
        lector = csv.DictReader(io.StringIO(texto))
        filas = list(lector)
        archivo_fuente = Path(nombre).name
    else:
        crudo = args.csv.read_bytes()
        with args.csv.open(encoding="utf-8-sig", newline="") as fh:
            filas = list(csv.DictReader(fh))
        archivo_fuente = args.csv.name

    pais_edad = defaultdict(Counter)
    pais_genero = defaultdict(Counter)
    destino_edad = defaultdict(Counter)
    destino_genero = defaultdict(Counter)
    generos = Counter()
    edades = Counter()
    destinos = Counter()
    motivos_filas = Counter()
    motivos_categorias = Counter()
    motivos_combos_crudos = Counter()
    violencias_categorias = Counter()
    violencias_combos = Counter()
    perpetradores_categorias = Counter()
    perpetradores_combos = Counter()
    por_anio = Counter()
    por_anio_violencias = Counter()
    por_anio_violencias_na = Counter()
    por_anio_violencias_blank = Counter()
    coocurrencia = Counter()
    coocurrencia_ids = defaultdict(set)
    motivos_na = motivos_blank = 0
    violencias_na = violencias_blank = 0
    perpetradores_na = perpetradores_blank = 0
    ambos_campos = solo_violencias = solo_perpetradores = ninguno = 0
    no_especificado_solo = 0

    for fila_id, fila in enumerate(filas, start=1):
        pais = limpio(fila.get("pais_de_nacimiento"))
        destino = limpio(fila.get("pais_destino"))
        edad = limpio(fila.get("grupo_etario"))
        genero = limpio(fila.get("genero"))
        anio = limpio(fila.get("anio"))
        motivos = partes(fila.get("motivos_generales"))
        violencias = partes(fila.get("violencias"))
        perpetradores = partes(fila.get("tipos_perpetradores"))
        edades[edad] += 1
        generos[genero] += 1
        por_anio[anio] += 1
        if not pais:
            raise SystemExit("hay filas sin pais_de_nacimiento")
        pais_edad[pais][edad] += 1
        pais_genero[pais][genero] += 1
        if destino and destino != "NA":
            destinos[destino] += 1
            destino_edad[destino][edad] += 1
            destino_genero[destino][genero] += 1

        motivo_crudo = limpio(fila.get("motivos_generales"))
        if motivo_crudo == "NA":
            motivos_na += 1
        elif not motivo_crudo:
            motivos_blank += 1
        if motivos:
            motivos_filas[clave_motivos(motivos)] += 1
            motivos_combos_crudos[clave_categorias(motivos)] += 1
            for motivo in set(motivos):
                motivos_categorias[motivo] += 1

        violencia_cruda = limpio(fila.get("violencias"))
        if violencia_cruda == "NA":
            violencias_na += 1
            por_anio_violencias_na[anio] += 1
        elif not violencia_cruda:
            violencias_blank += 1
            por_anio_violencias_blank[anio] += 1
        if violencias:
            violencias_combos[clave_categorias(violencias)] += 1
            por_anio_violencias[anio] += 1
            for violencia in set(violencias):
                violencias_categorias[violencia] += 1

        perpetrador_crudo = limpio(fila.get("tipos_perpetradores"))
        if perpetrador_crudo == "NA":
            perpetradores_na += 1
        elif not perpetrador_crudo:
            perpetradores_blank += 1
        if perpetradores:
            perpetradores_combos[clave_categorias(perpetradores)] += 1
            for perpetrador in set(perpetradores):
                perpetradores_categorias[perpetrador] += 1
            if set(perpetradores) == {"No especificado"}:
                no_especificado_solo += 1

        if violencias and perpetradores:
            ambos_campos += 1
            for violencia in set(violencias):
                for perpetrador in set(perpetradores):
                    coocurrencia[(violencia, perpetrador)] += 1
                    coocurrencia_ids[(violencia, perpetrador)].add(fila_id)
        elif violencias:
            solo_violencias += 1
        elif perpetradores:
            solo_perpetradores += 1
        else:
            ninguno += 1

    total = len(filas)
    total_destino = sum(destinos.values())
    total_na = sum(1 for fila in filas if limpio(fila.get("pais_destino")) == "NA")

    # Validaciones contra los marginales ya publicados.
    datos = json.loads(args.data.read_text(encoding="utf-8"))
    redodem = datos["redodem"]
    if total != redodem["total_source_rows"]:
        raise SystemExit(f"filas CSV {total} ≠ data.json {redodem['total_source_rows']}")
    fs = redodem["field_summaries"]
    if dict(edades) != fs["grupo_etario"]["categories"]:
        raise SystemExit("los grupos de edad no coinciden con data.json")
    if dict(generos) != fs["genero"]["categories"]:
        raise SystemExit("los géneros no coinciden con data.json")
    if dict(destinos) != {k: v for k, v in fs["pais_destino"]["categories"].items() if k != "NA"}:
        raise SystemExit("los destinos no coinciden con data.json")
    if total_na != fs["pais_destino"]["literal_na"]:
        raise SystemExit("NA de destino no coincide con data.json")

    # Todos los cruces deben reconciliar con su universo.
    if sum(sum(c.values()) for c in pais_edad.values()) != total:
        raise SystemExit("país × edad no reconcilia con 40,800")
    if sum(sum(c.values()) for c in pais_genero.values()) != total:
        raise SystemExit("país × género no reconcilia con 40,800")
    if sum(sum(c.values()) for c in destino_edad.values()) != total_destino:
        raise SystemExit("destino × edad no reconcilia con 6,059")
    if sum(sum(c.values()) for c in destino_genero.values()) != total_destino:
        raise SystemExit("destino × género no reconcilia con 6,059")
    for pais, cruce in pais_edad.items():
        if sum(cruce.values()) != fs["pais_de_nacimiento"]["categories"][pais]:
            raise SystemExit(f"país × edad no reconcilia para {pais}")
    for pais, cruce in pais_genero.items():
        if sum(cruce.values()) != fs["pais_de_nacimiento"]["categories"][pais]:
            raise SystemExit(f"país × género no reconcilia para {pais}")
    for destino, cruce in destino_edad.items():
        if sum(cruce.values()) != destinos[destino]:
            raise SystemExit(f"destino × edad no reconcilia para {destino}")
    for destino, cruce in destino_genero.items():
        if sum(cruce.values()) != destinos[destino]:
            raise SystemExit(f"destino × género no reconcilia para {destino}")

    # Validaciones de los agregados de motivos, coaparición y cobertura anual.
    if dict(por_anio) != {anio: info["total"] for anio, info in redodem["year_month"].items()}:
        raise SystemExit("las filas por año no coinciden con data.json")
    for anio, info in redodem["violence_field_by_year"].items():
        total_anio = por_anio[anio]
        valor_anio = por_anio_violencias[anio]
        na_anio = por_anio_violencias_na[anio]
        blank_anio = por_anio_violencias_blank[anio]
        if (info.get("total"), info.get("non_na_value"), info.get("literal_na")) != (total_anio, valor_anio, na_anio):
            raise SystemExit(f"la cobertura de violencias de {anio} no coincide con data.json")
        if blank_anio:
            raise SystemExit(f"hay {blank_anio} filas con violencias en blanco en {anio}")

    if dict(motivos_categorias) != redodem["departure_reason_mentions"]["mentions"]:
        raise SystemExit("las menciones de motivos no coinciden con data.json")
    if dict(violencias_categorias) != redodem["violence_mentions"]["mentions"]:
        raise SystemExit("las menciones de violencias no coinciden con data.json")
    if dict(perpetradores_categorias) != redodem["perpetrator_mentions"]["mentions"]:
        raise SystemExit("las menciones de perpetradores no coinciden con data.json")
    if motivos_na != fs["motivos_generales"]["literal_na"] or violencias_na != fs["violencias"]["literal_na"] or perpetradores_na != fs["tipos_perpetradores"]["literal_na"]:
        raise SystemExit("los literales NA de los campos no coinciden con data.json")
    if no_especificado_solo != fs["tipos_perpetradores"]["not_specified"]:
        raise SystemExit("las filas que solo declaran «No especificado» no coinciden con data.json")

    fs_motivos = {
        clave_categorias(clave.split("|")): valor
        for clave, valor in fs["motivos_generales"]["categories"].items()
        if clave != "NA"
    }
    fs_violencias = {
        clave_categorias(clave.split("|")): valor
        for clave, valor in fs["violencias"]["categories"].items()
        if clave != "NA"
    }
    fs_perpetradores = {
        clave_categorias(clave.split("|")): valor
        for clave, valor in fs["tipos_perpetradores"]["categories"].items()
        if clave != "NA"
    }
    if fs_motivos != dict(motivos_combos_crudos):
        raise SystemExit("las combinaciones de motivos no coinciden con data.json")
    if fs_violencias != dict(violencias_combos):
        raise SystemExit("las combinaciones de violencias no coinciden con data.json")
    if fs_perpetradores != dict(perpetradores_combos):
        raise SystemExit("las combinaciones de perpetradores no coinciden con data.json")

    if any(len(ids) != coocurrencia[par] for par, ids in coocurrencia_ids.items()):
        raise SystemExit("una pareja de coaparición contiene filas repetidas")
    checks = {
        "total_rows": total,
        "motif_rows": sum(motivos_filas.values()),
        "motif_mentions": sum(motivos_categorias.values()),
        "motif_na": motivos_na,
        "motif_blank": motivos_blank,
        "violence_rows": sum(violencias_combos.values()),
        "violence_mentions": sum(violencias_categorias.values()),
        "violence_na": violencias_na,
        "violence_blank": violencias_blank,
        "perpetrator_rows": sum(perpetradores_combos.values()),
        "perpetrator_mentions": sum(perpetradores_categorias.values()),
        "perpetrator_na": perpetradores_na,
        "perpetrator_blank": perpetradores_blank,
        "both_fields_rows": ambos_campos,
        "violence_only_rows": solo_violencias,
        "perpetrator_only_rows": solo_perpetradores,
        "neither_field_rows": ninguno,
        "no_especificado_only_rows": no_especificado_solo,
        "cooccurrence_pairs": len(coocurrencia),
        "cooccurrence_pair_rows": sum(coocurrencia.values()),
        "max_pair_rows": max(coocurrencia.values()),
        "year_rows": sum(por_anio.values()),
        "year_value_rows": sum(por_anio_violencias.values()),
    }
    esperado = {
        "total_rows": 40800,
        "motif_rows": 6338,
        "motif_mentions": 7863,
        "motif_na": 34462,
        "motif_blank": 0,
        "violence_rows": 499,
        "violence_mentions": 737,
        "violence_na": 40301,
        "violence_blank": 0,
        "perpetrator_rows": 469,
        "perpetrator_mentions": 597,
        "perpetrator_na": 40331,
        "perpetrator_blank": 0,
        "both_fields_rows": 469,
        "violence_only_rows": 30,
        "perpetrator_only_rows": 0,
        "neither_field_rows": 40301,
        "no_especificado_only_rows": 3,
        "cooccurrence_pairs": 76,
        "cooccurrence_pair_rows": 950,
        "max_pair_rows": 78,
        "year_rows": 40800,
        "year_value_rows": 499,
    }
    if checks != esperado:
        raise SystemExit(f"los nuevos agregados no reconciliaron: {checks}")

    def ordenar(cruce: dict[str, Counter], orden: list[str]) -> dict[str, dict[str, int]]:
        salida = {}
        for categoria in sorted(cruce, key=lambda k: (-sum(cruce[k].values()), k)):
            valores = {clave: int(cruce[categoria].get(clave, 0)) for clave in orden if cruce[categoria].get(clave, 0)}
            if valores:
                salida[categoria] = valores
        return salida

    redodem["cross_tabs"] = {
        "pais_de_nacimiento": {
            "grupo_etario": ordenar(pais_edad, EDADES),
            "genero": ordenar(pais_genero, GENEROS),
        },
        "pais_destino": {
            "grupo_etario": ordenar(destino_edad, EDADES),
            "genero": ordenar(destino_genero, GENEROS),
        },
    }
    redodem["cross_tabs_meta"] = {
        "source_file": archivo_fuente,
        "source_url": URL_FUENTE,
        "source_sha256": hashlib.sha256(crudo).hexdigest(),
        "rows": total,
        "destination_rows": total_destino,
        "destination_na": total_na,
        "age_order": EDADES,
        "gender_order": GENEROS,
        "note": "Cruces calculados desde las filas del CSV REDODEM. Destino excluye las filas con NA; edad y género conservan «No especificado».",
    }

    motivos_ordenados = [
        {"category": categoria, "mentions": menciones}
        for categoria, menciones in sorted(motivos_categorias.items(), key=lambda item: (-item[1], item[0]))
    ]
    combinaciones = []
    for combinacion, filas_combinacion in sorted(
        motivos_filas.items(), key=lambda item: (-item[1], len(item[0].split("|")), item[0])
    ):
        categorias = combinacion.split("|") if combinacion else []
        combinaciones.append({
            "key": combinacion,
            "categories": categorias,
            "rows": filas_combinacion,
            "category_count": len(categorias),
        })
    redodem["motif_combinations"] = {
        "unit": "filas de atención/observación",
        "total_rows": total,
        "literal_na": motivos_na,
        "blank": motivos_blank,
        "records_with_value": sum(motivos_filas.values()),
        "mentions_total": sum(motivos_categorias.values()),
        "combination_count": len(combinaciones),
        "categories": motivos_ordenados,
        "combinations": combinaciones,
        "missing_note": "El literal NA no es un motivo: representa una ficha sin motivo registrado. Las filas con NA no entran en las combinaciones.",
        "note": "Cada fila se cuenta una vez en su combinación exacta; las combinaciones no se descomponen en pares parciales. Las menciones por categoría pueden superar las filas porque una ficha puede declarar varios motivos.",
        "reconciliation": {
            "combination_rows": sum(motivos_filas.values()),
            "mentions": sum(motivos_categorias.values()),
            "literal_na": motivos_na,
            "blank": motivos_blank,
        },
    }

    violencias_ordenadas = [
        {"category": categoria, "rows_with_value": filas}
        for categoria, filas in sorted(violencias_categorias.items(), key=lambda item: (-item[1], item[0]))
    ]
    perpetradores_ordenados = [
        {"category": categoria, "rows_with_value": filas}
        for categoria, filas in sorted(perpetradores_categorias.items(), key=lambda item: (-item[1], item[0]))
    ]
    violencia_orden = [item["category"] for item in violencias_ordenadas]
    perpetrador_orden = [item["category"] for item in perpetradores_ordenados]
    celdas = []
    visibles = suprimidas = 0
    for violencia in violencia_orden:
        for perpetrador in perpetrador_orden:
            filas_celda = coocurrencia.get((violencia, perpetrador), 0)
            if filas_celda >= PRIVACY_THRESHOLD:
                visibles += 1
                celdas.append({
                    "violence": violencia,
                    "perpetrator": perpetrador,
                    "status": "visible",
                    "rows": filas_celda,
                })
            elif filas_celda > 0:
                suprimidas += 1
                celdas.append({
                    "violence": violencia,
                    "perpetrator": perpetrador,
                    "status": "suppressed",
                    "rows": None,
                    "range": "1–4",
                })
    cero_pares = len(violencia_orden) * len(perpetrador_orden) - len(coocurrencia)
    redodem["violence_perpetrator"] = {
        "unit": "filas de atención/observación",
        "violence_categories": violencias_ordenadas,
        "perpetrator_categories": perpetradores_ordenados,
        "cells": celdas,
        "visible_cells": visibles,
        "suppressed_cells": suprimidas,
        "zero_pairs": cero_pares,
        "privacy_threshold": PRIVACY_THRESHOLD,
        "privacy_rule": "Se publica la cifra exacta cuando la celda tiene 5 o más filas. Las celdas con 1–4 filas se muestran como rango suprimido y no exponen el valor exacto. Los pares con 0 filas no se listan.",
        "privacy_decision": "El proyecto no tenía un umbral de privacidad para esta matriz. Se adopta 5 por ser el mínimo habitual para no publicar celdas pequeñas de una población vulnerable; el umbral queda como parámetro explícito y se aplica solo a la cifra de la celda.",
        "source_row_id": "posición 1-based del CSV; se usa solo para contar filas distintas y no se exporta",
        "pair_rows_total": sum(coocurrencia.values()),
        "both_fields_rows": ambos_campos,
        "violence_only_rows": solo_violencias,
        "perpetrator_only_rows": solo_perpetradores,
        "neither_field_rows": ninguno,
        "violence_na": violencias_na,
        "perpetrator_na": perpetradores_na,
        "no_especificado_only_rows": no_especificado_solo,
        "note": "Cada celda cuenta filas distintas que contienen ambas categorías; los marginales no se usan para reconstruir el cruce. La coaparición no demuestra causalidad, verificación del perpetrador ni una relación confirmada.",
        "reconciliation": {
            "pairs_with_rows": len(coocurrencia),
            "pair_rows_total": sum(coocurrencia.values()),
            "visible_cells": visibles,
            "suppressed_cells": suprimidas,
            "zero_pairs": cero_pares,
            "both_fields_rows": ambos_campos,
            "violence_only_rows": solo_violencias,
            "perpetrator_only_rows": solo_perpetradores,
            "neither_field_rows": ninguno,
        },
    }

    cobertura_anual = []
    for anio in sorted(por_anio):
        total_anio = por_anio[anio]
        valor_anio = por_anio_violencias[anio]
        na_anio = por_anio_violencias_na[anio]
        blank_anio = por_anio_violencias_blank[anio]
        cobertura_anual.append({
            "year": anio,
            "total_rows": total_anio,
            "rows_with_value": valor_anio,
            "literal_na": na_anio,
            "blank": blank_anio,
            "percent": round(100 * valor_anio / total_anio, 4) if total_anio else 0,
        })
    redodem["violence_coverage_by_year"] = cobertura_anual
    redodem["analysis_meta"] = {
        "analysis_version": "0.34.0",
        "schema_version": "redodem_attention_v1",
        "source_file": archivo_fuente,
        "source_url": URL_FUENTE,
        "source_sha256": hashlib.sha256(crudo).hexdigest(),
        "rows": total,
        "generated_by": "preparar_redodem.py",
        "source_row_id": "posición 1-based del CSV; se usa solo para contar filas distintas y no se exporta",
        "privacy_threshold": PRIVACY_THRESHOLD,
        "privacy_decision": "Umbral 5 para la matriz de coaparición; no existía un parámetro previo en el proyecto. Las celdas 1–4 se suprimen y los ceros no se listan como pares.",
        "reconciliation": checks,
    }

    args.data.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"cruces REDODEM publicados · {total:,} filas · destino {total_destino:,} + NA {total_na:,} · "
        f"{len(pais_edad)} países · {len(destino_edad)} destinos"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
