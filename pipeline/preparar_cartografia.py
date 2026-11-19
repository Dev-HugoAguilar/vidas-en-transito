# -*- coding: utf-8 -*-
"""Prepara la cartografía local del bloque «Cartografía de evidencia».

Genera, a partir de fuentes verificables y sin servicios en tiempo de ejecución:

- `geografia/paises.geojson`: límites reales de México, Centroamérica y el sur de
  Estados Unidos (Natural Earth 50m, dominio público), recortados a la ventana del
  corredor y simplificados.
- `geografia/corredor.geojson`: corredor centroamericano **generalizado** por
  países, construido con puntos representativos reales de cada país en la secuencia
  que describe OIM DTM (Panamá → Costa Rica → Nicaragua → Honduras → Guatemala →
  México). No es una línea GPS ni una ruta exacta.
- `geografia/ferroviaria.json`: estado de la capa ferroviaria oficial. La geometría
  del SHP de ATTRAPI aún no está incorporada: el intento de descarga registrado
  respondió HTTP 403. Se documentan el intento, la licencia, la fecha de
  actualización y el enlace, y **no se inventa geometría**.

Uso:
    python -X utf8 pipeline/preparar_cartografia.py
    python -X utf8 pipeline/preparar_cartografia.py --insumos RUTA

Escribe en `web/geografia/`, el runtime publicado, e insumos que no se versionan
en la carpeta indicada por `--insumos` o MIGRATION_SOURCE_DIR (por defecto,
`pipeline/insumos_fuente/`).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import urllib.request
from pathlib import Path

import geopandas as gpd
from shapely.geometry import box
from shapely.ops import unary_union

_parser = argparse.ArgumentParser(description="Prepara la cartografía local del tablero.")
_parser.add_argument(
    "--insumos",
    type=Path,
    default=Path(os.environ.get("MIGRATION_SOURCE_DIR", Path(__file__).resolve().parents[1] / "pipeline" / "insumos_fuente")),
    help="carpeta con los insumos excluidos (por defecto: pipeline/insumos_fuente)",
)
ARGS, _ = _parser.parse_known_args()

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "web" / "geografia"
SALIDA.mkdir(parents=True, exist_ok=True)
INSUMOS = ARGS.insumos
INSUMOS.mkdir(parents=True, exist_ok=True)

NE_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson"
VENTANA = (-118.5, 4.5, -75.0, 34.5)

PAISES = {
    "USA": "Estados Unidos",
    "MEX": "México",
    "GTM": "Guatemala",
    "BLZ": "Belice",
    "HND": "Honduras",
    "SLV": "El Salvador",
    "NIC": "Nicaragua",
    "CRI": "Costa Rica",
    "PAN": "Panamá",
    "CUB": "Cuba",
}
CORREDOR = ["PAN", "CRI", "NIC", "HND", "GTM", "MEX"]
# Ventanas sobre el eje del corredor: el punto de cada país se toma de la parte
# sur (la entrada del tránsito hacia el norte), no del centro geométrico del país.
ANCLAS = {
    "PAN": (-80.6, 7.4, -77.2, 9.6),
    "CRI": (-85.2, 8.0, -82.4, 10.6),
    "NIC": (-86.6, 10.7, -83.6, 13.1),
    "HND": (-88.6, 12.8, -84.9, 15.1),
    "GTM": (-92.3, 13.6, -88.1, 16.1),
    "MEX": (-93.6, 14.2, -90.3, 17.2),
}


def descargar(url: str, destino: Path) -> bytes:
    if destino.exists():
        return destino.read_bytes()
    peticion = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) portafolio-hugo/1.0"}
    )
    datos = urllib.request.urlopen(peticion, timeout=180).read()
    destino.write_bytes(datos)
    return datos


crudo = INSUMOS / "ne_50m_admin_0_countries.geojson"
datos = descargar(NE_URL, crudo)
print("Natural Earth:", f"{len(datos):,} bytes", "sha256", hashlib.sha256(datos).hexdigest()[:16])

mundo = gpd.read_file(crudo)
columna_iso = "ISO_A3" if "ISO_A3" in mundo.columns else "ADM0_A3"
mundo[columna_iso] = mundo[columna_iso].replace("-99", None)
seleccion = mundo[mundo[columna_iso].isin(PAISES.keys())].to_crs(4326)
ventana = box(*VENTANA)


def solo_poligonos(geometria):
    if geometria.is_empty:
        return geometria
    if geometria.geom_type in ("Polygon", "MultiPolygon"):
        return geometria
    partes = [g for g in getattr(geometria, "geoms", []) if g.geom_type in ("Polygon", "MultiPolygon")]
    return unary_union(partes) if partes else geometria


def redondear(objeto, decimales=4):
    if isinstance(objeto, float):
        return round(objeto, decimales)
    if isinstance(objeto, (list, tuple)):
        return [redondear(v, decimales) for v in objeto]
    if isinstance(objeto, dict):
        return {k: redondear(v, decimales) for k, v in objeto.items()}
    return objeto


recortados, centros = [], {}
for _, fila in seleccion.iterrows():
    iso = fila[columna_iso]
    geometria = fila.geometry
    if geometria is None or geometria.is_empty or not geometria.intersects(ventana):
        continue
    recortado = solo_poligonos(geometria.intersection(ventana).buffer(0))
    if recortado.is_empty:
        continue
    recortados.append(
        {
            "type": "Feature",
            "properties": {"iso": iso, "nombre": PAISES[iso]},
            "geometry": json.loads(json.dumps(recortado.__geo_interface__)),
        }
    )
    ventana_ancla = box(*ANCLAS[iso]) if iso in ANCLAS else None
    base_punto = recortado.intersection(ventana_ancla) if ventana_ancla else recortado
    if base_punto.is_empty:
        base_punto = recortado
    punto = base_punto.representative_point()
    centros[iso] = (round(float(punto.x), 4), round(float(punto.y), 4))

geografia = {
    "type": "FeatureCollection",
    "fuente": {
        "nombre": "Natural Earth · Admin 0 Countries (50m)",
        "url": NE_URL,
        "licencia": "Dominio público (Natural Earth)",
        "procesamiento": f"recorte a {VENTANA} y simplificación 0,02° con shapely; EPSG:4326",
        "sha256_descarga": hashlib.sha256(datos).hexdigest(),
    },
    "features": redondear(recortados),
}
(SALIDA / "paises.geojson").write_text(
    json.dumps(geografia, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
)
print("paises.geojson:", len(recortados), "países ·", (SALIDA / "paises.geojson").stat().st_size, "bytes")

tramos = []
for origen, destino in zip(CORREDOR, CORREDOR[1:]):
    x0, y0 = centros[origen]
    x1, y1 = centros[destino]
    tramos.append(
        {
            "type": "Feature",
            "properties": {
                "orden": len(tramos) + 1,
                "desde": PAISES[origen],
                "hasta": PAISES[destino],
                "iso_desde": origen,
                "iso_hasta": destino,
                "precision": "tramo generalizado entre centros de país; no es un camino ni una ruta GPS",
                "fuente": "OIM DTM · portal de rutas para las Américas",
                "url": "https://dtm.iom.int/es/global-overview-of-migration-routes-portal/americas",
                "corte": "abril de 2026",
            },
            "geometry": {"type": "LineString", "coordinates": [[x0, y0], [x1, y1]]},
        }
    )

corredor = {
    "type": "FeatureCollection",
    "aviso": "Representación generalizada por países; la fuente describe las rutas principales para las que tiene datos y no es exhaustiva.",
    "secuencia": [PAISES[iso] for iso in CORREDOR],
    "centros": [
        {"iso": iso, "nombre": PAISES[iso], "lon": centros[iso][0], "lat": centros[iso][1]}
        for iso in CORREDOR
    ],
    "features": tramos,
}
(SALIDA / "corredor.geojson").write_text(
    json.dumps(corredor, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
)
print("corredor.geojson:", len(tramos), "tramos ·", (SALIDA / "corredor.geojson").stat().st_size, "bytes")
for iso in CORREDOR:
    print(f"   {iso}: {centros[iso]}")

ferroviaria = {
    "estado": "pendiente",
    "titulo": "Red Ferroviaria Nacional · infraestructura física · ATTRAPI",
    "fuente": {
        "nombre": "Red Ferroviaria Nacional ATTRAPI — recurso «Vía férrea, 2025»",
        "organismo": "Agencia de Trenes y Transporte Público Integrado (ATTRAPI)",
        "url_ficha": "https://www.datos.gob.mx/es/dataset/red_ferroviaria_nacional_attrapi",
        "url_recurso": "https://www.datos.gob.mx/es/dataset/red_ferroviaria_nacional_attrapi/resource/538041af-450d-4b25-9b67-67c187a7d57f",
        "url_descarga": "https://repodatos.atdt.gob.mx/api_update/attrapi/red_ferroviaria_nacional_attrapi/01_via_ferrea.zip",
        "formato": "SHP",
        "licencia": "Creative Commons Attribution 4.0 (CC BY 4.0)",
        "licencia_url": "https://creativecommons.org/licenses/by/4.0/",
        "actualizacion_datos": "16 de abril de 2026",
        "frecuencia": "anual",
        "contenido": "representación lineal de los tramos de vías principales, auxiliares e industriales de la Red Ferroviaria Nacional",
    },
    "motivo": "La geometría oficial aún no está incorporada al mapa. El intento de descarga directa registrado respondió HTTP 403 «Access Denied» (Akamai). Se reintentará la descarga y, cuando el archivo se obtenga y valide, se publicará la capa. No se sustituyó por una geometría dibujada o de procedencia incierta.",
    "intentos": [
        "curl y urllib al ZIP oficial: HTTP 403 (Akamai: Access Denied)",
        "navegador automatizado (Playwright) sobre la ficha del recurso: sin descarga",
        "fetch desde el contexto de la página: bloqueado por el CDN",
        "búsqueda de un servicio FeatureServer publicado por ATTRAPI: sin resultados",
    ],
    "pendiente": "Descargar el SHP cuando el CDN permita el acceso, validar CRS, campos y validez, transformar a EPSG:4326, simplificar y publicar como capa propia.",
}
(SALIDA / "ferroviaria.json").write_text(
    json.dumps(ferroviaria, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print("ferroviaria.json: capa pendiente documentada")

