# Cartografía de «Vidas en tránsito»

Documenta de dónde sale cada capa del mapa de «Cartografía de evidencia», cómo se
procesó, qué licencia tiene y qué **no** se pudo verificar. La geometría vive en
`web/geografia/` (el runtime publicado) y `construir.py` la copia a `dist/geografia/`;
las capas base y ferroviaria se regeneran con `preparar_cartografia.py` y las zonas
del INM con `preparar_evidencia.py`.

## Capas del mapa

| Capa | Estado | Geometría | Fuente | Licencia | Corte |
| --- | --- | --- | --- | --- | --- |
| Límites de países | publicada | 10 polígonos (`paises.geojson`, 62 KB) | Natural Earth · Admin 0 Countries (50m) | Dominio público | versión 5.1.2 |
| Corredor centroamericano | publicada, **generalizada** | 5 tramos entre puntos de país (`corredor.geojson`, 2,9 KB) | OIM DTM, portal de rutas para las Américas | uso de la fuente (enlace, no se redistribuye geometría de OIM) | abril de 2026 |
| Incidentes documentados | publicada | 148 puntos con coordenadas y precisión | ICIJ/CLIP, base de camiones 2018–2023 | uso de la fuente | 2018–2023 |
| Red ferroviaria oficial | publicada | 809 tramos lineales (`ferroviaria.geojson`, 418 KB, 6 707 vértices); **270 de Ferromex** por el campo `ENTIDAD` | ARTF · IDE, servicio «Vías ferroviarias» (FeatureServer) | CC BY 4.0 (datos abiertos de ARTF) | actualización hasta agosto de 2023; descarga 13-nov-2026 |
| Tránsito migrante documentado | publicada, **solo zonas** | 13 polígonos estatales (`evidencia_transito.geojson`, 75 KB) | INM, comunicados 119/23 (20-sep-2023) y 124/23 (22-sep-2023) | documento público citado; geometría de Natural Earth (dominio público) | 2023 |
| Centros de apoyo | pendiente | ninguna | ACNUR / OIT | sin verificar | — |

## Límites de países

- Descarga: `ne_50m_admin_0_countries.geojson` del repositorio de Natural Earth.
  SHA-256 de la descarga: `3e458fc036ad0a66…` (registrado en el propio GeoJSON).
- Proceso: filtro a Estados Unidos, México, Guatemala, Belice, Honduras, El Salvador,
  Nicaragua, Costa Rica, Panamá y Cuba; recorte a la ventana
  `(-118,5) · (-75,34)`, limpieza de geometrías y simplificación a 0,02° con
  shapely; coordenadas redondeadas a 4 decimales; EPSG:4326.
- Uso: solo base geográfica del mapa; no aporta datos del proyecto.

## Corredor centroamericano (generalizado)

- La fuente (OIM DTM) describe el corredor hacia el norte por Panamá → Costa Rica →
  Nicaragua → Honduras → Guatemala → México, pero **no publica una geometría de
  tramo reutilizable**, así que no se calca su mapa.
- Representación: para cada país se toma un **punto representativo real** (dentro de
  una ventana sobre el eje del corredor: la parte sur del país) y se unen los países
  consecutivos con un arco discontinuo. Es un esquema de tránsito por países, no un
  camino: no hay línea GPS, ni pasos fronterizos, ni trayectos individuales.
- Cada tramo declara en su ficha: países, orden, fuente, corte (abril de 2026),
  precisión («tramo generalizado entre centros de país; no es un camino ni una ruta
  GPS») y la advertencia de que la fuente no es exhaustiva.
- Etiqueta visible en la leyenda: «Corredor centroamericano documentado por OIM ·
  representación generalizada · corte abril de 2026» (resumida en la leyenda, con el
  detalle en la ficha de cada tramo).

## Red ferroviaria oficial · ARTF · IDE (publicada)

- **Fuente.** Agencia Reguladora del Transporte Ferroviario (ARTF), servicio «Vías
  ferroviarias» de su Infraestructura de Datos Espaciales (ArcGIS FeatureServer,
  capa 0): <https://services6.arcgis.com/ZP95JslokqLi5f3i/arcgis/rest/services/V%C3%ADas_ferroviarias/FeatureServer/0>.
  Es el mismo organismo que publica la Red Ferroviaria Nacional en datos.gob.mx
  (<https://www.datos.gob.mx/es/dataset/red_ferroviaria_nacional>, CC BY 4.0) y sus
  campos coinciden con la serie «Vía férrea» (`LINEA`, `ENTIDAD`, `VIA`,
  `TIPO_VIA`, `NIVEL`, `SERVICIO`, `CNDICON`, `LONG_`, `FECHA_ACT`).
- **Descarga.** 13 de noviembre de 2026, 809 elementos `LineString` en GeoJSON con
  `outSR=4326` y `maxAllowableOffset=0,001`. SHA-256 del archivo publicado:
  `1c4af1d0aa5d7401…` (completo en `ferroviaria.json`); SHA-256 de la descarga
  cruda: `e91f575708130267…`.
- **Preparación.** Reproyección a EPSG:4326 desde el servicio (EPSG:3857),
  simplificación Douglas-Peucker 0,003° con shapely (`preserve_topology`),
  coordenadas a 5 decimales: 12 297 → 6 707 vértices. Las 809 geometrías son
  válidas (`is_valid`), sin longitud nula; extensión −117,03…−88,15 de longitud y
  14,67…32,66 de latitud, dentro de México.
- **Atributos y estilo.** `CNDICON` distingue operación (696 tramos, línea continua)
  y sin uso (113, discontinua); el resto de campos se muestran en la ficha. No se
  infiere uso migrante.
- **Qué tramos son Ferromex.** No se dibujó ninguna línea a mano ni se recortó la red
  por aproximación geográfica: se usa el campo `ENTIDAD` del propio servicio. Los
  **270** tramos cuyo valor es «Ferrocarril Mexicano S.A. de C.V.» se marcan como
  **Ferromex** (marca comercial de esa empresa, confirmada en el aviso legal de
  ferromex.mx) y se dibujan en continuo oscuro; el resto de operadores (Ferrosur 146,
  KCSM 180, otros concesionarios 143, sin concesionar/asignar 70) en continuo claro.
  El selector «Red ferroviaria · operador» filtra el mapa por ese campo. Ferromex
  declara en su portal **11 000 km, 24 estados, 13 puertos y 6 cruces fronterizos**
  (consulta del 13 de noviembre de 2026); esas cifras corporativas se citan como
  contexto y **no** se usan para dimensionar la geometría.
- **Pendiente: el SHP de ATTRAPI.** La capa «Vía férrea, 2025» de ATTRAPI
  (`538041af-…`, datos al 16 de abril de 2026) no se ha incorporado: el intento de
  descarga directa registrado respondió HTTP 403 «Access Denied». No es la fuente de
  la capa visible y no se sustituyó por una geometría dibujada a mano.

- Ficha del recurso: <https://www.datos.gob.mx/es/dataset/red_ferroviaria_nacional_attrapi>
- Recurso «Vía férrea, 2025» (`538041af-450d-4b25-9b67-67c187a7d57f`): SHP de vías
  principales, auxiliares e industriales.
- Licencia: CC BY 4.0. Última actualización de los datos: **16 de abril de 2026**.
- URL de descarga: `https://repodatos.atdt.gob.mx/api_update/attrapi/red_ferroviaria_nacional_attrapi/01_via_ferrea.zip`
- **Aún no incorporada.** El intento de descarga directa registrado el **13 de noviembre de 2026** devolvió HTTP 403 «Access Denied» (Akamai). Detalle de las comprobaciones:
  1. `https://www.datos.gob.mx/api/3/action/package_show?id=red_ferroviaria_nacional_attrapi`
     → **HTTP 200**: confirma licencia CC BY 4.0, los cinco recursos SHP, el
     identificador del recurso y la fecha de actualización. Los metadatos están
     verificados; el archivo, no.
  2. `Invoke-WebRequest` y `curl` al ZIP con agente de Chrome, `Accept` y `Referer`
     de la ficha → **HTTP 403** (486 B, «Access Denied» de Akamai).
  3. Raíz del CDN y los otros recursos (`02_nodo.zip`, etc.) → **HTTP 403**: en ese
     intento la denegación alcanzó al host completo, no solo al archivo.
  4. Ruta CKAN `/dataset/…/resource/…/download` → **HTTP 302** al mismo CDN y 403.
  5. Navegación real de Chromium (Playwright) al ZIP y `context.request` → **403**.
  6. Visor incrustado de la ficha (`www.vistadatos.gob.mx/app_direct/gobmx-shapes/`)
     → **403**; hosts alternativos (`cdn.datos.gob.mx`, `atdt.gob.mx`) → 403/400;
     subdominios `geoportal/sig/datos` → sin DNS.
  7. Variantes de caché (`?v=2`, `?cachebust=…`) → 403; Archivo Web → sin instantáneas.
  8. El *datastore* de CKAN sí responde: `datastore_search` devuelve **832 registros
     de atributos** (`linea`, `servicio`, `tipo_via`, `entidad`, `fecha_act`, `long`).
     Es la tabla de atributos del SHP y no incluye geometría: no permite dibujar la red.
- Decisión: se publica la geometría oficial de ARTF en su IDE, atribuida a su fuente
  real, con licencia, fecha y campos documentados. El control está activo y la capa se
  dibuja; el bloque de fuentes distingue esta capa del ZIP de ATTRAPI (403).
- El guion del mapa ya contempla el alta: si `geografia/ferroviaria.json` declara
  `"estado": "disponible"` y una geometría, la dibuja con línea continua fina y
  habilita el control. El resto del procedimiento (CRS, validez, reproyección a
  EPSG:4326, simplificación, SHA-256) está descrito en el propio JSON.
- No se nombra la red «La Bestia» ni se le atribuye uso migrante: es infraestructura
  física y su superposición con el corredor no demuestra que las personas migrantes
  usen esos tramos.

## Tránsito migrante documentado · INM 2023 (publicada, solo zonas)

- **Qué es.** Capa independiente de la red física: marca **zonas estatales** que el
  Instituto Nacional de Migración (INM) menciona en 2023 en relación con la ruta del
  tren y con las acciones de contención y rescate. No es una ruta, ni una estación,
  ni una secuencia de ciudades, y no se extiende a toda la red ferroviaria.
- **Fuentes.** Dos comunicados públicos del INM:
  - **119/23 · 20 de septiembre de 2023** — la ruta del tren por ocho estados
    (México, Hidalgo, Querétaro, Guanajuato, Aguascalientes, Nuevo León, Durango y
    Chihuahua) y la propuesta de puntos de verificación, entre ellos Huehuetoca
    (Estado de México). <https://www.gob.mx/inm/prensa/propone-inm-a-ferromex-fortalecer-coordinacion-en-acciones-y-estrategias-para-evitar-que-personas-migrantes-arriesguen-su-vida-a-bordo-de-los-trenes>
  - **124/23 · 22 de septiembre de 2023** — 658 acciones en el sistema ferroviario y
    8 988 personas migrantes rescatadas entre enero y septiembre de 2023 en Veracruz,
    Tlaxcala, Coahuila, Puebla, México, Nuevo León, Guanajuato, Chihuahua y Oaxaca.
    <https://www.gob.mx/inm/prensa/acuerdan-inm-y-ferromex-acciones-con-los-tres-niveles-de-gobierno-y-cbp-para-la-ruta-del-sistema-ferroviario-a-fin-de-que-las-personas-migrantes-no-arriesguen-su-vida-a-bordo?idiom=es-MX>
  - Unión de estados citados: **13** (Aguascalientes, Chihuahua, Coahuila, Durango,
    Guanajuato, Hidalgo, México, Nuevo León, Oaxaca, Puebla, Querétaro, Tlaxcala y
    Veracruz). Cada zona conserva en sus propiedades qué comunicado la sostiene.
- **Geometría.** La fuente no publica trayectos ni coordenadas utilizables, así que la
  zona se dibuja con el **límite estatal** de Natural Earth Admin 1 (10m, dominio
  público), simplificado a 0,01°: 13 polígonos, EPSG:4326, SHA-256
  `314ab5ada5cee301…`. La geometría describe el estado, no el recorrido.
- **Referencia histórica sin geometría.** El mapa archivístico de El Colegio de México
  (2014) sobre rutas de trenes de carga usadas por migrantes se cita en la leyenda y
  en las fuentes, pero **no se dibuja**: su licencia CC BY-NC-ND no permite adaptarlo
  y el repositorio devuelve una pantalla de captcha.
- **Estilo y ficha.** Relleno gris claro translúcido, sin borde y por debajo de las
  divisiones estatales, las vías y los puntos para no tapar la red; al seleccionar, la ficha declara el
  estado, el período, los comunicados que la sostienen y el límite: «la zona no indica
  por dónde pasó cada persona».
- **Nota visible en el mapa.** «Las vías representan infraestructura ferroviaria. Las
  capas de uso migrante se basan en fuentes y períodos específicos; no muestran todos
  los trayectos ni prueban que se haya utilizado cada tramo de la red. La superposición
  de capas no implica causalidad.»

## Composición e interacción del mapa (v0.13.3)

- **Encuadre.** Mercator propio con ventana completa en escritorio
  (`(-118,5)–(-75,34)`, 1080×780) y ventana recortada a México-Centroamérica en
  pantallas estrechas, con lienzo más alto (1080×1040), para que el contenido no
  quede reducido a una franja.
- **Símbolos a tamaño constante.** El radio de incidentes y nodos, los grosores y
  los guiones se calculan en píxeles de pantalla y se convierten a unidades del SVG,
  así que el mapa se lee igual a 390 px que a 1440 px.
- **Capas.** Corredor con halo blanco, trazo discontinuo, flechas de dirección y seis
  nodos numerados; incidentes como puntos pequeños con halo y área de clic amplia;
  red ferroviaria (Ferromex en oscuro, otras redes en claro, tramos sin uso
  discontinuos); zonas del INM en gris claro bajo las divisiones estatales y las vías; etiquetas de país
  con halo; retícula discreta. Un control «Capas» agrupa los interruptores en Movilidad,
  Ferrocarril, Evidencia, Contexto y Centros de apoyo (desactivado con su razón).
  Cada interruptor enciende o apaga su capa, la leyenda marca la capa oculta y
  «Restablecer capas» vuelve al estado inicial.
- **Selección.** Un único manejador de puntero distingue clic de arrastre (el paneo
  solo captura el puntero cuando el gesto supera 5 px), de modo que el clic vuelve a
  abrir la ficha. Cada tramo, nodo, vía, zona e incidente es un `role="button"` con
  `tabindex`, `aria-pressed`, foco visible y activación con Enter o barra espaciadora.
  `Escape` y el botón «Limpiar selección» devuelven el estado inicial.
- **Ficha.** Tipo de evidencia, nombre o extremos, fuente, fecha/corte, precisión,
  datos disponibles y nota de alcance. Para las vías incluye operador, tipo de vía,
  estado operativo, servicio, longitud declarada, actualización, fuente y licencia;
  para las zonas, período, comunicados, detalle y geometría. Cuando la fuente no
  publica un dato se escribe «No disponible en la fuente»; no se inventan nombres ni
  atributos.
- **Filtro por año.** El archivo ICIJ/CLIP trae el campo `year` (2018–2023), así que el
  panel ofrece un selector para los incidentes: filtra mapa y lista, y limpia la
  selección al cambiar. El selector de operador ferroviario filtra por `ENTIDAD`. No
  se añadieron filtros que la fuente no sostenga.
- **Alternativa sin mapa.** Dos tablas plegables: una con los 172 elementos (5 tramos,
  pasos, zonas del INM e incidentes) y otra con los tramos ferroviarios
  con operador, estado y longitud. Cada fila abre la misma ficha que el mapa.

## Procedencia en el tablero

El mapa se dibuja en el cliente con SVG y una proyección Mercator propia; no usa
servicios externos, ni teselas, ni librerías de mapas. Los archivos de `geografia/`
se cargan con `fetch` relativo desde la propia carpeta, igual que `data.json` y
`fuentes_ampliadas.json`. Controles: capas independientes, zoom (−, +, rueda), paneo
con arrastre, «Restablecer vista», leyenda y fuentes en el panel lateral, ficha de
selección por clic, toque o teclado y etiquetas geográficas conmutables.

## Reproducir

```bash
python pipeline/preparar_cartografia.py
python pipeline/preparar_evidencia.py
python pipeline/construir.py
```

`preparar_cartografia.py` requiere `geopandas` y `shapely`; descarga Natural Earth a
la carpeta de insumos excluidos (no se versiona) y escribe los tres archivos de
`web/geografia/`.
`preparar_evidencia.py` descarga el ZIP admin-1 de Natural Earth si falta (o acepta
`--zip`) y escribe `evidencia_transito.geojson`; con el ZIP usado el 13-nov-2026
reproduce byte a byte el archivo publicado (SHA-256 `314ab5ada5cee301…`).


## Mapa hexagonal de muertes y desapariciones (v0.15.0)

- **Fuente.** OIM Missing Migrants Project, conjunto «Missing Migrants Project Data»
  publicado en HDX: CSV de 23 826 filas descargado el 13 de noviembre de 2026
  (SHA-256 de la descarga `0831c651121cbf67…`). Licencia **CC BY-IGO**.
  El CSV crudo no se publica; el sitio distribuye solo la malla agregada.
- **Universo.** Rutas del corredor del proyecto (`US-Mexico border crossing`,
  `Darien`, `Caribbean to US`, `Caribbean to Central America`,
  `Haiti to Dominican Republic`, `Venezuela to Caribbean`) con coordenadas
  parseables dentro del encuadre `(-118,5 … -76,5)` × `(6,5 … 33,5)`:
  **6 089 filas**. Quedan fuera 17 680 filas de otras rutas, 57 fuera del
  encuadre y **45 sin celda terrestre a menos de 0,75°** (0,7 %), declaradas en
  el panel. Las celdas suman exactamente las filas asignadas.
- **Dos subconjuntos que no se suman.** *Muertes*: filas con `number_dead > 0`
  (5 926 incidentes, 7 142 personas reportadas). *Desapariciones*: filas con
  `number_missing > 0` (152 incidentes, 536 personas reportadas). Cada celda
  guarda el desglose por año de ambas medidas.
- **Malla.** Mercator propia, **936 hexágonos terrestres** (radio 11, vista
  1200×820, misma fórmula del mapa de Panorama), **206 con datos**.
  `geografia/hexbin_muertes.geojson` (243 KB, SHA-256 `1e693844…`) y
  `hexbin_muertes.json` con totales, exclusiones y comprobación de suma.
- **Regeneración.** `python pipeline/preparar_hexbin.py`
  descarga el CSV de HDX y el ZIP admin-1 de Natural Earth si faltan, y escribe
  la malla, los metadatos y `estados_mexico.geojson` (32 entidades).
- **Base cartográfica.** `paises_hex.geojson` (Natural Earth 50m, dominio
  público, recorte y simplificación 0,02°), límites estatales de México
  (admin-1 10m), etiquetas de país y las capas contextuales ya existentes:
  corredor OIM (arco discontinuo, no GPS), red ferroviaria de ARTF (Ferromex en
  morado oscuro y otras redes en morado claro, con trazos más gruesos), zonas del
  INM 2023 e ICIJ/CLIP agregado en los mismos hexágonos, con una rampa naranja
  propia; no se dibujan puntos circulares.
- **EAAF.** Los agregados de `data.json` (2 351 casos, 2 240 familias, 6 000
  perfiles genéticos, 2 500 casos de desaparecidos y 490 identificaciones, con
  cortes del 28-feb-2025 y 14-ago-2026) se muestran en el panel del modo
  Desapariciones, **fuera del mapa y sin sumarse** con MMP.
- **Interacción.** Modos Muertes/Desapariciones; medidas de incidentes y
  personas; filtro por año (solo años con datos, 2014–2026); fuente (OIM/MMP,
  ICIJ/CLIP y EAAF agregado en desapariciones); capas conmutables; zoom con
  botones, rueda centrada en el cursor y pinza táctil; arrastre y «Restablecer»;
  ficha por celda con cifra, unidad, fechas, países, rutas, calidad de fuente y
  límite; tabla accesible; teclado (Tab, Enter, Escape).
- **Límites.** Una celda agrupa registros georreferenciados: no es la ubicación
  exacta de cada incidente ni una ruta. La fecha es la reportada por MMP, no
  necesariamente la fecha de muerte. Un incidente puede corresponder a varias
  personas. Una celda vacía no implica ausencia de muertes o desapariciones. Las
  cifras de ICIJ/CLIP son filas de incidentes documentados, no personas, y no se
  suman ni se comparan como un total común con MMP.
- **Verificación.** `node tools/verificar-hexbin-vidas.mjs` → **94
  comprobaciones OK**: la suma de celdas coincide con las filas del filtro en
  cada modo y medida, los modos, filtros y fuentes cambian hexágonos, leyenda,
  título, ficha y conteos sin mezclar MMP e ICIJ/CLIP, las fichas y el teclado
  funcionan, las capas se conmutan, el agregado del EAAF se mantiene separado,
  la rueda y la pinza hacen zoom sin seleccionar ni desplazar la página fuera del
  mapa, y no hay errores de consola ni peticiones externas.


### Incidentes ICIJ/CLIP en hexágonos (v0.21.0)

- Cada celda naranja agrupa **filas de incidentes documentados con coordenadas**;
  no es una persona y no se suma al hexbin de MMP. La fuente se elige en el
  control «Fuente»; al activar ICIJ/CLIP, medida y modos MMP se fijan o
  deshabilitan y los conteos, la leyenda, el título y la tabla declaran la unidad
  ICIJ.
- Tooltip al pasar el cursor o enfocar con teclado: número de filas de la celda,
  periodo, fechas, entidades, precisión declarada y la nota «Una celda agrega
  filas geolocalizadas; no es la ubicación exacta de cada caso ni una ruta, y no
  se suma con MMP».
- La ficha de celda se fija con clic, Enter o toque; Esc la cierra. Muestra
  fuente, periodo, fechas de las filas, entidades, precisión, unidad y límites
  metodológicos. En móvil, al tocar una celda se desplaza el panel de la ficha a
  la vista.
- Los 148 registros con coordenadas también están en una tabla accesible de
  filas, con fecha, entidad, precisión, migrantes, muertes y coordenada; esa
  tabla no dibuja puntos en el mapa.
- Los tramos ferroviarios también se pueden seleccionar: su ficha indica operador,
  color en el mapa (morado oscuro para Ferromex, claro para otras redes), tipo,
  condición, servicio, longitud, actualización, fuente y licencia.
- La leyenda declara la fuente activa y la unidad de cada capa: celdas con
  registros MMP o filas ICIJ/CLIP, tramos de infraestructura ferroviaria y
  divisiones administrativas.

### Fechas de registro y contexto de fuentes (v0.22.0)

El calendario mensual se conserva como sección secundaria, **«Fechas de registro
en las fuentes»**, con la pregunta editorial explícita sobre meses y años de
registros fechados. MMP se etiqueta como `reported_date` (fecha de reporte) y El
Paso como `Pronouncement Date` (fecha de pronunciamiento); ninguno equivale
necesariamente a la fecha de fallecimiento y los dos calendarios conservan
escalas independientes. Una celda sin fila fechada se explica como ausencia de
observación en el snapshot, no como cero muertes.

La secuencia de países del corredor OIM DTM, las tarjetas de volumen de archivo y
la matriz de cobertura se trasladaron a **Fuentes y método**. Allí los volúmenes
separan filas de archivo (MMP y El Paso) de los casos agregados del EAAF, sin
sumarlos ni homologar familias, perfiles o personas identificadas. La vista
**Muertes documentadas** conserva el mapa hexagonal y los conteos por ruta y causa
reportada, pero no dibuja una tendencia de muertes ocurridas ni conserva tarjetas
de volumen de archivo: no hay una fecha de fallecimiento comparable.

### Panorama de personas y perfiles (v0.23.0)

Panorama incluye la tarjeta **«Registros de monitoreo»**: 40,800 filas de REDODEM
(organizaciones participantes, 2023–2024), calculadas desde `data.json`, con la
aclaración de que no son personas únicas ni el total de personas migrantes. Desde
v0.25 el mapa abre la pestaña y los perfiles quedan después. Luego se presentan
tres preguntas con gráficas y tablas accesibles: edad y sexo
consignados, país registrado en el campo de nacimiento y destino capturado en el
registro.

«No especificado» (307 filas de nacimiento, 611 de género) y el literal `NA`
(34,741 filas de destino) se conservan visibles y separados de «Otros». El país de
nacimiento no se presenta como nacionalidad verificada; el destino capturado no
confirma cruce fronterizo, destino final ni permanencia en México. Panorama
declara que no puede responderse cuántas personas cruzaron a Estados Unidos ni
cuántas se quedaron en México, y no dibuja una gráfica de resultados de cruce.

La cobertura detallada del campo «violencias» se movió a **Fuentes y método**; la
pestaña **Atención y perfiles** conserva composición por año, motivos y violencias
como detalle secundario. REDODEM no se suma con MMP, El Paso ni EAAF.

### Mapa protagonista (v0.24.0)

La sección cartográfica abre con **«Corredor, ferrocarril e incidentes
documentados»**. En escritorio el mapa ocupa dos tercios del ancho; el panel
lateral reúne capas, filtros y ficha de selección. La leyenda completa queda
inmediatamente debajo del mapa, con una entrada por color/trazo, unidad y límite;
**Fuentes, disponibilidad y límites** se pliega debajo y **Explorar datos en
tabla** integra corredor, 809 vías, 13 zonas y 148 incidentes. Los incidentes se
dibujan en naranja; la red distingue Ferromex, otras redes y tramos sin uso. Las
fichas de incidente declaran el tipo de hecho y usan «No disponible» en los
campos ausentes. En móvil el mapa usa casi todo el ancho y el panel de capas
empieza plegado.

### El mapa abre Panorama (v0.25.0)

El bloque cartográfico completo se coloca inmediatamente después de la navegación
Atlas: encabezado, controles, mapa, panel lateral, leyenda, fuentes y tabla. Las
tarjetas de indicadores, las tres gráficas de perfiles, la nota de que el destino
no verifica cruce ni permanencia y la búsqueda e identificación (EAAF) quedan
después. Los calendarios se retiraron de Panorama en v0.28 y viven en Fuentes y
método. El mapa no se duplica y las demás pestañas no cambian.

### Exploración por edad y sexo (v0.26.0)

«País registrado en el campo de nacimiento» y «Destino capturado en el registro»
usan el selector segmentado del Atlas (cápsula deslizante) con Vista general,
Explorar por edad y Explorar por sexo. Los cruces país/destino × grupo etario y
género se calcularon desde las 40,800 filas del CSV oficial de REDODEM; al
seleccionar una burbuja se dibuja su desglose en burbujas por las categorías de la
fuente, con «No especificado» conservado. Los cruces de destino usan solo las
6,059 filas con destino distinto de `NA`; las 34,741 `NA` se reportan aparte. El
detalle declara denominador y total de la categoría y no estima personas únicas.

### Fechas de registro fuera de Panorama (v0.28.0)

La sección «Fechas de registro en las fuentes» y sus dos calendarios se retiraron
de Panorama. Se conservan en **Fuentes y método**, dentro del bloque plegable
**«Fechas de registro de MMP y El Paso»**, cerrado por defecto, con sus tablas
accesibles y la misma advertencia semántica sobre `reported_date` y
`Pronouncement Date`. Panorama queda con el mapa como primer bloque, la tarjeta de
registros, los perfiles REDODEM y la búsqueda e identificación; no quedan
calendarios, títulos, leyendas, tablas ni el contenedor vacío que los alojaba.

### Las gráficas de Panorama adoptan el lenguaje del mapa (v0.29.0)

Las gráficas de perfiles reutilizan la base clara del mapa: blanco, superficies
gris azulado muy tenue, bordes finos, radios de 8–16 px, títulos Georgia y
etiquetas Inter. Las notas de fuente y método usan la barra índigo de las notas
del mapa; las tablas accesibles comparten caption, encabezado `#f6f8fd` y
etiquetas pequeñas en mayúsculas. Los controles segmentados conservan la cápsula
gris del mapa y el foco índigo.

La matriz edad × sexo usa una escala secuencial índigo–lavanda basada en los
conteos de filas, no en proporciones poblacionales. «No especificado» se mantiene
en gris y los ceros se explican como ausencia de filas en esa combinación; el
texto de todas las celdas cumple AA. País de nacimiento y destino comparten lienzo
y estructura: categorías en índigo, agrupación «Otros» en lavanda con texto
oscuro, y `No especificado`/`NA` fuera de las burbujas, en gris. El tooltip de las
burbujas adopta el fondo oscuro del tooltip cartográfico. La comparación EAAF se
alineó con la paleta y la tipografía del tablero; desde v0.30 se organiza en
bloques editoriales por fuente y corte, sin puntos ni líneas.

Los colores semánticos del mapa no se tocan: corredor OIM azul, incidentes
ICIJ/CLIP naranjas, ferrocarril morado y límites/zonas en gris. Ninguna gráfica
demográfica reutiliza el naranja ni el morado ferroviario. La verificación visual
específica está en `tools/verificar-panorama-visual.mjs`.

### Alcance, totales y búsqueda (v0.30.0)

La tarjeta de 40,800 pasa a una nota compacta de alcance que declara la base, la
unidad, el periodo y la fuente, y aclara que las filas no son necesariamente
personas distintas ni el total migrante. La matriz edad × sexo añade totales por
fila y columna —6 + 4 + el total de la base— que reconcilian con 40,800, y un
selector «Conteos» / «Composición dentro del grupo de edad». La composición usa
como denominador el total de cada fila de edad, se redondea a un decimal y no se
interpreta como proporción poblacional; la fila Total queda en filas absolutas.
El título «Adultos y adultos jóvenes concentran el 74,5 %» se calcula desde los
conteos (30,388 de 40,800).

La búsqueda e identificación se reorganiza en dos grupos editoriales por corte
(28 feb 2025 y 14 ago 2026) y cinco tarjetas con nombre, cifra, unidad, fuente y
fecha. Se conservan los signos `>` y las precisiones literales, no se conectan
los cortes con líneas y se declara que los indicadores son agregados
independientes, no etapas de un mismo proceso.

### Eventos migratorios anuales (v0.31.0)

Panorama añade una gráfica de columnas con la serie oficial de eventos de
personas en situación migratoria irregular registrados en México (UPMRIP/SEGOB,
Boletín Estadístico, Cuadro 3.1, con base en registros del INM). La escala es
lineal, en índigo; los años completos 2021–2025 se dibujan en índigo y 2026 se
distingue con trama y la etiqueta «ene–sep», porque solo está publicado hasta
septiembre y no se anualiza. Los tooltips declaran año, conteo, unidad y estado;
la tabla accesible conserva los mismos valores. La tarjeta muestra fuente,
unidad, periodo, fecha de consulta, corte y definición. 2020 se excluyó porque su
cuadro 3.1 reporta «extranjeros presentados» con otra definición y columnas.

La definición administrativa cambió en 2013 y 2021; la fuente homologa el
concepto y advierte que una misma persona pudo tener más de un evento. La serie
no se suma con REDODEM ni con otras fuentes, y 40,800 no se usa como estimación
de personas migrantes.

### Respuesta y alojamiento (v0.32.0)

La sección «Respuesta y alojamiento registrados» usa pequeños múltiplos por año
para el total de personas devueltas y los tres tipos de resolución del Cuadro
3.2.3: eventos de deportación, retorno asistido y retorno asistido de niñas,
niños o adolescentes. Cada panel conserva su escala independiente, su unidad de
eventos y su propia lectura; no se apilan ni se conectan como etapas. 2026 usa
trama y se marca como parcial de enero–septiembre. Las definiciones literales
están plegadas en la tarjeta y los tooltips declaran valor, unidad, periodo,
fuente y definición.

No se localizó una serie periódica comparable de personas alojadas en estaciones
migratorias o estancias provisionales. La tarjeta deja esa vista fuera e informa
el dato faltante, distinguiendo personas alojadas durante un periodo de ocupación
simultánea y capacidad instalada. No se dibuja una serie ficticia ni se suman
devoluciones, eventos y alojamiento.
