# `pipeline/` · derivación y publicación

Estos scripts **no** forman parte del sitio: el tablero se sirve desde `web/` y no
ejecuta Python en el navegador. Aquí solo se regeneran los agregados publicados y
se empaqueta la copia servible.

- **Runtime publicado:** `web/` (no existe `pipeline/runtime`).
- **Manifiesto de hashes:** `docs/MANIFEST_LOCAL.json`.
- **Salida del build:** `dist/` (ignorada por git).
- **Raíz del clon:** cada script la deriva de `Path(__file__).resolve().parents[1]`,
  así que funcionan desde cualquier clon y desde cualquier directorio actual. No
  hay rutas del monorepo donde se armó el tablero.

## Insumos: dónde van y por qué no están aquí

El repositorio **no redistribuye** los XLS, CSV ni ZIP de las fuentes. Se descargan
a mano en una carpeta de insumos que no se versiona:

- por defecto: `pipeline/insumos_fuente/`
- o la que indiques con `--insumos RUTA` en cada script
- o la variable de entorno `MIGRATION_SOURCE_DIR` (la respetan todos, también
  `derive_data.py`)

Una prueba de la suite (`tests/test_datos.py`) falla a propósito si alguien versiona
`insumos_fuente/`, `*.xls`, `*.xlsx`, `*.csv` o `*.zip`. La regla es ejecutable.

| Insumo | Nombre esperado dentro de la carpeta de insumos | De dónde se obtiene |
|---|---|---|
| Cuadros UPMRIP, serie histórica y 2026 | `upmrip_cuadro_1.1.xls`, `1.2.xls`, `1.4.xls`, `2.1.xls`, `2.2.xls`, `2.3.xls`, `2.4.xls` | UPMRIP/SEGOB, <https://portales.segob.gob.mx/es/PoliticaMigratoria/Cuadros_Delitos?Anual=2026&Secc=1> |
| Incidentes ICIJ/CLIP | `icij_clip_cases.csv` | Base publicada por ICIJ/CLIP; metodología en <https://www.icij.org/inside-icij/2024/04/from-chiapas-to-tamaulipas-new-database-maps-thousands-of-migrants-dangerous-journeys-through-mexico-in-trailer-trucks/> |
| Cuadros del Boletín Estadístico 3.1 y 3.2.3 | `eventos_migratorios/cuadro3.1_2021.xls` … `cuadro3.1_2026.xls` y `eventos_migratorios/cuadro3.2.3_2021.xls` … `cuadro3.2.3_2026.xls` | UPMRIP/SEGOB, <https://www.portales.segob.gob.mx/es/PoliticaMigratoria/CuadrosBOLETIN?Anual=2026&Secc=3> |
| Base REDODEM | `base_monitoreo-de-proteccion_redodem.csv` (o el `.zip` oficial: el script acepta ambos) | REDODEM, <https://monitoreo-de-proteccion.redodem.org/csv/base_monitoreo-de-proteccion_redodem.zip> |
| OIM MMP («Missing Migrants Project Data») | `mmp.csv` | OIM, <https://missingmigrants.iom.int/downloads> (el script descarga la URL de HDX si falta) |
| Natural Earth 50m (países) | `ne_50m_admin_0_countries.geojson` | Dominio público, <https://github.com/nvkelso/natural-earth-vector> (el script lo descarga si falta) |
| Natural Earth admin-1 10m | `ne_admin1.zip` y `ne_10m_admin_1_states_provinces.zip` | Dominio público, <https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_admin_1_states_provinces.zip> (el script lo descarga si falta) |

Ninguno de esos archivos se copia al build: `construir.py` solo copia los archivos
declarados en `docs/MANIFEST_LOCAL.json`, que son agregados ya derivados.

## Orden de ejecución

Los pasos 1–7 son de **datos** (requieren insumos o red) y el 8 es de **build**
(funciona sin insumos, porque `web/` está versionado).

```bash
python -m pip install -r pipeline/requirements.txt          # xlrd
python -m pip install geopandas shapely                     # pasos 5, 6 y 7
```

1. **`derive_data.py`** — UPMRIP, ICIJ/CLIP y agregados OIM.
   Lee los siete XLS UPMRIP y `icij_clip_cases.csv`; consulta el servicio ArcGIS de
   OIM (necesita red). Escribe `web/fuentes_ampliadas.json`.
   `python pipeline/derive_data.py`

2. **`preparar_eventos_migratorios.py`** — eventos y devoluciones de los cuadros
   3.1 y 3.2.3. Amplía `web/data.json` (`eventos_migratorios`, `devoluciones`) sin
   tocar las demás claves.
   `python pipeline/preparar_eventos_migratorios.py --insumos RUTA`

3. **`preparar_redodem.py`** — cruces país/destino × edad y género, UpSet de
   motivos, matriz violencia × perpetrador con umbral de privacidad 5 y cobertura
   anual del campo. Amplía `web/data.json`.
   `python pipeline/preparar_redodem.py --insumos RUTA`

4. **`preparar_eaaf.py`** — herramienta offline: reconstruye `eaaf_public_detail`
   desde la transcripción del PDF incluida en el propio script (no necesita
   insumos) y actualiza el respaldo `#eaaf-inline-data` de `web/index.html`.
   `python pipeline/preparar_eaaf.py`

   > Reemplaza el respaldo embebido de `web/index.html`, así que cambia el SHA-256
   > de ese archivo: actualiza su entrada en `docs/MANIFEST_LOCAL.json` antes de
   > publicar.

5. **`preparar_cartografia.py`** — límites de países, corredor generalizado y
   estado de la capa ferroviaria. Descarga Natural Earth 50m si falta. Escribe
   `web/geografia/{paises.geojson,corredor.geojson,ferroviaria.json}`.
   `python -X utf8 pipeline/preparar_cartografia.py --insumos RUTA`

6. **`preparar_evidencia.py`** — zonas estatales del INM 2023 sobre límites
   admin-1 de Natural Earth. Escribe `web/geografia/evidencia_transito.geojson`.
   `python pipeline/preparar_evidencia.py --insumos RUTA`

7. **`preparar_hexbin.py`** — malla hexagonal de muertes y desapariciones (OIM MMP).
   Necesita `web/fuentes_ampliadas.json` del paso 1 y el GeoJSON 50m del paso 5.
   Escribe `web/geografia/{hexbin_muertes.geojson,hexbin_muertes.json,paises_hex.geojson,estados_mexico.geojson}`.
   `python pipeline/preparar_hexbin.py --insumos RUTA`

8. **`construir.py`** — publica. Verifica cada archivo de `web/` contra
   `docs/MANIFEST_LOCAL.json` y copia los 15 archivos a `dist/`.
   `python pipeline/construir.py`
   `python pipeline/construir.py --comprobar` (solo verifica, no copia)

Si un paso regenera un archivo publicado con contenido distinto, el build falla
diciendo qué archivo no coincide: hay que actualizar su `sha256` (y `bytes`) en
`docs/MANIFEST_LOCAL.json` en el mismo cambio, para que lo servido y lo verificable
sean lo mismo.

## Verificar sin insumos crudos

```bash
python -m pytest -q                     # contrato de datos y guarda de no redistribución
python pipeline/construir.py            # publica dist/ desde web/
python pipeline/construir.py --comprobar
python -m http.server 8000 --directory web   # abre http://127.0.0.1:8000/
```

`tests/test_rutas.py` comprueba que las rutas resueltas quedan dentro del clon y
que ningún script vuelve a las rutas del monorepo. Sin la carpeta de insumos,
`preparar_redodem.py` (y los demás pasos de datos) fallan con un mensaje que dice
qué archivo falta y cómo indicar la carpeta, no con un `FileNotFoundError` de una
ruta ajena al repositorio.

## Qué no hace este pipeline

- No descarga ni publica microdatos: solo agregados.
- No anualiza el corte parcial de 2026 ni imputa celdas vacías como cero.
- No ejecuta `derive_data.py` ni los `preparar_*.py` durante el build.
