# -*- coding: utf-8 -*-
"""Publica «Vidas en tránsito» copiando el runtime `web/` y verificando hashes.

Copia `web/` (la aplicación publicada, con `geografia/`) a `dist/` comprobando
cada hash contra `docs/MANIFEST_LOCAL.json`. Lo publicado es exactamente lo que
hay en el origen: no hay dos copias divergentes.

Todas las rutas se resuelven desde este archivo, no desde el directorio actual ni
desde una ruta del monorepo donde se armó el tablero:

- raíz del clon: `Path(__file__).resolve().parents[1]`
- runtime: `web/`
- manifiesto: `docs/MANIFEST_LOCAL.json`
- salida: `dist/` (ignorada por git)

No ejecuta `derive_data.py` ni los `preparar_*.py`: la derivación de datos y la
preparación cartográfica se hacen fuera del build (ver `pipeline/README.md`,
`docs/FUENTES_Y_LIMITES.md` y `docs/CARTOGRAFIA.md`); el navegador solo carga
archivos locales.

Uso:
    python pipeline/construir.py
    python pipeline/construir.py --comprobar
    python pipeline/construir.py --salida RUTA_DENTRO_DEL_CLON
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RUNTIME = RAIZ / "web"
MANIFIESTO = RAIZ / "docs" / "MANIFEST_LOCAL.json"
SALIDA_POR_DEFECTO = RAIZ / "dist"


def hash_de(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def dentro_del_clon(ruta: Path, etiqueta: str) -> Path:
    """Resuelve la ruta y falla si queda fuera del clon."""
    resuelta = ruta.resolve()
    if resuelta != RAIZ and RAIZ not in resuelta.parents:
        raise SystemExit(
            f"{etiqueta} queda fuera del clon: {resuelta}\n"
            f"  el build solo escribe dentro de {RAIZ}"
        )
    return resuelta


def relativa(ruta: Path) -> str:
    try:
        return ruta.relative_to(RAIZ).as_posix()
    except ValueError:
        return str(ruta)


def principal(argumentos: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publica el tablero verificando hashes.")
    parser.add_argument(
        "--comprobar",
        action="store_true",
        help="no copia: comprueba que lo publicado coincide con web/ y el manifiesto",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=SALIDA_POR_DEFECTO,
        help="carpeta de publicación dentro del clon (por defecto: dist/)",
    )
    args = parser.parse_args(argumentos)

    if not MANIFIESTO.is_file():
        raise SystemExit(
            f"falta el manifiesto publicado: {relativa(MANIFIESTO)}\n"
            "  se espera docs/MANIFEST_LOCAL.json dentro del clon; no se busca en"
            " la ruta del monorepo."
        )
    if not RUNTIME.is_dir():
        raise SystemExit(
            f"falta el runtime publicado: {relativa(RUNTIME)}/\n"
            "  se espera la carpeta web/ del clon (la aplicación servible), no"
            " pipeline/runtime."
        )

    destino = dentro_del_clon(args.salida, "la carpeta de publicación")
    origen = dentro_del_clon(RUNTIME, "el runtime")
    manifiesto = dentro_del_clon(MANIFIESTO, "el manifiesto")

    contenido = json.loads(manifiesto.read_text(encoding="utf-8"))
    esperados = {f["path"]: f["sha256"] for f in contenido["files"]}

    for relativo, digest in esperados.items():
        archivo = origen / relativo
        if not archivo.is_file():
            raise SystemExit(f"falta {relativa(origen)}/{relativo}")
        if hash_de(archivo) != digest:
            raise SystemExit(f"{relativa(origen)}/{relativo} no coincide con el MANIFEST_LOCAL")

    if args.comprobar:
        if not destino.is_dir():
            raise SystemExit(
                f"no hay build publicado en {relativa(destino)}/:"
                " ejecuta `python pipeline/construir.py` primero"
            )
        for relativo, digest in esperados.items():
            publicado = destino / relativo
            if not publicado.is_file() or hash_de(publicado) != digest:
                raise SystemExit(f"{relativa(destino)}/{relativo} no coincide con el origen")
        print(f"vidas-en-transito: build íntegro ({len(esperados)} archivos)")
        return 0

    for relativo in esperados:
        archivo_destino = destino / relativo
        archivo_destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(origen / relativo, archivo_destino)
        if hash_de(archivo_destino) != esperados[relativo]:
            raise SystemExit(f"la copia de {relativo} no coincide")

    total = sum((destino / r).stat().st_size for r in esperados)
    print(
        f"publicado: {relativa(destino)} ·",
        f"{len(esperados)} archivos ·",
        f"{total:,} bytes ·",
        hashlib.sha256((destino / "index.html").read_bytes()).hexdigest()[:16] + "…",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
