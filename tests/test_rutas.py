"""Contrato de rutas del pipeline.

Estas pruebas fijan que `pipeline/` funciona desde un clon del repositorio: la
raíz se deriva de `Path(__file__).resolve().parents[1]`, el runtime publicado es
`web/`, el manifiesto está en `docs/MANIFEST_LOCAL.json` y ninguna ruta resuelta
sale del clon ni apunta al monorepo donde se armó el tablero.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
PIPELINE = RAIZ / "pipeline"


def cargar(nombre: str):
    """Importa un script de `pipeline/` sin exigir que sea un paquete."""
    ruta = PIPELINE / nombre
    especificacion = importlib.util.spec_from_file_location(f"pipeline_{ruta.stem}", ruta)
    assert especificacion and especificacion.loader
    modulo = importlib.util.module_from_spec(especificacion)
    especificacion.loader.exec_module(modulo)
    return modulo


def test_construir_resuelve_el_runtime_y_el_manifiesto_dentro_del_clon() -> None:
    construir = cargar("construir.py")

    assert construir.RAIZ == RAIZ, "la raíz debe derivarse de parents[1] de este archivo"
    assert construir.RUNTIME == RAIZ / "web", "el runtime publicado es web/"
    assert construir.MANIFIESTO == RAIZ / "docs" / "MANIFEST_LOCAL.json"
    assert construir.SALIDA_POR_DEFECTO == RAIZ / "dist"

    for ruta in (construir.RUNTIME, construir.MANIFIESTO, construir.SALIDA_POR_DEFECTO):
        resuelta = ruta.resolve()
        assert resuelta == RAIZ or RAIZ in resuelta.parents, f"{ruta} sale del clon"

    assert construir.MANIFIESTO.is_file(), "el manifiesto publicado debe existir en el clon"
    assert construir.RUNTIME.is_dir(), "el runtime publicado debe existir en el clon"


def test_construir_falla_con_mensaje_claro_si_falta_el_manifiesto(monkeypatch, capsys) -> None:
    construir = cargar("construir.py")
    monkeypatch.setattr(construir, "MANIFIESTO", RAIZ / "docs" / "NO_EXISTE.json")

    with pytest.raises(SystemExit) as salida:
        construir.principal([])

    texto = str(salida.value)
    assert "manifiesto" in texto
    assert "FileNotFoundError" not in texto
    assert "Traceback" not in capsys.readouterr().err


def test_construir_rechaza_una_salida_fuera_del_clon(tmp_path) -> None:
    construir = cargar("construir.py")
    fuera = tmp_path / "dist"

    with pytest.raises(SystemExit) as salida:
        construir.principal(["--salida", str(fuera)])

    assert "fuera del clon" in str(salida.value)


def test_redodem_apunta_al_runtime_y_a_los_insumos_del_clon() -> None:
    redodem = cargar("preparar_redodem.py")

    assert redodem.DATA_DEFECTO == RAIZ / "web" / "data.json"
    assert redodem.DATA_DEFECTO.is_file(), "web/data.json debe existir en el clon"
    assert redodem.INSUMOS_POR_DEFECTO == RAIZ / "pipeline" / "insumos_fuente"
    assert redodem.CSV_DEFECTO.parent == redodem.INSUMOS_POR_DEFECTO
    for ruta in (redodem.DATA_DEFECTO, redodem.INSUMOS_POR_DEFECTO):
        resuelta = ruta.resolve()
        assert resuelta == RAIZ or RAIZ in resuelta.parents, f"{ruta} sale del clon"


def test_redodem_falla_con_mensaje_claro_si_faltan_insumos(monkeypatch, tmp_path) -> None:
    redodem = cargar("preparar_redodem.py")
    vacia = tmp_path / "insumos"
    vacia.mkdir()

    monkeypatch.setattr("sys.argv", ["preparar_redodem.py", "--insumos", str(vacia)])
    with pytest.raises(SystemExit) as salida:
        redodem.main()

    texto = str(salida.value)
    assert "falta el CSV" in texto
    assert "--insumos" in texto
    assert "FileNotFoundError" not in texto


def test_ningun_script_del_pipeline_usa_rutas_del_monorepo() -> None:
    prohibidas = ("dashboards/", "parents[3]", "parents[2]", 'AQUI / "runtime"', 'BASE / "runtime"')
    for script in sorted(PIPELINE.glob("*.py")):
        texto = script.read_text(encoding="utf-8")
        for prohibida in prohibidas:
            assert prohibida not in texto, f"{script.name} conserva una ruta del monorepo: {prohibida}"


def test_los_scripts_derivan_la_raiz_de_su_propia_ruta() -> None:
    patron = re.compile(r"^(RAIZ|BASE)\s*=\s*Path\(__file__\)\.resolve\(\)\.parents\[1\]", re.M)
    for script in sorted(PIPELINE.glob("*.py")):
        if script.name.endswith("derive_data.py"):
            continue  # usa BASE/RAIZ en dos líneas cortas
        texto = script.read_text(encoding="utf-8")
        assert patron.search(texto), f"{script.name} no deriva la raíz de su propia ruta"
