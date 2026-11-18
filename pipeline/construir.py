# -*- coding: utf-8 -*-
"""Publica «Vidas en tránsito» en el sitio.

Copia `runtime/` (los tres archivos de la aplicación y la carpeta `geografia/`) a
`dist/dashboards/vidas-en-transito/` verificando cada hash contra
`MANIFEST_LOCAL.json`. Lo publicado es exactamente lo que hay en el origen: no hay
dos copias divergentes.

No ejecuta `derive_data.py` ni `preparar_cartografia.py`: la derivación de datos y
la preparación cartográfica se hacen fuera del sitio (ver `LEEME.md`,
`FUENTES_Y_LIMITES.md` y `CARTOGRAFIA.md`); el navegador solo carga archivos locales.

Uso: python dashboards/vidas-en-transito/construir.py [--comprobar]
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parents[1]
DESTINO = REPO / "dist" / "dashboards" / "vidas-en-transito"
RUNTIME = AQUI / "runtime"


def hash_de(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def principal() -> int:
    manifiesto = json.loads((AQUI / "MANIFEST_LOCAL.json").read_text(encoding="utf-8"))
    esperados = {f["path"]: f["sha256"] for f in manifiesto["files"]}

    for relativo, digest in esperados.items():
        origen = RUNTIME / relativo
        if not origen.exists():
            raise SystemExit(f"falta runtime/{relativo}")
        if hash_de(origen) != digest:
            raise SystemExit(f"runtime/{relativo} no coincide con el MANIFEST_LOCAL")

    if "--comprobar" in sys.argv:
        for relativo, digest in esperados.items():
            publicado = DESTINO / relativo
            if not publicado.exists() or hash_de(publicado) != digest:
                raise SystemExit(f"dist/…/{relativo} no coincide con el origen")
        print(f"vidas-en-transito: build íntegro ({len(esperados)} archivos)")
        return 0

    for relativo in esperados:
        destino = DESTINO / relativo
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(RUNTIME / relativo, destino)
        if hash_de(destino) != esperados[relativo]:
            raise SystemExit(f"la copia de {relativo} no coincide")

    total = sum((DESTINO / r).stat().st_size for r in esperados)
    print(
        "publicado: dist/dashboards/vidas-en-transito ·",
        f"{len(esperados)} archivos ·",
        f"{total:,} bytes ·",
        hashlib.sha256((DESTINO / 'index.html').read_bytes()).hexdigest()[:16] + "…",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
