"""Contrato de datos del tablero «Vidas en tránsito».

Estas pruebas no miden visualizaciones: verifican que los archivos publicados
conserven las invariantes que la interfaz y la documentación dan por ciertas, y
que el repositorio **no redistribuya** los insumos crudos de las fuentes.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

WEB = Path(__file__).resolve().parents[1] / "web"
GEO = WEB / "geografia"

#: Nombres de campo que indicarían microdatos de personas.
CAMPOS_PERSONALES = {
    "nombre",
    "nombres",
    "apellido",
    "apellidos",
    "nombre_completo",
    "curp",
    "rfc",
    "domicilio",
    "telefono",
    "fecha_nacimiento",
    "correo",
    "email",
}


def cargar(nombre: str) -> dict:
    return json.loads((WEB / nombre).read_text(encoding="utf-8"))


def claves(objeto, acumulado: set[str] | None = None) -> set[str]:
    """Recorre el JSON y reúne todas las claves de objeto."""
    if acumulado is None:
        acumulado = set()
    if isinstance(objeto, dict):
        for clave, valor in objeto.items():
            acumulado.add(str(clave))
            claves(valor, acumulado)
    elif isinstance(objeto, list):
        for elemento in objeto:
            claves(elemento, acumulado)
    return acumulado


def test_datos_conservan_advertencia_y_estado() -> None:
    datos = cargar("data.json")
    for campo in (
        "generated_at",
        "prototype_status",
        "warning",
        "sources",
        "redodem",
        "map_status",
        "eventos_migratorios",
        "devoluciones",
        "eaaf_public_detail",
    ):
        assert campo in datos, f"falta el campo {campo}"
    assert datos["warning"].strip(), "la advertencia de lectura no puede estar vacía"


def test_redodem_declara_su_unidad_de_observacion() -> None:
    datos = cargar("data.json")
    redodem = datos["redodem"]
    texto = json.dumps(redodem, ensure_ascii=False).lower()
    # La unidad es la fila de atención, no la persona única.
    assert "redodem" in texto
    assert any(
        palabra in texto for palabra in ("fila", "registro", "atención", "atencion")
    ), "el bloque REDODEM debe declarar que la unidad es la fila de atención"


def test_ningun_archivo_publica_campos_personales() -> None:
    for nombre in ("data.json", "fuentes_ampliadas.json"):
        encontradas = {clave.lower() for clave in claves(cargar(nombre))}
        intrusas = encontradas & CAMPOS_PERSONALES
        assert not intrusas, f"{nombre} expone campos personales: {sorted(intrusas)}"


def test_geografia_son_colecciones_validas() -> None:
    archivos = sorted(GEO.glob("*.geojson"))
    assert archivos, "no hay capas geográficas publicadas"
    for archivo in archivos:
        capa = json.loads(archivo.read_text(encoding="utf-8"))
        assert capa.get("type") == "FeatureCollection", archivo.name
        assert isinstance(capa.get("features"), list), archivo.name


def test_fuentes_ampliadas_conservan_cortes_y_bloques() -> None:
    fuentes = cargar("fuentes_ampliadas.json")
    assert fuentes.get("source_cutoffs"), "faltan los cortes de fuente"
    for bloque in ("upmrip", "icij_clip", "iom_shelters", "diagnostics"):
        assert bloque in fuentes, f"falta el bloque {bloque}"


def test_insumos_crudos_no_se_redistribuyen() -> None:
    """El proyecto declara que no redistribuye XLS ni CSV de origen."""
    repo = Path(__file__).resolve().parents[1]
    assert not (repo / "insumos_fuente").exists(), (
        "insumos_fuente/ no debe versionarse: los datos crudos se descargan aparte"
    )
    for patron in ("*.xls", "*.xlsx", "*.csv", "*.zip"):
        sobrantes = [p.name for p in repo.rglob(patron) if ".git" not in p.parts]
        assert not sobrantes, f"archivos crudos versionados: {sobrantes}"


@pytest.mark.parametrize("nombre", ["data.json", "fuentes_ampliadas.json"])
def test_los_json_publicados_son_serializables(nombre: str) -> None:
    assert json.dumps(cargar(nombre), ensure_ascii=False)
