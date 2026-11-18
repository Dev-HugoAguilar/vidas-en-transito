# -*- coding: utf-8 -*-
"""Regenera la capa «Tránsito migrante documentado» (zonas estatales del INM, 2023).

Las fuentes son dos comunicados públicos del INM:

- **119/23 (20 de septiembre de 2023).** La ruta del tren pasa por el Estado de
  México, Hidalgo, Querétaro, Guanajuato, Aguascalientes, Nuevo León, Durango y
  Chihuahua; el INM propuso puntos de verificación, entre ellos Huehuetoca.
- **124/23 (22 de septiembre de 2023).** Acciones de enero a septiembre de 2023 en
  Veracruz, Tlaxcala, Coahuila, Puebla, Estado de México, Nuevo León, Guanajuato,
  Chihuahua y Oaxaca.

La fuente no publica trayectos ni coordenadas reutilizables: la capa dibuja **zonas
estatales**, no rutas. La geometría de cada zona es el límite del estado en Natural
Earth (admin-1, 10m, dominio público), simplificado a 0,01°. No se copia ningún mapa
del INM ni de El Colegio de México.

Uso:
    python dashboards/vidas-en-transito/preparar_evidencia.py
    python dashboards/vidas-en-transito/preparar_evidencia.py --zip RUTA --salida RUTA

Requiere geopandas. Si falta el ZIP de Natural Earth, se descarga a `insumos_fuente/`.
El resultado publicado se verifica con `MANIFEST_LOCAL.json` y `construir.py --comprobar`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path

import geopandas as gpd
from shapely.geometry import mapping

AQUI = Path(__file__).resolve().parent
GEOGRAFIA = AQUI / "runtime" / "geografia"
INSUMOS = AQUI / "insumos_fuente"
ZIP_POR_DEFECTO = INSUMOS / "ne_admin1.zip"
URL_NATURAL_EARTH = "https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_admin_1_states_provinces.zip"
FECHA_CORTE = "2026-11-13"

FUENTE_119 = {
    "id": "inm_119_2023",
    "titulo": "INM · Comunicado 119/23",
    "fecha": "2023-09-20",
    "url": "https://www.gob.mx/inm/prensa/propone-inm-a-ferromex-fortalecer-coordinacion-en-acciones-y-estrategias-para-evitar-que-personas-migrantes-arriesguen-su-vida-a-bordo-de-los-trenes",
    "alcance": "La ruta del tren pasa por estos estados; el INM propuso puntos de verificación en Huehuetoca (Estado de México) y en esos estados.",
}
FUENTE_124 = {
    "id": "inm_124_2023",
    "titulo": "INM · Comunicado 124/23",
    "fecha": "2023-09-22",
    "url": "https://www.gob.mx/inm/prensa/acuerdan-inm-y-ferromex-acciones-con-los-tres-niveles-de-gobierno-y-cbp-para-la-ruta-del-sistema-ferroviario-a-fin-de-que-las-personas-migrantes-no-arriesguen-su-vida-a-bordo?idiom=es-MX",
    "alcance": "658 acciones en el sistema ferroviario y 8 988 personas migrantes rescatadas entre enero y septiembre de 2023 en estos estados.",
}

ESTADOS_119 = {
    "México": "ruta del tren; punto de verificación propuesto en Huehuetoca",
    "Hidalgo": "ruta del tren; punto de verificación propuesto",
    "Querétaro": "ruta del tren; punto de verificación propuesto",
    "Guanajuato": "ruta del tren; punto de verificación propuesto",
    "Aguascalientes": "ruta del tren; punto de verificación propuesto",
    "Nuevo León": "ruta del tren; punto de verificación propuesto",
    "Durango": "ruta del tren; punto de verificación propuesto",
    "Chihuahua": "ruta del tren; punto de verificación propuesto",
}
ESTADOS_124 = {
    "Veracruz": "acciones de enero a septiembre de 2023",
    "Tlaxcala": "acciones de enero a septiembre de 2023",
    "Coahuila": "acciones de enero a septiembre de 2023",
    "Puebla": "acciones de enero a septiembre de 2023",
    "México": "acciones de enero a septiembre de 2023",
    "Nuevo León": "acciones de enero a septiembre de 2023",
    "Guanajuato": "acciones de enero a septiembre de 2023",
    "Chihuahua": "acciones de enero a septiembre de 2023",
    "Oaxaca": "acciones de enero a septiembre de 2023",
}

REFERENCIA_COLMEX = {
    "titulo": "El Colegio de México · mapa de rutas de trenes de carga utilizadas por migrantes",
    "fecha": "2014",
    "url": "https://repositorio.colmex.mx/concern/archival_documents/765372448",
    "nota": "Referencia histórica de 2014. Licencia CC BY-NC-ND: no se copia ni se adapta su geometría; no se dibuja.",
}


def descargar_si_falta(zip_natural_earth: Path) -> Path:
    if zip_natural_earth.exists():
        return zip_natural_earth
    zip_natural_earth.parent.mkdir(parents=True, exist_ok=True)
    print(f"descargando Natural Earth admin-1 → {zip_natural_earth}")
    with urllib.request.urlopen(URL_NATURAL_EARTH) as origen, zip_natural_earth.open("wb") as destino:
        destino.write(origen.read())
    return zip_natural_earth


def construir(zip_natural_earth: Path) -> dict:
    gdf = gpd.read_file(f"zip://{zip_natural_earth}")
    columna_admin = "admin" if "admin" in gdf.columns else "adm0_a3"
    mexicanos = gdf[gdf[columna_admin].isin({"Mexico", "MEX"})]

    nombres = set(ESTADOS_119) | set(ESTADOS_124)
    faltan = sorted(nombres - set(mexicanos["name"]))
    if faltan:
        raise SystemExit(f"estados sin polígono en Natural Earth: {faltan}")

    features = []
    for _, fila in mexicanos.iterrows():
        nombre = fila["name"]
        if nombre not in nombres:
            continue
        geometria = fila.geometry.simplify(0.01, preserve_topology=True)
        if geometria.is_empty:
            continue
        fuentes, detalle = [], []
        if nombre in ESTADOS_119:
            fuentes.append(FUENTE_119["id"])
            detalle.append(f"119/23: {ESTADOS_119[nombre]}")
        if nombre in ESTADOS_124:
            fuentes.append(FUENTE_124["id"])
            detalle.append(f"124/23: {ESTADOS_124[nombre]}")
        features.append({
            "type": "Feature",
            "geometry": mapping(geometria),
            "properties": {
                "estado": nombre,
                "iso": fila.get("iso_3166_2") or "",
                "fuentes": fuentes,
                "periodo": "2023",
                "detalle": "; ".join(detalle),
                "nota": "Zona estatal mencionada por el INM; no define un trayecto exacto ni una ruta vigente.",
            },
        })

    return {
        "type": "FeatureCollection",
        "metadata": {
            "titulo": "Tránsito migrante documentado · fuentes y períodos",
            "descripcion": "Zonas estatales mencionadas por el INM en 2023 como parte de la ruta del tren y de las acciones de rescate. No son trayectos ni una ruta vigente.",
            "fuentes": [FUENTE_119, FUENTE_124],
            "referencias_sin_geometria": [REFERENCIA_COLMEX],
            "geometria_zonas": "Natural Earth 10m admin-1 (dominio público), simplificada a 0,01°",
            "creado": FECHA_CORTE,
            "estados": len(features),
        },
        "features": features,
    }


def principal() -> int:
    parser = argparse.ArgumentParser(description="Genera las zonas estatales del INM 2023.")
    parser.add_argument("--zip", type=Path, default=ZIP_POR_DEFECTO, help="ZIP de Natural Earth admin-1")
    parser.add_argument("--salida", type=Path, default=GEOGRAFIA / "evidencia_transito.geojson")
    args = parser.parse_args()

    documento = construir(descargar_si_falta(args.zip))
    texto = json.dumps(documento, ensure_ascii=False, separators=(",", ":"))
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(texto, encoding="utf-8")

    print(f"zonas: {len(documento['features'])} · {sorted(f['properties']['estado'] for f in documento['features'])}")
    print(f"bytes: {len(texto.encode('utf-8'))} · sha256: {hashlib.sha256(texto.encode('utf-8')).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
