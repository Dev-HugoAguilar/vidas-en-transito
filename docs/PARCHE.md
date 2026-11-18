# Corrección local del artefacto entregado (v0.13.0)

El paquete `Observatorio_Vidas_en_transito_Harness_v0.13.0.zip` se usa tal cual,
con **una única corrección de defecto** documentada aquí. Los datos, las etiquetas,
los cortes, los denominadores, las categorías y la metodología no se han tocado.

## Defecto encontrado

Al cargar el tablero servido en local, la consola registraba:

```text
TypeError: fmtN is not a function
    at renderExpandedDashboard (index.html:203:505)
```

El panel de cifras clave llamaba a `fmtN(...)` como función, pero dentro de
`renderExpandedDashboard` `fmtN` es un `Intl.NumberFormat` (en el resto del archivo
se usa siempre `fmtN.format(...)`). El error detenía el renderizado del bloque
ampliado: el tablero mostraba 14 tablas en lugar de 34 y **los 20 paneles nuevos no
aparecían**.

## Corrección aplicada

Dos llamadas, sin cambios de contenido:

```diff
- `${fmtN(I.totals.rows_with_death_value)} casos tienen valor de muertes;
-  suma reportada: ${fmtN(I.totals.deaths_reported)}.`
+ `${fmtN.format(I.totals.rows_with_death_value)} casos tienen valor de muertes;
+  suma reportada: ${fmtN.format(I.totals.deaths_reported)}.`
```

Se añadió además un comentario junto a `const fmtN=new Intl.NumberFormat('es-MX');`
para dejar constancia en el propio archivo.

## Huellas

| Archivo | Paquete | Local corregido | Cambia |
| --- | --- | --- | --- |
| `index.html` | `3f7cbf5e0b20c74a3c4f677cb75e29e918a3388177652a925b6fdaa429a7db13` · 93 157 B | `1eb476904f7a7814…` · 93 157 B + comentario | Sí (dos llamadas y un comentario) |
| `data.json` | `5b9f1f9b0a860d2043fe5ba68222d5bfcaab9a67f1a357527f9aafacdee69494` | idéntico | No |
| `fuentes_ampliadas.json` | `19ec4aae287a9da3a3dbc21167edfb3a915c1fe057fa351277104da07bcb63b1` | idéntico | No |

El hash vigente de cada archivo publicado está en `MANIFEST_LOCAL.json`, que es
contra el que verifica `construir.py`. El `MANIFEST.json` del paquete se conserva
sin editar como registro de lo entregado.
---

## Segunda modificación local (v0.13.1): mapa geográfico

El bloque «Cartografía de evidencia» se reescribió para sustituir la silueta
esquemática por un mapa geográfico real con capas independientes. Detalle en
`CARTOGRAFIA.md`.

| Archivo | Cambio |
| --- | --- |
| `runtime/index.html` | nuevo bloque `.geo-*`, estilos y guion del mapa; se retiró el SVG ilustrativo y el panel de capas bloqueadas |
| `runtime/geografia/paises.geojson` | nuevo · límites reales (Natural Earth 50m, dominio público) |
| `runtime/geografia/corredor.geojson` | nuevo · 5 tramos generalizados del corredor de OIM DTM |
| `runtime/geografia/ferroviaria.json` | nuevo · estado pendiente de la capa ATTRAPI, con enlace, licencia y motivo |
| `preparar_cartografia.py` | nuevo · regenera las tres capas |
| `construir.py` · `MANIFEST_LOCAL.json` | publican y verifican también `geografia/` |

`data.json` y `fuentes_ampliadas.json` del paquete siguen **idénticos** (hashes
verificados en `MANIFEST_LOCAL.json`). No se dibujó geometría ferroviaria: el SHP
oficial aún no está incorporada: el intento de descarga registrado devolvió HTTP 403 y no se sustituyó por otra fuente.

---

## Tercera modificación local (v0.13.2): burbujas empaquetadas

Los paneles categóricos de la serie REDODEM (03 origen, 04 destino, 05 motivos y
las dos comparaciones de 07: violencias y perpetradores) dejan los puntos sueltos
y las barras para usar el componente de burbujas del Atlas vial, portado a
JavaScript sin React. Los títulos, descripciones, notas, cortes, denominadores y
cifras del tablero no cambian; `data.json` y `fuentes_ampliadas.json` siguen
idénticos.

| Archivo | Cambio |
| --- | --- |
| `runtime/burbujas.js` | nuevo · componente de burbujas: empaquetado circular de d3-hierarchy (ISC), escala `r = k·√valor`, tooltip, selección, teclado, leyendas y aviso de licencia |
| `runtime/index.html` | los cinco paneles categóricos usan el componente; carga de `burbujas.js`; estilos `.bv-*`; «No especificado» y «NA» en bloque aparte; notas de agrupación y de multirrespuesta; `.grid-two` con `minmax(0,1fr)` para que ninguna tarjeta fuerce ancho en móvil |
| `construir.py` · `MANIFEST_LOCAL.json` | publican y verifican también `burbujas.js` |
| `tools/verificar-burbujas-vidas.mjs` | nuevo · 128 comprobaciones (vista directa, ficha, móvil) |

Qué se conserva de los datos: 8 burbujas en origen con los conteos declarados
(Honduras 12 889 … Haití 1 456) más «Otros (92 categorías)» 4 933; 307 filas «No
especificado» aparte; 8 burbujas de destino más «Otros (16)» 70; NA 34 741 de
40 800 aparte; motivos 4 066 / 3 325 / 405 / 67 menciones sobre 6 338 filas.



---

## Cuarta modificación local (v0.13.3): mapa rediseñado y selección corregida

El mapa de «Cartografía de evidencia» se recompuso (lienzo mayor, panel lateral con
ficha, leyenda y fuentes, encuadre adaptativo, símbolos a tamaño constante) y se
corrigió el defecto que impedía seleccionar tramos e incidentes: el manejador de
puntero capturaba en cada `pointerdown` y el clic nunca llegaba al elemento.

| Archivo | Cambio |
| --- | --- |
| `runtime/index.html` | bloque del mapa reescrito (HTML, CSS y guion): capas, ficha, filtro por año, lista sin mapa, selección por clic/toque/teclado y limpiar |
| `runtime/geografia/ferroviaria.json` | registro del nuevo intento de descarga (13-nov-2026) con los códigos HTTP y la evidencia; sigue `estado: pendiente` |
| `tools/verificar-mapa-vidas.mjs` | reescrito: 82 comprobaciones de composición, capas, filtro y selección |
| `CARTOGRAFIA.md` · `docs/VIDAS-EN-TRANSITO.md` · `LEEME.txt` | documentación del rediseño y del bloqueo ferroviario |

La capa ferroviaria se publica desde el servicio IDE de ARTF (809 tramos, CC BY 4.0);
el ZIP de ATTRAPI sigue pendiente porque el intento registrado devolvió HTTP 403.
Los metadatos CKAN sí se leyeron (licencia CC BY 4.0, datos al 16 de abril de 2026).
No se sustituyó por otra fuente ni se dibujó geometría inventada.

---

## Quinta modificación local (v0.13.5): red ferroviaria real

Se incorpora al mapa la red ferroviaria de México con geometría real y el control
activo. El ZIP de ATTRAPI sigue pendiente (HTTP 403 registrado); la capa visible
procede del servicio IDE de ARTF y se atribuye a esa fuente.

| Archivo | Cambio |
| --- | --- |
| `runtime/geografia/ferroviaria.geojson` | nuevo · 809 tramos lineales, EPSG:4326, 6 707 vértices |
| `runtime/geografia/ferroviaria.json` | estado «disponible», fuente ARTF · IDE, descarga, CRS, licencia, SHA-256 y el 403 de ATTRAPI |
| `runtime/index.html` | dibujo de la capa, control activo, estilo por estado operativo, ficha de la vía y textos de fuentes |
| `MANIFEST_LOCAL.json` | publica y verifica `geografia/ferroviaria.geojson` |
| `tools/verificar-mapa-vidas.mjs` | 94 comprobaciones, incluidas las de la capa ferroviaria |

La capa se identifica como infraestructura física: no se etiqueta como «La Bestia»
ni se afirma que las personas migrantes hayan recorrido sus tramos.

---

## Sexta modificación local (v0.14.0): Ferromex y evidencia de uso migrante

Dos capas más, separadas de la infraestructura: dentro de la red ferroviaria oficial se
distingue **Ferromex** por el campo `ENTIDAD` del propio servicio, y se añade la capa
**«Tránsito migrante documentado · INM 2023»** con 13 zonas estatales. No se dibujó
ninguna geometría a mano ni se amplió la evidencia a toda la red.

| Archivo | Cambio |
| --- | --- |
| `runtime/geografia/ferroviaria.geojson` | se añade `operador` derivado de `ENTIDAD`; 270 tramos «Ferromex», 539 de otras redes |
| `runtime/geografia/ferroviaria.json` | resumen por operador, regla de Ferromex, cifras corporativas (11 000 km, 24 estados, 13 puertos, 6 cruces) y el 403 de ATTRAPI |
| `runtime/geografia/evidencia_transito.geojson` | nuevo · 13 polígonos estatales (Natural Earth admin-1), período 2023, fuentes INM 119/23 y 124/23, COLMEX 2014 como referencia sin geometría |
| `runtime/geografia/evidencia_transito.json` | nuevo · metadatos de la capa de evidencia |
| `preparar_evidencia.py` | nuevo · regenera las zonas; reproduce el archivo publicado byte a byte |
| `runtime/index.html` | control y estilo de Ferromex, capa de zonas, filtro por operador, fichas de vía y de zona, leyenda y fuentes, nota metodológica, lista ferroviaria y símbolos que conservan su tamaño al acercar |
| `MANIFEST_LOCAL.json` | publica y verifica las dos capas nuevas |
| `tools/verificar-mapa-vidas.mjs` | 118 comprobaciones (incluido el zoom con símbolos a tamaño constante): geometría servida y hashes, capas, filtros, fichas, teclado, móvil y textos |

Textos exactos que se añadieron al mapa: la nota «Las vías representan infraestructura
ferroviaria…» sobre el lienzo, la atribución a ARTF · IDE con licencia CC BY 4.0 y la
aclaración de que las zonas del INM indican estados con registros de 2023, no
trayectos. El SHP de ATTRAPI 2025 sigue sin incorporarse (HTTP 403 registrado) y no se
atribuye a la capa visible.

---

## Séptima modificación local (v0.14.1): puntos de incidentes en rojo

Solo cambia el color de la capa «Incidentes documentados»: de verde azulado a rojo
oscuro **#C43B45** con borde blanco. Se actualiza el mismo color en la leyenda
(swatch y símbolo), en los estados hover, foco y seleccionado (tonos más oscuros y
borde blanco más grueso) y en la ficha del incidente (etiqueta con punto rojo). No
cambian datos, filtros, capas, geometrías ni el resto de la paleta.

| Archivo | Cambio |
| --- | --- |
| `runtime/index.html` | color de `.geo-svg-incidente` y sus estados, swatch de la capa, símbolo de leyenda y etiqueta de la ficha (`data-tipo="incidente"`) |



---

## Octava modificación local (v0.15.0): mapa hexagonal en «Muertes documentadas»

La vista de muertes gana su pieza principal: un mapa hexagonal interactivo con
modos **Muertes** y **Desapariciones**, medidas de incidentes y personas, filtro
temporal, capas contextuales, ficha por celda, zoom/arrastre y tabla accesible.
Los valores se derivan del CSV público de OIM MMP (CC BY-IGO) y la malla se
genera con `preparar_hexbin.py`; el agregado del EAAF se mantiene fuera del mapa.

| Archivo | Cambio |
| --- | --- |
| `runtime/hexmap.js` | nuevo · malla, modos, medidas, periodo, fuente, capas, fichas, teclado, zoom/arrastre y tabla |
| `runtime/geografia/hexbin_muertes.geojson` | nuevo · 936 celdas y agregados por año de muertes y desapariciones |
| `runtime/geografia/hexbin_muertes.json` | nuevo · fuente, licencia, filtros, exclusiones, totales y comprobación de suma |
| `runtime/geografia/paises_hex.geojson` · `estados_mexico.geojson` | nuevos · base cartográfica del encuadre y límites estatales |
| `preparar_hexbin.py` | nuevo · deriva la malla desde el CSV de HDX y Natural Earth |
| `runtime/index.html` | bloque y estilos `.hx-*` en la vista de muertes; carga de `hexmap.js` |
| `MANIFEST_LOCAL.json` | publica y verifica los archivos nuevos (15 en total) |
| `tools/verificar-hexbin-vidas.mjs` | nuevo · 71 comprobaciones de sumas, modos, filtros, capas, fichas, teclado, zoom, tabla y móvil |

No cambian las demás vistas ni sus datos. El CSV crudo de MMP no se distribuye: el
sitio publica la malla agregada, con fuente, licencia y totales verificados.


---

## Novena modificación local (v0.15.1): pulido del mapa hexagonal

Se ajusta solo la composición y el estilo del mapa de «Muertes documentadas»:
fondo y celdas sin registros en blanco, escala rosa a rojo más contrastada,
zonas del INM en gris claro, divisiones estatales en gris medio visible,
fronteras nacionales finas, corredor y red ferroviaria con más jerarquía, y
puntos ICIJ/CLIP interactivos con ficha propia y tabla accesible. Se añaden
unidades explícitas (incidentes, muertes reportadas, personas desaparecidas
reportadas) y la nota de que las personas son agregados de la fuente.

| Archivo | Cambio |
| --- | --- |
| `runtime/index.html` | estilos `.hx-*` y textos del bloque; tabla de puntos ICIJ |
| `runtime/hexmap.js` | unidades, fichas de puntos ICIJ, tabla de puntos, radios de símbolo al hacer zoom |
| `runtime/geografia/hexbin_muertes.*` | malla regenerada con radio 11 (936 celdas) |
| `tools/verificar-hexbin-vidas.mjs` | 71 comprobaciones, incluidas las de puntos ICIJ y la tabla |


---

## Décima modificación local (v0.15.2): fuentes plegadas en el mapa

El bloque «Fuentes, disponibilidad y límites» del mapa de Panorama deja de ocupar
el panel lateral: pasa a una fila plegable con el mismo contenido (atribuciones,
licencias, registro del 403 de ATTRAPI y límites). No se elimina información de
atribución ni licencia; solo se oculta por defecto.

| Archivo | Cambio |
| --- | --- |
| `runtime/index.html` | el panel de fuentes pasa de `<section>` a `<details>` con resumen «Fuentes, disponibilidad y límites» |
| `tools/verificar-mapa-vidas.mjs` | abre el bloque para comprobar su contenido y lo vuelve a cerrar |

---

## Undécima modificación local (v0.16.0): estilo del mapa de rutas

El mapa de «Cartografía de evidencia» adopta el estilo refinado: fondo blanco,
países sin relleno de color, zonas del INM en gris claro, divisiones estatales en
gris medio, fronteras finas, más espacio de mapa y controles/leyenda compactos.
Se añade la capa conmutable de límites de países y los estados de México como
base geométrica. Se retiran los conteos de títulos, leyenda, controles, tooltips y
fichas del mapa; los incidentes se seleccionan con su propia ficha y tooltip
(fecha, entidad, detección —o «sin dato»—, precisión, migrantes y muertes cuando
existen, enlace a la fuente y nota). El mapa hexagonal de muertes no cambia.

| Archivo | Cambio |
| --- | --- |
| `runtime/index.html` | estilos `.geo-*`, control de límites de países, tooltip de incidentes, ficha sin conteos, textos de leyenda y fuentes sin cifras |
| `tools/verificar-mapa-vidas.mjs` | 118 comprobaciones: estilos, capas, tooltip, fichas sin conteos y móvil |


---


---

## Duodécima modificación local (v0.17.0): control «Capas» agrupado

Los controles del mapa de Panorama pasan de una fila de casillas a un control
«Capas» plegable, con interruptores agrupados por Movilidad, Ferrocarril,
Evidencia, Contexto y Centros de apoyo. Cada fila muestra nombre, fuente y
limitación; la leyenda marca las capas ocultas; «Restablecer capas» vuelve al
estado inicial. En móvil el panel ocupa una columna con objetivos táctiles.

| Archivo | Cambio |
| --- | --- |
| `runtime/index.html` | botón «Capas», panel agrupado con interruptores, leyenda reactiva, reset y estilos |
| `tools/verificar-mapa-vidas.mjs` | 118 comprobaciones, incluidas las de panel, leyenda, reset, teclado y móvil |


---

## Decimotercera modificación local (v0.18.0): colores y fichas del mapa hexagonal

El mapa hexagonal conserva su escala MMP y cambia solo la lectura de las capas
contextuales: red ferroviaria en morado (Ferromex oscuro, otras redes claras),
incidentes ICIJ/CLIP en naranja y una ficha de incidente con los campos del
registro. Los campos ausentes se muestran como «Sin dato» y se explica que el
extracto no los incluye por fila. Se añade la ficha de los tramos ferroviarios y
se mantienen leyenda, controles y verificaciones.

| Archivo | Cambio |
| --- | --- |
| `runtime/index.html` | colores de vías y puntos, leyenda y estilos de ficha |
| `runtime/hexmap.js` | marcadores ICIJ con área de clic, tooltip y ficha ampliados, ficha ferroviaria, leyenda por unidades |
| `tools/verificar-hexbin-vidas.mjs` | 71 comprobaciones: colores, campos, leyenda, ficha de vía y móvil |


---

## Decimocuarta modificación local (v0.19.0): pestañas del portafolio

La navegación de «Vidas en tránsito» adopta el componente de pestañas de los
tableros anteriores (`#tabs` de Clientes y campañas): pista gris, botones de 13 px
con radios suaves, activo en gris pizarra con texto blanco y `aria-current="page"`,
desplazamiento horizontal en móvil y sin saltos de línea. Se conservan las seis
secciones y su orden.

| Archivo | Cambio |
| --- | --- |
| `runtime/index.html` | marcado `#tabs`, estilos y controlador con `aria-current` |
| `tools/verificar-vidas-en-transito.mjs` | 38 comprobaciones, incluidas pista, activo y `aria-current` |


---

## Decimoquinta modificación local (v0.20.0): navegación del Atlas Vial

La navegación abandona las pestañas numeradas y reproduce el componente real del
Atlas Vial: contenedor píldora gris, botones con icono y etiqueta breve, cápsula
activa en `#374151` con texto blanco y sombra sutil, y una sola cápsula que se
desplaza a la pestaña activa. Se conservan las seis secciones, su orden y el
contenido; los iconos siguen la familia de 16 px y trazo 1,6 del Atlas.
En móvil, las píldoras se reparten en dos columnas (una en pantallas muy
estrechas), con 44 px de alto y sin cortar etiquetas.

| Archivo | Cambio |
| --- | --- |
| `runtime/index.html` | marcado `.wm-tabs`, iconos, cápsula, estilos y controlador con teclado |
| `tools/verificar-vidas-en-transito.mjs` | 38 comprobaciones: contenedor, iconos, etiquetas sin números, cápsula y `aria-current` |
| `tools/verificar-hexbin-vidas.mjs` | 71 comprobaciones: incluye pestañas en móvil en varias filas |


---

## Decimosexta modificación local (v0.21.0): ICIJ/CLIP en hexágonos y zoom con rueda

**Defecto.** El mapa hexagonal mezclaba dos representaciones de ICIJ/CLIP: una
capa de puntos naranjas circulares y un agregado por celda con un conmutador
«hexágonos / puntos». Además, la rueda del ratón no acercaba el mapa: solo
funcionaban los botones − y +, y el gesto táctil no tenía pinza.

**Corrección.** Se retiran los puntos circulares y el conmutador de forma. La
fuente se elige en el control «Fuente»; con ICIJ/CLIP activo, los 148 registros
con coordenadas se agregan en los mismos 936 hexágonos y con el mismo tamaño de
celda, en una rampa naranja propia. Medida, modos, leyenda, título, resumen,
tabla, ficha y conteos cambian con la fuente y declaran su unidad; nunca se
suman MMP e ICIJ/CLIP. La rueda acerca y aleja centrada en el cursor, solo dentro
del mapa, sin desplazar la página ni seleccionar celdas; se añade pinza táctil de
dos punteros y se conservan arrastre, límites y botones.

| Archivo | Cambio |
| --- | --- |
| `runtime/hexmap.js` | fuente ICIJ/CLIP en hexágonos, índice por celda, rampa naranja, fichas/tooltips/tabla por unidad, control de fuente y zoom con rueda y pinza |
| `runtime/index.html` | textos y leyenda por fuente, tabla de filas ICIJ sin puntos, `touch-action` del mapa |
| `runtime/MANIFEST_LOCAL.json` | hashes de `index.html` y `hexmap.js` actualizados |
| `tools/verificar-hexbin-vidas.mjs` | **94 comprobaciones**: fuente ICIJ, unidad, paleta, fichas, conteos, rueda centrada, sin selección, desplazamiento fuera del mapa y pinza |
| `docs/VIDAS-EN-TRANSITO.md` · `CARTOGRAFIA.md` · `LEEME.md` | conteos y descripción de la fuente ICIJ y del zoom |

**Verificación.** Hexbin **94 OK**, mapa de Panorama **118 OK**, tablero **38 OK**
y burbujas **128 OK**; sin errores de consola ni peticiones externas. Capturas
nuevas: `hexbin-icij-mapa.png` y `hexbin-icij-ficha.png`.


---

## Decimoséptima modificación local (v0.22.0): fechas de registro y contexto de fuentes

**Defecto editorial.** El bloque «Calendario de evidencia» se presentaba como
«Cuándo aparecen los registros» y podía leerse como una cronología de muertes,
aunque MMP usa `reported_date` y El Paso usa `Pronouncement Date`, fechas que no
equivalen necesariamente a la fecha de fallecimiento. Además, la secuencia de
países del corredor y las tarjetas de volumen de archivo ocupaban el Panorama,
mezclaban filas, registros y casos EAAF como si fueran una misma unidad, y la
vista de Muertes todavía conservaba tarjetas de volumen de archivo.

**Corrección.** El calendario pasa a ser una sección secundaria titulada «Fechas
de registro en las fuentes», con pregunta editorial explícita y cada calendario
etiquetado con su campo temporal exacto, su escala independiente y la nota de que
una celda sin fila fechada no es cero muertes ni ausencia de observación. La
secuencia del corredor, los volúmenes y la matriz de cobertura se trasladan a
«Fuentes y método», bajo «Contexto territorial, fuentes y cobertura». Los
volúmenes separan archivos de registros (filas MMP, registros de expediente de El
Paso) de los agregados EAAF (casos), sin sumarlos ni homologarlos. La vista de
Muertes conserva el mapa y los análisis de ruta y causa reportada, retira las
tarjetas de volumen y declara que no dibuja una tendencia de muertes ocurridas
porque no existe una fecha de fallecimiento comparable.

| Archivo | Cambio |
| --- | --- |
| `runtime/index.html` | sección secundaria de fechas, calendarios con semántica exacta, contexto/volumen/cobertura en Fuentes y método, nota editorial en Muertes |
| `runtime/hexmap.js` | subtítulo de MMP reformulado como filas con fecha de reporte, sin cambios de datos |
| `runtime/MANIFEST_LOCAL.json` | hash de `index.html` actualizado |
| `tools/verificar-vidas-en-transito.mjs` | **48 comprobaciones**: pregunta editorial, dos fechas, escalas, reubicación, separación de unidades y ausencia de tendencia |
| `docs/VIDAS-EN-TRANSITO.md` | sección v0.22.0 y conteos actualizados |

**Verificación.** Hexbin **94 OK**, mapa de Panorama **118 OK**, tablero **48 OK**
y burbujas **128 OK**; sin errores de consola ni peticiones externas. Capturas
nuevas: `fechas-registro.png`, `fuentes-metodo.png` y `muertes-registros.png`.


---

## Decimoctava modificación local (v0.23.0): Panorama de personas y perfiles

**Defecto editorial.** Panorama abría con el mapa y el inventario técnico de
archivos; los perfiles de REDODEM estaban en otra pestaña y las métricas de
calidad competían con la lectura sobre las personas. Además, la vista no
declaraba con suficiente claridad que el destino capturado no verifica cruces ni
permanencia, y el volumen de archivo podía leerse como una misma unidad entre
filas, registros y casos EAAF.

**Corrección.** Panorama abre con la tarjeta **«Registros de monitoreo»** —40,800
filas calculadas desde `data.json`, periodo 2023–2024— y la aclaración de que son
filas de atención/observación, no personas únicas ni el total de personas
migrantes. Debajo se presentan tres preguntas con sus gráficas y tablas
accesibles: edad y sexo consignados; país registrado en el campo de nacimiento,
con «No especificado» aparte y sin llamarlo nacionalidad verificada; y destino
capturado en el registro, con `NA` separado y sin afirmar cruce, destino final ni
permanencia. La sección declara que no puede responderse cuántas personas
cruzaron a Estados Unidos ni cuántas se quedaron en México. La cobertura detallada
del campo «violencias» se trasladó a Fuentes y método; la pestaña Atención y
perfiles conserva composición, motivos y violencias como detalle secundario.

| Archivo | Cambio |
| --- | --- |
| `runtime/index.html` | Panorama con tarjeta principal, tres visualizaciones y trazabilidad; perfiles antes del mapa; cobertura de violencias en método |
| `runtime/MANIFEST_LOCAL.json` | versión 0.23.0 y hash de `index.html` |
| `tools/verificar-vidas-en-transito.mjs` | **60 comprobaciones**: cifras contra `data.json`, unidades, faltantes, destinos, orden y ausencia de resultados de cruce |
| `tools/verificar-burbujas-vidas.mjs` | paneles de origen/destino en Panorama y motivos/violencias en Atención y perfiles; 128 comprobaciones |
| `docs/VIDAS-EN-TRANSITO.md` · `CARTOGRAFIA.md` · `LEEME.md` | descripción de Panorama y límites de lectura |

**Verificación.** Tablero **60 OK**, burbujas **128 OK**, mapa de Panorama **118
OK** y hexbin **94 OK**; sin errores de consola ni peticiones externas. Capturas
nuevas: `panorama-perfiles.png`, `panorama-perfiles-movil.png` y
`metodo-cobertura.png`.


---

## Decimonovena modificación local (v0.24.0): mapa protagonista y panel cartográfico

**Defecto editorial.** La sección cartográfica abría con un título genérico y
repartía leyenda, fuentes y tablas en la columna lateral. El mapa competía con el
inventario, el panel de capas se desplegaba encima y la tabla ferroviaria
duplicaba el acceso general. Los incidentes se dibujaban en rojo y la ficha usaba
«sin dato» para campos ausentes.

**Corrección.** La sección abre con el título solicitado y una descripción única
de las cuatro capas. El mapa ocupa dos tercios del ancho en escritorio; el panel
lateral reúne capas, filtros y ficha. La leyenda completa queda inmediatamente
debajo del mapa, con una clave por color/trazo, unidad y límite; las fuentes pasan
a un acordeón cerrado debajo y «Explorar datos en tabla» integra corredor, red
ferroviaria, zonas e incidentes. Los incidentes son naranjas; la red distingue
Ferromex, otras redes y tramos sin uso; la ficha de incidentes declara el tipo de
hecho y usa «No disponible» en los campos ausentes. En móvil el panel «Capas y
filtros» empieza plegado y el mapa usa casi todo el ancho.

| Archivo | Cambio |
| --- | --- |
| `runtime/index.html` | nueva jerarquía cartográfica, panel lateral compacto, leyenda/fuentes/tabla bajo el mapa, colores y fichas |
| `runtime/MANIFEST_LOCAL.json` | versión 0.24.0 y hash de `index.html` |
| `tools/verificar-mapa-vidas.mjs` | **129 comprobaciones**: título único, proporción, orden, leyenda, tabla consolidada, colores, fuentes cerradas y móvil |
| `docs/VIDAS-EN-TRANSITO.md` · `CARTOGRAFIA.md` · `LEEME.md` | descripción cartográfica actualizada |

**Verificación.** Mapa **129 OK**, tablero **60 OK**, burbujas **128 OK** y hexbin
**94 OK**; sin errores de consola ni peticiones externas. Capturas nuevas:
`mapa-despues.png`, `mapa-movil.png`, `mapa-bloque-escritorio.png` y
`mapa-bloque-movil.png`.


---

## Vigésima modificación local (v0.25.0): el mapa abre Panorama

**Defecto editorial.** Panorama comenzaba con la tarjeta de registros y tres
gráficas de perfiles; el mapa quedaba más abajo y la nota sobre el destino no
verificado aparecía antes de ver el territorio. La pestaña no mostraba el mapa
desde el inicio.

**Corrección.** Se movió el bloque cartográfico completo —encabezado, controles,
mapa, panel lateral, leyenda, fuentes y tabla— inmediatamente después de la
navegación Atlas. Las tarjetas de indicadores, las tres gráficas de perfiles, la
nota sobre cruce/permanencia, los calendarios y el EAAF quedan después del mapa.
No se eliminó ni duplicó contenido; las demás pestañas no cambian. Se renumeraron
los bloques internos de Panorama.

| Archivo | Cambio |
| --- | --- |
| `runtime/index.html` | mapa al inicio de Panorama; perfiles y avisos debajo; numeración 01–04 |
| `runtime/MANIFEST_LOCAL.json` | versión 0.25.0 y hash de `index.html` |
| `tools/verificar-vidas-en-transito.mjs` | comprueba que `#geoCard` es el primer bloque y que los perfiles y la nota quedan después |
| `docs/VIDAS-EN-TRANSITO.md` · `CARTOGRAFIA.md` · `LEEME.md` | orden actualizado |

**Verificación.** Tablero **60 OK**, mapa **129 OK**, burbujas **128 OK** y hexbin
**94 OK**; sin errores de consola ni peticiones externas. Captura nueva:
`panorama-inicio.png`.


---

## Vigésima primera modificación local (v0.26.0): exploración por edad y sexo

**Defecto editorial.** «País de nacimiento» y «Destino capturado» eran gráficas
estáticas: no había controles segmentados ni una ruta de exploración por edad o
sexo, y las tarjetas no declaraban junto a la vista el total, el denominador y los
faltantes.

**Auditoría de datos.** El `data.json` de REDODEM contiene los totales por país,
por destino y los marginales de edad (`grupo_etario`) y sexo (`genero`), pero no
el cruce país × edad/sexo. Implementar un desglose por categoría sin ese cruce
obligaría a estimar; se descartó.

**Corrección.** Se añadió a ambas gráficas el selector segmentado del Atlas Vial
con cápsula deslizante, teclado y tres vistas. La vista general conserva las
burbujas y sus tablas. Al elegir edad o sexo y seleccionar una burbuja se abre un
detalle con el total exacto de esa única categoría, sus faltantes, una tabla
accesible y la leyenda **«Sin datos suficientes para este desglose»**; no se
inventan burbujas ni distribuciones. «Volver a la vista general» cierra el detalle.
Los conteos junto a cada vista declaran filas, denominador y faltantes; `NA`
permanece separado del destino registrado.

| Archivo | Cambio |
| --- | --- |
| `runtime/index.html` | controles segmentados Atlas, cápsula, detalle con fallback, conteos y notas de límite |
| `runtime/MANIFEST_LOCAL.json` | versión 0.26.0 y hash de `index.html` |
| `tools/verificar-burbujas-vidas.mjs` | **138 comprobaciones**: cápsula, modos, selección, fallback, NA, teclado y móvil |
| `docs/VIDAS-EN-TRANSITO.md` · `LEEME.md` · `CARTOGRAFIA.md` | auditoría del cruce y comportamiento del detalle |

**Verificación.** Burbujas **138 OK**, tablero **60 OK**, mapa **129 OK** y hexbin
**94 OK**; sin errores de consola ni peticiones externas. Captura nueva:
`origen-explorar.png`.


---

## Vigésima segunda modificación local (v0.27.0): cruces REDODEM reales

**Defecto.** v0.26 concluyó que el extracto no contenía el cruce país/destino ×
edad/sexo porque solo inspeccionó `data.json`. El CSV oficial de monitoreo de
protección sí contiene las cuatro columnas por fila.

**Corrección de datos.** Se descargó el ZIP oficial de REDODEM y se añadió
`preparar_redodem.py`, que lee el CSV (40,800 filas), calcula los cuatro cruces y
valida cada suma contra los marginales. Publica únicamente agregados en
`runtime/data.json`; el CSV crudo no entra al build. Los cruces de destino usan las
6,059 filas con destino distinto de `NA`; las 34,741 `NA` quedan aparte. «No
especificado» de edad y género se conserva como categoría.

**Corrección de interfaz.** Los controles segmentados ahora abren burbujas reales
por grupo etario o género para la categoría seleccionada. General se oculta durante
el detalle; «Volver» la restaura. Tooltip, leyenda, denominador y tabla accesible
salen del cruce calculado. «Otros» suma los cruces de sus miembros. El fallback
«Sin datos suficientes» queda solo para cruces vacíos o no reconciliables.

| Archivo | Cambio |
| --- | --- |
| `preparar_redodem.py` | nuevo · deriva y valida los cuatro cruces desde CSV/ZIP |
| `runtime/data.json` | nuevos `redodem.cross_tabs` y `cross_tabs_meta`; cifras existentes intactas |
| `runtime/index.html` | detalle con burbujas reales, ocultamiento de la general y vuelta |
| `runtime/MANIFEST_LOCAL.json` | versión 0.27.0 y hashes de `index.html` y `data.json` |
| `tools/verificar-burbujas-vidas.mjs` | **150 comprobaciones**: reconciliación 40,800/6,059, país y destino por edad/sexo, NA y móvil |
| `docs/VIDAS-EN-TRANSITO.md` · `CARTOGRAFIA.md` · `LEEME.md` · `FUENTES_Y_LIMITES.md` | fuente, script y cruces |

**Verificación.** burbujas **150 OK**, tablero **60 OK**, mapa **129 OK** y hexbin
**94 OK**; sin errores de consola ni peticiones externas. La fuente oficial es
https://monitoreo-de-proteccion.redodem.org/csv/base_monitoreo-de-proteccion_redodem.zip

## Vigésima tercera modificación local (v0.28.0): fechas de registro fuera de Panorama

**Defecto editorial.** Panorama todavía incluía la sección secundaria «Fechas de
registro en las fuentes» con dos calendarios. Esa sección competía con el mapa y
con los perfiles REDODEM, y su condición de «sección secundaria» no justificaba
mantenerla dentro de la pestaña.

**Corrección.** La tarjeta y sus dos calendarios se retiraron de Panorama. Se
movieron a Fuentes y método como un bloque plegable, cerrado por defecto, titulado
**«Fechas de registro de MMP y El Paso»**, con la explicación de `reported_date` y
`Pronouncement Date`, sus tablas accesibles y la advertencia de que no son fechas
de fallecimiento ni una tendencia. La tarjeta EAAF, que compartía una rejilla de
dos columnas con los calendarios, pasa a ocupar el ancho completo sin contenedor
vacío. Panorama conserva el mapa como primer bloque y, debajo, la tarjeta de
registros, los perfiles y la búsqueda e identificación.

| Archivo | Cambio |
| --- | --- |
| `runtime/index.html` | calendarios fuera de Panorama; bloque plegable en Fuentes y método; EAAF a ancho completo |
| `MANIFEST_LOCAL.json` | versión 0.28.0 y hash de `index.html` |
| `tools/verificar-vidas-en-transito.mjs` | **64 comprobaciones**: ausencia total en Panorama, bloque cerrado y apertura en Fuentes y método |
| `docs/VIDAS-EN-TRANSITO.md` · `CARTOGRAFIA.md` · `LEEME.md` | ubicación y alcance de los calendarios |

**Verificación.** tablero **64 OK**, burbujas **150 OK**, mapa **129 OK** y hexbin
**94 OK**; capturas `panorama-sin-fechas.png`, `metodo-fechas-plegado.png`,
`metodo-fechas-abierto.png` y `metodo-fechas-movil.png`.

## Vigésima cuarta modificación local (v0.29.0): lenguaje visual compartido en Panorama

**Defecto editorial.** Panorama mezclaba el lenguaje cartográfico del mapa con
gráficas de perfiles con estilos dispares: la matriz usaba azul translúcido, país
y destino usaban azul/magenta y alturas distintas, y la comparación EAAF no
declaraba la fecha de corte dentro de cada indicador.

**Corrección.** Se añadió una capa de estilos acotada a `#panorama` que reutiliza
las superficies, bordes, radios, tipografía y acento índigo del mapa. La matriz
edad × sexo pasa a una escala secuencial índigo–lavanda basada en conteos;
«No especificado» se conserva en gris y los ceros se explican como ausencia de
filas. País y destino comparten lienzo, guía, leyendas, tooltip oscuro y tabla;
las categorías van en índigo y «Otros» en lavanda con texto oscuro. La comparación
EAAF muestra la fecha de corte y la unidad en cada punto. La tarjeta de cifras
declara fuente, periodo y unidad junto al valor. Los colores semánticos del mapa
no se modificaron.

| Archivo | Cambio |
| --- | --- |
| `runtime/index.html` | estilos acotados a Panorama, escala de la matriz, metadatos, tarjeta y EAAF |
| `runtime/burbujas.js` | índigo/lavanda/gris con texto contrastado y alto fijo para país/destino |
| `MANIFEST_LOCAL.json` | versión 0.29.0 y hashes de `index.html` y `burbujas.js` |
| `tools/verificar-burbujas-vidas.mjs` | colores y contraste del texto interior actualizados |
| `tools/verificar-panorama-visual.mjs` | **53 comprobaciones**: jerarquía, escala, colores semánticos, tooltip, tablas, EAAF y móvil |
| `docs/VIDAS-EN-TRANSITO.md` · `CARTOGRAFIA.md` · `LEEME.md` | sistema visual y validación |

**Verificación.** visual de Panorama **53 OK**, tablero **64 OK**, burbujas
**150 OK**, mapa **129 OK** y hexbin **94 OK**; capturas
`panorama-unificado-perfiles.png`, `panorama-unificado-eaaf.png`,
`panorama-unificado-tooltip.png` y `panorama-unificado-movil.png`.

## Vigésima quinta modificación local (v0.30.0): alcance, totales y búsqueda

**Defecto editorial.** La cifra 40,800 seguía funcionando como KPI aislado y se
repetía en la bajada; la matriz no mostraba totales ni distinguía conteos de
composición; y la búsqueda e identificación usaba puntos del mismo tamaño que
podían sugerir magnitudes comparables o una evolución inexistente.

**Corrección.** La tarjeta se sustituye por una nota compacta de alcance con la
base, la unidad, el periodo y la fuente. La matriz conserva 24 celdas, añade 11
celdas de total (6 filas + 4 columnas + base), reconcilia con 40,800 y ofrece
«Conteos» / «Composición dentro del grupo de edad»; la composición usa el total
de la fila como denominador y declara que no es una proporción poblacional. El
título se calcula desde los conteos: 30,388 de 40,800 = 74,5 %. La búsqueda se
reorganiza en dos grupos editoriales y cinco tarjetas con cifra, unidad, fuente y
corte; se conservan los signos `>` y se elimina cualquier punto o línea que
sugiera evolución.

| Archivo | Cambio |
| --- | --- |
| `runtime/index.html` | nota de alcance, matriz con totales y selector, bloques EAAF |
| `MANIFEST_LOCAL.json` | versión 0.30.0 y hash de `index.html` |
| `tools/verificar-vidas-en-transito.mjs` | alcance, título calculado y matriz de 24 celdas |
| `tools/verificar-panorama-visual.mjs` | **76 comprobaciones**: totales, composición, teclado, EAAF y móvil |
| `docs/VIDAS-EN-TRANSITO.md` · `CARTOGRAFIA.md` · `LEEME.md` | cálculos, lectura y validación |

**Cálculos verificados.** Filas: Niñxs 6,768 · Adolescentes 2,768 · Adultos
jóvenes 14,722 · Adultos 15,666 · Adultos mayores 546 · No especificado 330.
Columnas: Hombre 25,339 · Mujer 14,787 · Persona no binaria 63 · No especificado
611. Total: 40,800. La suma de Adultos y Adultos jóvenes es 30,388 (74,5 %). No
hubo diferencias que explicar.

**Verificación.** visual de Panorama **76 OK**, tablero **64 OK**, burbujas
**150 OK**, mapa **129 OK** y hexbin **94 OK**; capturas
`panorama-composicion.png`, `panorama-composicion-movil.png` y
`panorama-unificado-eaaf.png`.

## Vigésima sexta modificación local (v0.31.0): eventos migratorios anuales

**Fuente verificada.** Se localizaron y descargaron los cuadros 3.1 del Boletín
Estadístico de UPMRIP/SEGOB para 2020–2026. La serie comparable usa 2021–2026:
309,692; 441,409; 778,907; 1,234,698; 155,730; y 31,077 para 2026
enero–septiembre. La tabla 2026 solo publica nueve meses y declara información
preliminar. 2020 (82,379) se conserva como antecedente, pero se excluye de la
gráfica porque su cuadro reporta «extranjeros presentados» con otra definición y
columnas. Los XLS quedaron en `insumos_fuente/eventos_migratorios/`;
`preparar_eventos_migratorios.py` valida los subtotales mensuales y regenera el
bloque de `data.json`.

**Corrección.** Panorama incorpora una gráfica de columnas anuales con escala
lineal, tooltips, leyenda, tabla accesible y la nota de que son eventos
administrativos, no personas únicas. 2026 se dibuja con trama y la etiqueta
«ene–sep»; no se proyecta ni se anualiza. La tarjeta declara fuente, unidad,
periodo, fecha de consulta, corte y definición. No se usa 40,800 como estimación
de migrantes ni se suma con REDODEM.

| Archivo | Cambio |
| --- | --- |
| `preparar_eventos_migratorios.py` | nuevo · lee los XLS 3.1 y publica el bloque anual |
| `insumos_fuente/eventos_migratorios/` | nuevo · cuadros oficiales 2020–2026 y README |
| `runtime/data.json` | nuevo bloque `eventos_migratorios` |
| `runtime/index.html` | tarjeta y gráfica anual en Panorama; EAAF pasa a 04 |
| `MANIFEST_LOCAL.json` | versión 0.31.0 y hashes de `index.html` y `data.json` |
| `tools/verificar-eventos-migratorios.mjs` | **37 comprobaciones**: fuente, valores, 2026 parcial, tooltips, teclado, tabla y móvil |
| `docs/VIDAS-EN-TRANSITO.md` · `CARTOGRAFIA.md` · `LEEME.md` · `FUENTES_Y_LIMITES.md` | fuente, definición y límites |

**Verificación.** eventos migratorios **37 OK**, visual de Panorama **76 OK**,
tablero **64 OK**, burbujas **150 OK**, mapa **129 OK** y hexbin **94 OK**;
capturas `eventos-migratorios.png` y `eventos-migratorios-movil.png`.

## Vigésima séptima modificación local (v0.32.0): devoluciones y alojamiento

**Fuente verificada.** Se descargaron los cuadros 3.2.3 de UPMRIP/SEGOB
2021–2026. El total de personas devueltas y los tres tipos de resolución son:
2021: 130,275 (2,298 deportación; 104,929 retorno; 23,048 NNA); 2022: 121,963
(4,143; 104,897; 12,923); 2023: 54,728 (3,626; 43,437; 7,665); 2024: 20,834
(516; 16,398; 3,920); 2025: 11,804 (1,153; 9,165; 1,486); 2026 enero–septiembre:
10,829 (4,559; 5,832; 438). Cada total suma exactamente sus tipos.

**Corrección.** Panorama añade «Respuesta y alojamiento registrados» con cuatro
pequeños múltiplos de escalas independientes: total, deportación, retorno
asistido y retorno asistido de NNA. 2026 se marca como parcial con trama y
«ene–sep». No se apilan las barras, no se conectan medidas y no se suman con los
eventos del Cuadro 3.1 ni con alojamiento. Las definiciones literales de los
tipos están plegadas y los tooltips declaran valor, unidad, periodo, fuente y
definición.

No se localizó una serie periódica comparable de personas alojadas en estaciones
migratorias o estancias provisionales en los cuadros del Boletín consultados. La
vista se deja fuera y se informa el dato faltante, distinguiendo el total de
personas alojadas durante un periodo de la ocupación simultánea y la capacidad
instalada.

| Archivo | Cambio |
| --- | --- |
| `preparar_eventos_migratorios.py` | lee también 3.2.3 y publica `devoluciones` |
| `insumos_fuente/eventos_migratorios/` | cuadros 3.2.3 2021–2026 y README |
| `runtime/data.json` | nuevo bloque `devoluciones` |
| `runtime/index.html` | sección de pequeños múltiplos, definiciones y aviso de alojamiento |
| `MANIFEST_LOCAL.json` | versión 0.32.0 y hashes |
| `tools/verificar-respuesta-migratoria.mjs` | **38 comprobaciones**: totales, tipos, escalas, tooltips, tabla y móvil |
| `docs/VIDAS-EN-TRANSITO.md` · `CARTOGRAFIA.md` · `LEEME.md` · `FUENTES_Y_LIMITES.md` | fuente, tipos, límites y dato faltante |

**Verificación.** respuesta migratoria **38 OK**, eventos migratorios **37 OK**,
visual de Panorama **76 OK**, tablero **64 OK**, burbujas **150 OK**, mapa
**129 OK** y hexbin **94 OK**; capturas `respuesta-alojamiento.png` y
`respuesta-alojamiento-movil.png`.

---

## Vigésima octava modificación local (v0.33.0): explorador EAAF

**Paquete de referencia.** Se revisó la entrega `v0.14.1` (dashboard, ETL,
documentación y respaldo). El repositorio ya estaba en `v0.32.0`, con el mapa
hexagonal, los eventos migratorios, las devoluciones y el rediseño de Panorama;
no se reemplazó el HTML ni el `data.json` completos. Se incorporó de forma
selectiva el contrato `eaaf_public_detail` (160 observaciones), el explorador de
Desapariciones y su respaldo embebido.

**Datos.** `runtime/data.json` conserva todas las claves previas y añade
`eaaf_public_detail`. Sus totales reconcilian: 2,351 casos no localizados;
2,240 familias; 6,000 donantes de ADN; 406 identificaciones. Los desgloses suman
2,351 por banco y por año; 6,000 donantes por banco y por año; 406
identificaciones por año, banco y país de hallazgo; y 578/529/1,448 en las 22
entidades de México*. `missing_search_aggregates` se mantiene con sus cinco
indicadores para no alterar el Panorama: el total de 406 se lee del detalle y no
se duplica como tarjeta.

**Interfaz.** Desapariciones abre corte → indicador → desglose → categoría. El
corte 28-feb-2025 ofrece banco/mecanismo, serie anual y, para identificaciones,
país de hallazgo. Al seleccionar México* aparece el botón para abrir las 22
entidades; el detalle declara el subtotal 578 casos y que las entidades ausentes
no se imputan a cero. El corte 14-ago-2026 solo muestra >2,500 casos y >490
identificaciones, sin desglose ni tendencia. Cada vista tiene barras y tabla
accesible con el mismo indicador, unidad, corte y nivel. No se añadieron edad,
sexo, nacionalidad, nombres ni coordenadas individuales.

**Herramienta offline.** `preparar_eaaf.py` reconstruye `eaaf_public_detail`
desde la transcripción estructurada y actualiza `#eaaf-inline-data`; no se
ejecuta en `construir.py` ni en el navegador. El respaldo permite dibujar el
explorador y el Panorama EAAF si falla `data.json`.

| Archivo | Cambio |
| --- | --- |
| `runtime/data.json` | nuevo `eaaf_public_detail`; se conservan las claves y los cinco agregados previos |
| `runtime/index.html` | CSS, sección de Desapariciones, `renderEAAFExplorer`, respaldo y marcadores |
| `preparar_eaaf.py` | ETL offline adaptado a `runtime/`; no altera `missing_search_aggregates` |
| `MANIFEST_LOCAL.json` | versión 0.33.0 y hashes |
| `tools/verificar-eaaf-vidas.mjs` | **64 comprobaciones**: datos, recorrido, tabla, teclado, 2026, respaldo y 390 px |
| `dist/content.js` | ficha actualizada con el explorador y la fuente EAAF |
| `LEEME.md` · `FUENTES_Y_LIMITES.md` · `INVENTARIO_GRAFICAS.md` | grano, unidades, desgloses, límites y uso del ETL |

**Verificación.** EAAF **64 OK**. Se conservan las verificaciones previas:
tablero **64 OK**, visual de Panorama **76 OK**, eventos **37 OK**, respuesta
**38 OK**, burbujas **150 OK**, mapa **129 OK** y hexbin **94 OK**. Capturas:
`eaaf-explorer-escritorio.png`, `eaaf-explorer-2026.png` y
`eaaf-explorer-movil.png`. No se hizo push, publicación ni despliegue remoto.

---

## Vigésima novena modificación local (v0.34.0): Atención y perfiles

**Fuente y grano.** La pestaña se reconstruyó desde el CSV local de REDODEM
(40,800 filas, 2023–2024), no desde los marginales publicados. El ETL usa la
posición 1-based del CSV como identificador interno de fila para no duplicar una
fila en una pareja; no exporta ese identificador ni microdatos. Cada fila sigue
siendo un registro de atención u observación, no una persona única.

**Motivos.** 6,338 filas con algún motivo, 34,462 con `NA`, 0 en blanco y 7,863
menciones (Socioeconómicos 4,066; De violencias 3,325; Personales 405;
Ambientales 67). Hay 14 combinaciones observadas; suman 6,338 filas y 29
pertenencias de categoría. El UpSet muestra cada fila en su combinación exacta y
separa el `NA`; no crea combinaciones ni porcentajes que deban sumar 100 %.

**Coaparición y privacidad.** La matriz 14 × 10 se calculó desde las filas
originales: 469 filas con ambos campos, 30 solo con violencias, 0 solo con
perpetradores y 40,301 sin valor en ninguno. Las 469 filas producen 950
coapariciones de categoría; hay 76 pares con filas y 64 pares con 0. El proyecto
no tenía umbral de privacidad: se adopta **5**. Las celdas con 5 o más filas
publican la cifra; las de 1–4 se muestran como rango suprimido y no exportan el
valor exacto; los pares con 0 no se listan. La tabla accesible tampoco publica
las cifras suprimidas. La coaparición no se interpreta como causalidad.

**Rankings y cobertura.** Violencias: 499 filas con valor y 737 menciones;
perpetradores: 469 y 597. «No especificado» es una categoría explícita (7
menciones; 3 filas solo con esa categoría), distinta del literal `NA`. Cobertura
del campo por año: 2023: 317 de 22,123 (1.43 %); 2024: 182 de 18,677 (0.97 %).
La línea solo conecta los dos años y no se presenta como tendencia.

**Diferencia con la captura.** La referencia abrevia «Destrucción de documentos»;
la etiqueta completa del archivo es **«Destrucción de documentos de identidad y
migratorios»**. Los demás conteos de la referencia coinciden. No se ajustaron
datos para hacerlos coincidir.

| Archivo | Cambio |
| --- | --- |
| `preparar_redodem.py` | calcula motivos, combinaciones, matriz con umbral, rankings y cobertura anual; valida filas, menciones, combinaciones y coapariciones |
| `runtime/data.json` | nuevos `motif_combinations`, `violence_perpetrator`, `violence_coverage_by_year` y `analysis_meta` |
| `runtime/index.html` | nueva composición editorial de la pestaña, UpSet, matriz, rankings, puntos conectados y tablas |
| `MANIFEST_LOCAL.json` | versión 0.34.0 y hashes |
| `tools/verificar-atencion-redodem.mjs` | **53 comprobaciones**: datos, UpSet, matriz, privacidad, rankings, año, teclado, contraste y 390 px |
| `LEEME.md` · `FUENTES_Y_LIMITES.md` · `INVENTARIO_GRAFICAS.md` · `docs/VIDAS-EN-TRANSITO.md` | definiciones, umbral, límites y reconciliaciones |
| `dist/content.js` | ficha del portafolio actualizada con la nueva lectura |

**Verificación.** Atención REDODEM **53 OK, 0 fallos**. Se conservan EAAF **64
OK**, tablero **64 OK**, visual de Panorama **76 OK**, eventos **37 OK**,
respuesta **38 OK**, burbujas **105 OK** (solo origen y destino de Panorama; los
tres paneles de Atención pasaron a UpSet, matriz y rankings), mapa **129 OK** y
hexbin **94 OK**. Capturas: `atencion-perfiles-escritorio.png`, `atencion-perfiles-movil.png`,
`atencion-matriz-escritorio.png`, `atencion-matriz-movil.png` y
`atencion-anio-movil.png`. No se hizo push, publicación ni despliegue remoto.


