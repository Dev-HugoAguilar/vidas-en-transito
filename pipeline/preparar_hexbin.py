# -*- coding: utf-8 -*-
"""Prepara el mapa hexagonal de «Muertes documentadas» (OIM MMP).

Fuente: OIM Missing Migrants Project, conjunto publicado en HDX
(«Missing Migrants Project Data», licencia CC BY-IGO), descargado el 13-nov-2026.
El proyecto no distribuye el CSV crudo: este guion deriva una malla de hexágonos
con agregados por celda, y deja registrados el corte, la licencia, el filtro de
corredor y las exclusiones.

Universos (nunca se suman entre sí):

- ``muertes``: filas con ``number_dead > 0``.
- ``desapariciones``: filas con ``number_missing > 0``.

Filtros: rutas del corredor del proyecto (las mismas seis etiquetas que usa
``data.json``), coordenadas parseables dentro del encuadre México-Centroamérica y
frontera sur de EE. UU. Las filas fuera del encuadre se cuentan y se declaran.

Salidas (dentro de `web/`, el runtime publicado):
- ``web/geografia/hexbin_muertes.geojson``: celdas terrestres con agregados.
- ``web/geografia/hexbin_muertes.json``: metadatos, totales y comprobaciones.
- ``web/geografia/estados_mexico.geojson``: límites estatales (Natural Earth).

Uso:
    python pipeline/preparar_hexbin.py
    python pipeline/preparar_hexbin.py --csv RUTA --sin-estados
    python pipeline/preparar_hexbin.py --insumos RUTA

Requiere shapely y geopandas. El CSV y el ZIP de Natural Earth se descargan a la
carpeta de insumos excluidos (por defecto ``pipeline/insumos_fuente/``; se puede
indicar con ``--insumos`` o con MIGRATION_SOURCE_DIR). No se publican.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point, mapping
from shapely.prepared import prep

RAIZ = Path(__file__).resolve().parents[1]
WEB = RAIZ / "web"
GEOGRAFIA = WEB / "geografia"
INSUMOS = Path(os.environ.get("MIGRATION_SOURCE_DIR", RAIZ / "pipeline" / "insumos_fuente"))

URL_MMP = "https://data.humdata.org/dataset/fc59785a-31d2-4018-aac7-6b9f619ae8ec/resource/99078436-9c4a-473b-a073-428304a9cf8a/download/iom-missing-migrants-project-data.csv"
URL_ADMIN1 = "https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_admin_1_states_provinces.zip"

CORTE_DESCARGA = "2026-11-13"
RUTAS = [
    "US-Mexico border crossing",
    "Darien",
    "Caribbean to US",
    "Caribbean to Central America",
    "Haiti to Dominican Republic",
    "Venezuela to Caribbean",
]
ENCUADRE = {"lon0": -118.5, "lon1": -76.5, "lat0": 6.5, "lat1": 33.5}
VISTA = {"ancho": 1200, "alto": 820, "margen": 24}
RADIO = 11.0  # circunradio del hexágono, en unidades de la vista
DISTANCIA_MAXIMA = 0.75  # grados: una fila sin celda propia se asigna a la tierra más cercana

RAD = math.pi / 180


def merc(lat: float) -> float:
    return math.log(math.tan(math.pi / 4 + (max(-85.0, min(85.0, lat)) * RAD) / 2))


def proyeccion() -> dict:
    ancho = VISTA["ancho"] - VISTA["margen"] * 2
    alto = VISTA["alto"] - VISTA["margen"] * 2
    k = min(
        ancho / ((ENCUADRE["lon1"] - ENCUADRE["lon0"]) * RAD),
        alto / (merc(ENCUADRE["lat1"]) - merc(ENCUADRE["lat0"])),
    )
    x0 = VISTA["margen"] + (ancho - (ENCUADRE["lon1"] - ENCUADRE["lon0"]) * RAD * k) / 2
    y0 = VISTA["margen"] + (alto - (merc(ENCUADRE["lat1"]) - merc(ENCUADRE["lat0"])) * k) / 2
    return {"k": k, "x0": x0, "y0": y0}


PROY = proyeccion()


def xy(lon: float, lat: float) -> tuple[float, float]:
    return (
        PROY["x0"] + (lon - ENCUADRE["lon0"]) * RAD * PROY["k"],
        PROY["y0"] + (merc(ENCUADRE["lat1"]) - merc(lat)) * PROY["k"],
    )


def lonlat(x: float, y: float) -> tuple[float, float]:
    lon = ENCUADRE["lon0"] + (x - PROY["x0"]) / (PROY["k"] * RAD)
    lat = math.degrees(2 * math.atan(math.exp((PROY["y0"] - y) / PROY["k"] + merc(ENCUADRE["lat1"]))) - math.pi / 2)
    return lon, lat


W = math.sqrt(3) * RADIO          # ancho entre centros horizontales
PASO_V = 1.5 * RADIO              # paso vertical entre filas


def centro(fila: int, columna: int) -> tuple[float, float]:
    return (
        VISTA["margen"] + columna * W + (fila % 2) * W / 2,
        VISTA["margen"] + fila * PASO_V,
    )


def celda_de(x: float, y: float) -> tuple[int, int]:
    fila = round((y - VISTA["margen"]) / PASO_V)
    columna = round((x - VISTA["margen"] - (fila % 2) * W / 2) / W)
    return fila, columna


def anillo(cx: float, cy: float) -> list[list[float]]:
    puntos = []
    for i in range(6):
        angulo = math.pi / 180 * (60 * i + 30)  # hexágono con punta arriba
        puntos.append([round(cx + RADIO * math.cos(angulo), 2), round(cy + RADIO * math.sin(angulo), 2)])
    puntos.append(puntos[0])
    return puntos


def descargar(url: str, destino: Path) -> Path:
    if destino.exists():
        return destino
    destino.parent.mkdir(parents=True, exist_ok=True)
    print(f"descargando {destino.name}")
    solicitud = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(solicitud, timeout=240) as origen:
        destino.write_bytes(origen.read())
    return destino


def coordenada(texto: str) -> tuple[float, float] | None:
    if not texto:
        return None
    limpio = texto.replace(" ", "").replace("|", ",").replace(";", ",")
    partes = limpio.split(",")
    if len(partes) != 2:
        return None
    try:
        a, b = float(partes[0]), float(partes[1])
    except ValueError:
        return None
    if abs(a) <= 90 and abs(b) <= 180:
        return b, a  # lat, lon
    if abs(a) <= 180 and abs(b) <= 90:
        return a, b
    return None


def dentro(lon: float, lat: float) -> bool:
    return ENCUADRE["lon0"] <= lon <= ENCUADRE["lon1"] and ENCUADRE["lat0"] <= lat <= ENCUADRE["lat1"]


def leer_mmp(ruta: Path) -> tuple[list[dict], dict]:
    filas = list(csv.DictReader(ruta.open(encoding="utf-8-sig")))
    total = len(filas)
    sin_coordenada = 0
    fuera_ruta = 0
    fuera_encuadre = 0
    invalidas = 0
    seleccion = []
    for fila in filas:
        if fila.get("migration_route") not in RUTAS:
            fuera_ruta += 1
            continue
        par = coordenada(fila.get("location_coodinates", ""))
        if par is None:
            sin_coordenada += 1
            continue
        lon, lat = par
        if not dentro(lon, lat):
            fuera_encuadre += 1
            continue
        try:
            muertos = int(fila.get("number_dead") or 0)
            desaparecidos = int(fila.get("number_missing") or 0)
        except ValueError:
            invalidas += 1
            continue
        fecha = (fila.get("reported_date") or "").strip()[:10]
        if len(fecha) != 10:
            invalidas += 1
            continue
        seleccion.append({
            "lon": lon,
            "lat": lat,
            "anio": fecha[:4],
            "fecha": fecha,
            "muertos": muertos,
            "desaparecidos": desaparecidos,
            "pais": (fila.get("country_of_incident") or "").strip(),
            "ruta": fila.get("migration_route", ""),
            "calidad": (fila.get("source_quality") or "").strip(),
        })
    return seleccion, {
        "filas_csv": total,
        "fuera_de_ruta": fuera_ruta,
        "sin_coordenada": sin_coordenada,
        "fuera_del_encuadre": fuera_encuadre,
        "invalidas": invalidas,
        "seleccionadas": len(seleccion),
    }


def principales(valores: list[str], limite: int = 4) -> list[str]:
    conteo = defaultdict(int)
    for valor in valores:
        if valor:
            conteo[valor] += 1
    return [v for v, _ in sorted(conteo.items(), key=lambda kv: (-kv[1], kv[0]))[:limite]]


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera la malla hexagonal de muertes y desapariciones.")
    parser.add_argument(
        "--insumos",
        type=Path,
        default=INSUMOS,
        help="carpeta con los insumos excluidos (por defecto: pipeline/insumos_fuente)",
    )
    parser.add_argument("--csv", type=Path, default=None, help="CSV de OIM MMP")
    parser.add_argument("--admin1", type=Path, default=None, help="ZIP admin-1 de Natural Earth")
    parser.add_argument("--sin-estados", action="store_true")
    args = parser.parse_args()
    if args.csv is None:
        args.csv = args.insumos / "mmp.csv"
    if args.admin1 is None:
        args.admin1 = args.insumos / "ne_10m_admin_1_states_provinces.zip"
    if not (args.insumos / "ne_50m_admin_0_countries.geojson").exists():
        raise SystemExit(
            f"falta {args.insumos / 'ne_50m_admin_0_countries.geojson'}\n"
            "  ejecuta antes `python pipeline/preparar_cartografia.py` o descarga"
            " Natural Earth 50m en la carpeta de insumos (--insumos o"
            " MIGRATION_SOURCE_DIR); ver pipeline/README.md."
        )
    GEOGRAFIA.mkdir(parents=True, exist_ok=True)

    csv_ruta = args.csv if args.csv.exists() else descargar(URL_MMP, args.csv)
    registros, exclusiones = leer_mmp(csv_ruta)

    mundo = gpd.read_file(args.insumos / "ne_50m_admin_0_countries.geojson")
    contexto = mundo.cx[ENCUADRE["lon0"]:ENCUADRE["lon1"], ENCUADRE["lat0"]:ENCUADRE["lat1"]].copy()
    contexto["geometry"] = contexto.geometry.simplify(0.02, preserve_topology=True)
    paises_hex = {
        "type": "FeatureCollection",
        "metadata": {
            "fuente": "Natural Earth · Admin 0 Countries (50m)",
            "licencia": "dominio público",
            "transformacion": "recorte al encuadre y simplificación 0,02°, EPSG:4326",
        },
        "features": [
            {
                "type": "Feature",
                "geometry": mapping(fila.geometry),
                "properties": {"nombre": fila["NAME"], "iso": fila.get("ISO_A3") or ""},
            }
            for _, fila in contexto.iterrows()
        ],
    }
    (GEOGRAFIA / "paises_hex.geojson").write_text(
        json.dumps(paises_hex, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    tierras = [prep(geometria) for geometria in contexto.geometry]

    filas = int((VISTA["alto"] - VISTA["margen"] * 2) / PASO_V) + 2
    columnas = int((VISTA["ancho"] - VISTA["margen"] * 2) / W) + 2

    celdas: dict[tuple[int, int], dict] = {}
    for fila in range(filas):
        for columna in range(columnas):
            cx, cy = centro(fila, columna)
            if not (0 <= cx <= VISTA["ancho"] and 0 <= cy <= VISTA["alto"]):
                continue
            lon, lat = lonlat(cx, cy)
            if not any(t.covers(Point(lon, lat)) for t in tierras):
                continue
            celdas[(fila, columna)] = {
                "i": f"h{fila}-{columna}",
                "cx": round(cx, 2),
                "cy": round(cy, 2),
                "lon": round(lon, 4),
                "lat": round(lat, 4),
                "muertes": [0, 0, 0, 0],      # n, personas, n_missing, missing? (se separa abajo)
                "desapariciones": [0, 0],
                "anios": defaultdict(lambda: [0, 0, 0, 0]),
                "paises": [],
                "rutas": [],
                "calidades": [],
                "fechas": [],
            }

    sin_celda = 0
    asignado = {"muertes": {"incidentes": 0, "personas": 0}, "desapariciones": {"incidentes": 0, "personas": 0}}
    centros_tierra = [(clave, c["lon"], c["lat"]) for clave, c in celdas.items()]

    def celda_mas_cercana(lon: float, lat: float):
        mejor = None
        mejor_d = DISTANCIA_MAXIMA
        coslat = math.cos(math.radians(lat))
        for clave, clon, clat in centros_tierra:
            dx = (lon - clon) * coslat
            dy = lat - clat
            distancia = math.hypot(dx, dy)
            if distancia < mejor_d:
                mejor_d = distancia
                mejor = clave
        return mejor

    for registro in registros:
        x, y = xy(registro["lon"], registro["lat"])
        fila, columna = celda_de(x, y)
        celda = celdas.get((fila, columna))
        if celda is None:
            clave = celda_mas_cercana(registro["lon"], registro["lat"])
            celda = celdas.get(clave) if clave else None
        if celda is None:
            sin_celda += 1
            continue
        anio = registro["anio"]
        muertos = registro["muertos"]
        desaparecidos = registro["desaparecidos"]
        celda["paises"].append(registro["pais"])
        celda["rutas"].append(registro["ruta"])
        celda["calidades"].append(registro["calidad"])
        celda["fechas"].append(registro["fecha"])
        if muertos > 0:
            celda["muertes"][0] += 1
            celda["muertes"][1] += muertos
            celda["anios"][anio][0] += 1
            celda["anios"][anio][1] += muertos
            asignado["muertes"]["incidentes"] += 1
            asignado["muertes"]["personas"] += muertos
        if desaparecidos > 0:
            celda["desapariciones"][0] += 1
            celda["desapariciones"][1] += desaparecidos
            celda["anios"][anio][2] += 1
            celda["anios"][anio][3] += desaparecidos
            asignado["desapariciones"]["incidentes"] += 1
            asignado["desapariciones"]["personas"] += desaparecidos

    # ICIJ/CLIP: se agrega con la misma malla para la capa contextual.
    icij = json.loads((WEB / "fuentes_ampliadas.json").read_text(encoding="utf-8"))["icij_clip"]["points"]
    for punto in icij:
        if "lat" not in punto or "lon" not in punto:
            continue
        x, y = xy(punto["lon"], punto["lat"])
        fila, columna = celda_de(x, y)
        celda = celdas.get((fila, columna))
        if celda is None:
            clave = celda_mas_cercana(punto["lon"], punto["lat"])
            celda = celdas.get(clave) if clave else None
        if celda is not None:
            celda.setdefault("icij", 0)
            celda["icij"] += 1

    features = []
    total = {"muertes": {"incidentes": 0, "personas": 0}, "desapariciones": {"incidentes": 0, "personas": 0}}
    por_anio = defaultdict(lambda: {"m_inc": 0, "m_per": 0, "d_inc": 0, "d_per": 0})
    con_datos = 0
    for (fila, columna), celda in sorted(celdas.items()):
        nm, pm, nd, pd_ = celda["muertes"][0], celda["muertes"][1], celda["desapariciones"][0], celda["desapariciones"][1]
        icij_celda = celda.get("icij", 0)
        if nm == 0 and nd == 0 and icij_celda == 0:
            features.append({
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [anillo(celda["cx"], celda["cy"])]},
                "properties": {"i": celda["i"], "c": [celda["lon"], celda["lat"]]},
            })
            continue
        con_datos += 1
        propiedades = {"i": celda["i"], "c": [celda["lon"], celda["lat"]]}
        if nm or nd:
            anios = {}
            for anio, valores in sorted(celda["anios"].items()):
                if any(valores):
                    anios[anio] = valores
            propiedades.update({
                "m": [nm, pm],
                "d": [nd, pd_],
                "y": anios,
                "f": [min(celda["fechas"]), max(celda["fechas"])],
                "p": principales(celda["paises"]),
                "r": principales(celda["rutas"]),
                "q": principales(celda["calidades"]),
            })
            total["muertes"]["incidentes"] += nm
            total["muertes"]["personas"] += pm
            total["desapariciones"]["incidentes"] += nd
            total["desapariciones"]["personas"] += pd_
            for anio, valores in anios.items():
                por_anio[anio]["m_inc"] += valores[0]
                por_anio[anio]["m_per"] += valores[1]
                por_anio[anio]["d_inc"] += valores[2]
                por_anio[anio]["d_per"] += valores[3]
        if icij_celda:
            propiedades["x"] = icij_celda
        features.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [anillo(celda["cx"], celda["cy"])]},
            "properties": propiedades,
        })

    coleccion = {
        "type": "FeatureCollection",
        "metadata": {
            "titulo": "Muertes y desapariciones documentadas · malla hexagonal",
            "resumen": "Celdas hexagonales sobre México, Centroamérica y la frontera sur de EE. UU. Cada celda suma registros de la OIM (MMP) con coordenadas dentro del encuadre. Un hexágono con dato no es una ubicación exacta de cada incidente.",
            "encuadre": ENCUADRE,
            "vista": VISTA,
            "radio": RADIO,
            "ancho_centros": round(W, 3),
            "paso_vertical": round(PASO_V, 3),
            "proyeccion": "Mercator propia, misma fórmula del mapa de la vista Panorama",
            "geometria_base": "Natural Earth Admin 0 (50m), dominio público",
        },
        "features": features,
    }

    total_registros = {"muertes": {"incidentes": 0, "personas": 0}, "desapariciones": {"incidentes": 0, "personas": 0}}
    for registro in registros:
        if registro["muertos"] > 0:
            total_registros["muertes"]["incidentes"] += 1
            total_registros["muertes"]["personas"] += registro["muertos"]
        if registro["desaparecidos"] > 0:
            total_registros["desapariciones"]["incidentes"] += 1
            total_registros["desapariciones"]["personas"] += registro["desaparecidos"]

    anios_disponibles = sorted({r["anio"] for r in registros})
    metadatos = {
        "estado": "disponible",
        "titulo": "Malla hexagonal · OIM Missing Migrants Project",
        "geometria": "hexbin_muertes.geojson",
        "fuente": {
            "nombre": "Missing Migrants Project",
            "organismo": "Organización Internacional para las Migraciones (OIM)",
            "url": "https://missingmigrants.iom.int/downloads",
            "url_descarga": URL_MMP,
            "licencia": "CC BY-IGO (Creative Commons Attribution for Intergovernmental Organisations 3.0 IGO)",
            "licencia_url": "https://creativecommons.org/licenses/by/3.0/igo/",
            "atribucion": "OIM · Missing Migrants Project",
            "descargado": CORTE_DESCARGA,
            "csv_sha256": hashlib.sha256(csv_ruta.read_bytes()).hexdigest(),
            "campo_fecha": "reported_date",
            "semantica_fecha": "fecha reportada por MMP; no es necesariamente la fecha de la muerte",
        },
        "universo": {
            "rutas": RUTAS,
            "encuadre": ENCUADRE,
            "definicion_muertes": "filas con number_dead > 0",
            "definicion_desapariciones": "filas con number_missing > 0",
            "nota_universos": "Muertes y desapariciones son dos subconjuntos de la misma base; no se suman entre sí ni con el agregado del EAAF.",
        },
        "resumen": {
            "celdas_totales": len(features),
            "celdas_con_datos": con_datos,
            "registros_seleccionados": exclusiones["seleccionadas"],
            "registros_sin_celda": sin_celda,
            "muertes": asignado["muertes"],
            "desapariciones": asignado["desapariciones"],
            "anios": anios_disponibles,
            "por_anio": dict(sorted(por_anio.items())),
        },
        "comprobacion": {
            "suma_celdas_muertes": total["muertes"],
            "suma_celdas_desapariciones": total["desapariciones"],
            "coincide": total == asignado,
            "registros_sin_celda": sin_celda,
        },
        "exclusiones": exclusiones,
        "preparacion": {
            "crs": "EPSG:4326 para los centros; malla proyectada con Mercator",
            "transformaciones": "sin reproyección externa; coordenadas del CSV tal como las publica la fuente, filtradas al encuadre",
            "malla": f"hexágonos de radio {RADIO} unidades, {len(features)} celdas terrestres",
        },
        "sha256": "",
    }

    texto = json.dumps(coleccion, ensure_ascii=False, separators=(",", ":"))
    destino = GEOGRAFIA / "hexbin_muertes.geojson"
    destino.write_text(texto, encoding="utf-8")
    metadatos["sha256"] = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    metadatos["bytes"] = len(texto.encode("utf-8"))
    (GEOGRAFIA / "hexbin_muertes.json").write_text(
        json.dumps(metadatos, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if not args.sin_estados:
        admin1 = args.admin1 if args.admin1.exists() else descargar(URL_ADMIN1, args.admin1)
        gdf = gpd.read_file(f"zip://{admin1}")
        mexico = gdf[gdf["admin"] == "Mexico"] if "admin" in gdf.columns else gdf[gdf["adm0_a3"] == "MEX"]
        estados = {
            "type": "FeatureCollection",
            "metadata": {
                "fuente": "Natural Earth · Admin 1 States/Provinces (10m)",
                "licencia": "dominio público",
                "transformacion": "simplificado a 0,02°, EPSG:4326",
            },
            "features": [
                {
                    "type": "Feature",
                    "geometry": mapping(fila.geometry.simplify(0.02, preserve_topology=True)),
                    "properties": {"nombre": fila["name"], "iso": fila.get("iso_3166_2") or ""},
                }
                for _, fila in mexico.iterrows()
                if isinstance(fila["name"], str) and fila["name"]
            ],
        }
        texto_estados = json.dumps(estados, ensure_ascii=False, separators=(",", ":"))
        (GEOGRAFIA / "estados_mexico.geojson").write_text(texto_estados, encoding="utf-8")
        print(f"estados: {len(estados['features'])} · {len(texto_estados.encode('utf-8'))} bytes")

    print(f"celdas: {len(features)} ({con_datos} con datos)")
    print(f"muertes: {total_registros['muertes']} · desapariciones: {total_registros['desapariciones']}")
    print(f"coincide: {metadatos['comprobacion']['coincide']} · sin celda: {sin_celda}")
    print(f"bytes: {metadatos['bytes']} · sha256: {metadatos['sha256'][:16]}…")
    print(f"exclusiones: {exclusiones}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
