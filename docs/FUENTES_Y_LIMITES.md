# Fuentes y decisiones · v0.34.0

Fecha de captura de este prototipo: 14 de noviembre de 2026. La serie de eventos migratorios se consultó el 13 de noviembre de 2026. Los datos se conservan separados por fuente y unidad. La ampliación de Atención y perfiles se calculó desde el CSV local de REDODEM (40,800 filas) y conserva el umbral de privacidad 5 en la matriz de coaparición.

| Fuente | Cobertura usada | Unidad | Visualizaciones | Límite principal |
|---|---|---|---|---|
| UPMRIP/SEGOB, serie histórica | 2016–2025 | Personas migrantes en situación irregular que manifestaron haber sido víctimas y fueron identificadas durante proceso/registro administrativo | Año, edad, sexo registrado, nacionalidad, delito, entidad de registro | Es registro administrativo y declaración de victimización; no es censo de delitos ni todas las personas migrantes |
| UPMRIP/SEGOB, cuadros 2026 | Enero–septiembre de 2026, preliminar | Mismo universo administrativo | Mes, edad, sexo, nacionalidad y delito | No se extrapola a un año completo; el PDF consultado presenta ventana distinta |
| UPMRIP/SEGOB, Boletín Estadístico Cuadro 3.1 (v0.31.0) | 2021–2025 completos; 2026 enero–septiembre, parcial | Eventos de personas en situación migratoria irregular registrados en México | Gráfica anual de columnas en Panorama | Eventos administrativos, no personas únicas; 2026 no se anualiza; 2020 se excluye por definición/columnas distintas; la definición administrativa cambió en 2013 y 2021 |
| UPMRIP/SEGOB, Boletín Estadístico Cuadro 3.2.3 (v0.32.0) | 2021–2025 completos; 2026 enero–septiembre, parcial | Eventos de personas devueltas por la autoridad migratoria mexicana, por tipo de resolución | Pequeños múltiplos y tabla: total, deportación, retorno asistido y retorno asistido de NNA | Eventos administrativos; no se apilan; no se suman con 3.1 ni con alojamiento; los tipos conservan su definición literal |
| ICIJ/CLIP, base de camiones | 2018–2023; 156 incidentes | Casos/incidentes documentados | Tiempo, entidad, detección, precisión y 148 puntos con coordenadas | Investigación periodística incompleta; filas de incidentes no equivalen a personas únicas. Las muertes se reportan solo en 13 filas; celdas vacías no son cero |
| OIM DTM, corredor centroamericano descrito en el portal de rutas | Corte de referencia abril de 2026; secuencia regional de países | Corredor descrito por OIM | Esquema por países, no traza vial ni representación exhaustiva | OIM advierte que muestra rutas principales con datos disponibles; no es exhaustivo |
| OIM DTM, ArcGIS Shelter Service, capa 0 | 3,822 features; 8 países presentes en la respuesta agregada | Registro publicado en el servicio | País, tipo de sitio y estado/campos incompletos | Extensión geográfica parcial; no hay fecha visible de actualización en metadatos consultados; no se interpreta como directorio actual validado para población migrante |
| OIM MMP · conjunto HDX con coordenadas (v0.15.0) | 23 826 filas globales; 6 089 del corredor dentro del encuadre (2014–2026) | Incidentes documentados y muertes reportadas (`number_dead`) | Mapa hexagonal por celda en «Muertes documentadas» | CC BY-IGO; la fecha es la reportada, no la de muerte; una celda agrega registros y no es una ubicación exacta; 45 filas sin celda terrestre cercana |
| OIM MMP · personas desaparecidas (v0.15.0) | 152 incidentes y 536 personas con `number_missing > 0` en el corredor y encuadre | Personas desaparecidas reportadas | Mapa hexagonal en el modo «Desapariciones» | Mismo conjunto y licencia; subconjunto distinto que no se suma con muertes ni con el EAAF |
| REDODEM · base de monitoreo de protección (v0.34.0) | 40,800 filas de atención u observación, 2023–2024 | Filas de atención/observación; no personas únicas | UpSet de motivos; matriz violencia × perpetrador; rankings de menciones; cobertura del campo por año; tablas accesibles | Registro de organizaciones participantes, no censo ni muestra representativa. La coaparición no demuestra causalidad. Las celdas 1–4 de la matriz se suprimen con umbral 5; NA no es cero ni «No especificado» |
| EAAF · Proyecto Frontera (detalle normalizado) | 160 observaciones: 2 351 casos no localizados, 2 240 familias, 6 000 donantes de ADN y 406 identificaciones; corte 28-feb-2025; 2010–2025 | Casos, familias, donantes de ADN, identificaciones | Explorador de Desapariciones: agregado → banco/mecanismo → México* → entidad; series anuales; país de hallazgo para identificaciones; tabla accesible | La fuente no publica edad, sexo ni nacionalidad; no se infieren. Los años son la fecha del evento que titula la serie, no la fecha de desaparición. Las entidades ausentes de México* no son cero. Sin coordenadas: no se dibuja ni se desglosa por celda; no se suma con MMP |
| EAAF · comunicado 14-ago-2026 | >2 500 casos y >490 identificaciones | Casos e identificaciones, con operador `>` | Tarjetas del mismo explorador, separadas del corte detallado | No publica desglose comparable; no se interpola ni se conecta como tendencia con 2025 |
| OIM MMP, El Paso, EAAF, REDODEM | Según `data.json` y documentación v0.12 | Depende de cada fuente | Visualizaciones preexistentes del tablero | Se conservan las notas de cobertura y metodología de la versión anterior |
| ARTF · IDE, servicio «Vías ferroviarias» (FeatureServer, capa 0) | 809 tramos lineales; datos hasta agosto de 2023; descarga 13-nov-2026 | Tramo de infraestructura ferroviaria | Mapa: red ferroviaria oficial; Ferromex (270) por el campo `ENTIDAD`, resto de operadores en claro, tramos sin uso discontinuos | CC BY 4.0. Es infraestructura física: no prueba uso migrante. El SHP «Vía férrea, 2025» de ATTRAPI no está incorporado (HTTP 403 registrado) y no se atribuye a la capa visible |
| INM, comunicados 119/23 (20-sep-2023) y 124/23 (22-sep-2023) | 2023; ruta del tren en 8 estados y acciones de enero–septiembre en 9 | Zona estatal mencionada por la fuente | Mapa: «Tránsito migrante documentado · INM 2023», 13 zonas sobre límites Natural Earth | La fuente identifica estados, no trayectos ni estaciones; no se dibujan rutas, secuencias de ciudades ni puntos de paso |
| El Colegio de México, mapa de rutas de trenes de carga (2014) | 2014 | Referencia histórica | Solo cita en leyenda y fuentes | CC BY-NC-ND: no se copia ni se adapta su geometría; el repositorio devuelve captcha |

## Cifras derivadas que se ven en el tablero

- UPMRIP suma de las diez cifras anuales: 6,368 registros anuales agregados. No son 6,368 personas únicas.
- UPMRIP enero–septiembre de 2026: 62 registros preliminares sumados en los nueve meses.
- UPMRIP Cuadro 3.1, eventos comparables: 2021: 309,692; 2022: 441,409; 2023: 778,907; 2024: 1,234,698; 2025: 155,730; 2026 enero–septiembre: 31,077. No se suman entre años ni se anualiza 2026. 2020 (82,379) se conserva como antecedente, pero no entra a la gráfica porque su cuadro reporta «extranjeros presentados» con otra definición y columnas.
- UPMRIP Cuadro 3.2.3, devoluciones: 2021: 130,275 (2,298 deportación; 104,929 retorno asistido; 23,048 NNA); 2022: 121,963 (4,143; 104,897; 12,923); 2023: 54,728 (3,626; 43,437; 7,665); 2024: 20,834 (516; 16,398; 3,920); 2025: 11,804 (1,153; 9,165; 1,486); 2026 enero–septiembre: 10,829 (4,559; 5,832; 438). Cada total es la suma de sus tipos; no se apila ni se suma con eventos o alojamiento.
- ICIJ/CLIP: 156 incidentes en el archivo, 172 vehículos documentados, al menos 111 muertes reportadas en 13 filas, 148 filas con coordenadas y 99 coordenadas de precisión exacta. El total de migrantes y menores suma los valores presentes, no un conteo exhaustivo.
- OIM DTM: 3,822 features. Campos de estado y tipo presentan vacíos; los ocho países responden a la capa consultada, no a una cobertura regional completa.
- EAAF, reconciliación del corte 28-feb-2025: casos por banco 2,351; familias 2,240; donantes 6,000; casos por año 2,351; donantes por año 6,000; identificaciones por año 406; por banco 406; por país de hallazgo 406; México* por entidad 578 casos, 529 familias y 1,448 donantes. Cada total coincide con la suma de sus categorías publicadas.

## Explorador EAAF

- **Grano:** una observación por indicador × corte × dimensión de desglose × categoría publicada. `eaaf_public_detail` contiene 160 registros; no son microdatos.
- **Dimensiones:** `total`, `banco_mecanismo`, `year`, `state_mexico` y `place_found_country`. `state_mexico` solo se abre después de seleccionar `México*`; las identificaciones no publican entidad.
- **Subtotal México*:** 578 casos, 529 familias y 1,448 donantes. Las 22 entidades listadas suman ese subtotal; las ausentes no se imputan a cero. Chiapas y Oaxaca se publican como bancos/mecanismos separados, no dentro de `México*`.
- **Años:** 2010–2025 para casos y donantes; 2011–2025 para identificaciones. El año es el de toma/registro, recolección o identificación, según la serie; no es la fecha de desaparición.
- **Identificaciones:** banco/mecanismo (7 categorías), año (15) y país de hallazgo (Estados Unidos 280, México 125, Guatemala 1). El total es 406.
- **2026:** solo `>2 500` casos y `>490` identificaciones. No hay desglose, no se interpola y no se presenta como continuación del corte 2025.
- **Revisión:** la transcripción del corte 2025 se concilió con los totales impresos; sigue pendiente una segunda revisión humana. El respaldo embebido `#eaaf-inline-data` permite dibujar el explorador si falla `data.json`.

## Atención y perfiles · REDODEM (v0.34.0)

- **Fuente y unidad.** CSV local `base_monitoreo-de-proteccion_redodem.csv` (40,800 filas), 2023–2024. Cada fila es un registro de atención u observación de una organización participante; no es una persona única, un censo ni una muestra representativa. El ETL solo exporta agregados.
- **Identificador de fila.** El CSV no trae `source_row_id`. Para contar coapariciones sin duplicar una fila, el ETL usa la **posición 1-based** del CSV como identificador interno; no se exporta ni aparece en tooltips o tablas.
- **Motivos.** 6,338 filas con algún motivo, 34,462 con `NA`, 0 en blanco y 7,863 menciones de categoría (Socioeconómicos 4,066; De violencias 3,325; Personales 405; Ambientales 67). Hay 14 combinaciones observadas; suman 6,338 filas. Cada combinación incluye 1–4 categorías y suma 29 pertenencias de categoría. `NA` no es un motivo y no se reparte entre combinaciones.
- **Coaparición violencia × perpetrador.** 469 filas tienen ambos campos; 30 tienen violencias pero no perpetrador; 0 tiene perpetrador pero no violencias; 40,301 no tienen valor en ninguno. Las 469 filas producen 950 coapariciones de categoría (una fila puede declarar varias violencias y varios perpetradores); hay 76 pares con al menos una fila y 64 pares con 0.
- **Umbral de privacidad.** No existía un umbral previo en el proyecto. Se adopta **5**: las celdas con 5 o más filas publican la cifra exacta; las celdas con 1–4 filas se muestran como rango suprimido (`1–4`) y no exportan el valor exacto; los pares con 0 no se listan. El umbral vive en `violence_perpetrator.privacy_threshold` y se declara en la interfaz.
- **Cobertura anual del campo `violencias`.** 2023: 317 de 22,123 filas (1.4329 %); 2024: 182 de 18,677 filas (0.9745 %). Los denominadores son las filas del año; el numerador es la presencia de un valor distinto de `NA` y de blanco (blanco: 0 en ambos años). La línea solo conecta los dos años y no es una tendencia.
- **Rankings.** Violencias: 499 filas con valor y 737 menciones; la categoría más frecuente es Robo o asalto (228) y la menor, Intrusión violenta a su vivienda (3). Perpetradores: 469 filas con valor y 597 menciones; Crimen organizado 128, Particulares 112, Autoridades migratorias 109, Autoridades policiales 108, Delincuencia común 83, Autoridades otras 25, Miembro de pandilla 11, Autoridades militares 9, No especificado 7, Coyote 5. «No especificado» es una respuesta explícita; 3 filas solo declaran esa categoría. No es el literal `NA`.
- **Diferencia de etiqueta.** La fuente escribe **«Destrucción de documentos de identidad y migratorios»**; la referencia de trabajo la abrevia como «Destrucción de documentos». Se conserva la etiqueta completa del archivo. No hay otras diferencias de conteo con la referencia.
- **Límite de interpretación.** La coaparición no demuestra causalidad, no verifica al perpetrador ni confirma una relación. Los rankings son menciones de categoría, no personas, prevalencia ni incidencia poblacional. El UpSet cuenta filas en combinaciones exactas y no crea combinaciones no observadas.

## Alojamiento en estaciones migratorias

No se localizó una serie periódica comparable 2021–2026 de personas alojadas en
estaciones migratorias o estancias provisionales en los cuadros del Boletín
Estadístico consultados. El tablero deja la vista fuera e informa el dato
faltante. No se sustituye con ocupación simultánea, capacidad instalada ni cortes
aislados, porque son unidades y periodos distintos. Una cifra de personas
alojadas durante un periodo no equivale a la ocupación simultánea.

## Capas documentadas pero no cuantificadas en esta versión

- **RARAMIR:** visor oficial UPMRIP. No se extrajeron capas o tablas estructuradas del visor. Su población administrativa no representa toda la movilidad en tránsito.
- **Grupos Beta:** se localizó el dataset agregado por entidad, pero no se incorporó porque no quedó disponible una descarga verificable del CSV en esta sesión.
- **ACNUR México y OIT:** directorios consultables; falta captura/revalidación de contactos, vigencia y licencia para un mapa práctico.
- **COLMEX 2014:** mapa histórico de ferrocarril; no se copia ni adapta por sus condiciones de reutilización y porque no representa una ruta vigente.
- **HumanTMexicoNetwork:** excluido de la cartografía pública por el carácter sensible y el muestreo no representativo.
- **Carteles/rutas ilícitas:** no se dibujan ni infieren. Los casos ICIJ se muestran como incidentes históricos documentados y no como una red de rutas.

## Referencias y descargas

- UPMRIP, cuadros mensuales 2026: https://portales.segob.gob.mx/es/PoliticaMigratoria/Cuadros_Delitos?Anual=2026&Secc=1
- UPMRIP, portal de delitos y series: https://portales.segob.gob.mx/es/PoliticaMigratoria/Delitos_Perpetrados
- UPMRIP, Boletín Estadístico Cuadro 3.1 (2026): https://www.portales.segob.gob.mx/es/PoliticaMigratoria/CuadrosBOLETIN?Anual=2026&Secc=3
- UPMRIP, definición de eventos de personas en situación migratoria irregular: https://portales.segob.gob.mx/es/PoliticaMigratoria/EvPerMigrIrreg
- OIM DTM, corredor centroamericano (Panamá, Costa Rica, Nicaragua, Honduras, Guatemala y México): https://dtm.iom.int/es/global-overview-of-migration-routes-portal/americas
- OIM DTM, servicio geográfico ArcGIS: https://gisportal.iom.int/arcgis/rest/services/DTM_LAC/Shelter_Service/MapServer
- ICIJ/CLIP, metodología y base de incidentes: https://www.icij.org/inside-icij/2024/04/from-chiapas-to-tamaulipas-new-database-maps-thousands-of-migrants-dangerous-journeys-through-mexico-in-trailer-trucks/
- REDODEM, base de monitoreo de protección (CSV/ZIP, 40,800 filas): https://monitoreo-de-proteccion.redodem.org/csv/base_monitoreo-de-proteccion_redodem.zip
- EAAF, Proyecto Frontera, estadísticas generales al 28 de febrero de 2025: https://eaaf.org/wp-content/uploads/2025/03/Estadisticas_Proyecto-Frontera_Generales_28feb2025-2.pdf
- EAAF, comunicado de identificaciones del 14 de agosto de 2026: https://eaaf.org/identificacion-de-siete-personas-migrantes-desaparecidas-en-estados-unidos/
- RARAMIR: https://portales.segob.gob.mx/es/PoliticaMigratoria/raramir
- Grupos Beta: https://www.datos.gob.mx/dataset/migrantes_atendidos_grupos_beta_proteccion_migrantes
- Directorio ACNUR México: https://help.unhcr.org/mexico/donde-encontrar-ayuda/albergues/
- Mapa de centros de atención OIT: https://www.ilo.org/es/publications/mapa-de-centros-de-atencion-personas-migrantes-en-mesoamerica
- Mapa ferroviario histórico COLMEX: https://repositorio.colmex.mx/concern/archival_documents/765372448?locale=es

## Reproducción de la derivación

Descarga manualmente los cuadros UPMRIP XLS 1.1–1.4 y 2.1–2.4, más `icij_clip_cases.csv`, desde sus portales originales y guárdalos en `insumos_fuente/` con los nombres descritos en el código. Instala `xlrd>=2.0.1` y ejecuta:

```bash
python derive_data.py
```

El script consulta agregados de OIM ArcGIS y reescribe `fuentes_ampliadas.json`. Se necesita conexión de red.

Para los cruces REDODEM, descarga el ZIP oficial de la base de monitoreo en `insumos_fuente/` y ejecuta:

```bash
python preparar_redodem.py --csv insumos_fuente/base_monitoreo-de-proteccion_redodem.zip
```

Para reconstruir el detalle EAAF desde la transcripción estructurada y actualizar el respaldo embebido:

```bash
python preparar_eaaf.py
```

Es una herramienta offline: no se ejecuta al servir el sitio ni desde `construir.py`. Conserva `missing_search_aggregates` (cinco indicadores del Panorama) y escribe `eaaf_public_detail` y `#eaaf-inline-data`.

El script acepta CSV o ZIP, calcula país/destino × grupo etario y género, valida la reconciliación con 40,800 filas y 6,059 destinos, y publica solo los agregados en `runtime/data.json`. El CSV crudo no se copia al build.
