# Observatorio de vidas en tránsito · v0.34.0

Prototipo local autocontenido para abrir un tablero de seis vistas, con los gráficos previos del proyecto, una nueva capa de visualizaciones derivadas de UPMRIP, ICIJ/CLIP y OIM DTM, el explorador interactivo del EAAF en Desapariciones y la lectura editorial de motivos, violencias y perpetradores en Atención y perfiles.

## Abrir

Sirve la carpeta por HTTP para que el navegador pueda cargar los JSON:

```bash
python -m http.server 8000 --bind 127.0.0.1
```

Abre `http://127.0.0.1:8000/` desde esta carpeta. No se publica ni se conecta a un servicio de portafolio.

## Gráficas añadidas

- UPMRIP: serie anual 2016–2025; meses enero–septiembre de 2026; desgloses por edad, sexo registrado, nacionalidad individual, delito y entidad de registro.
- REDODEM: el mapa abre Panorama y, debajo, una nota compacta de alcance: **Base analizada: 40,800 registros REDODEM · 2023–2024**, con la advertencia de que son filas de atención u observación, no necesariamente personas distintas ni el total de población migrante. La matriz de edad y sexo conserva los conteos, añade totales por fila y columna que reconcilian con la base y ofrece el selector «Conteos» / «Composición dentro del grupo de edad»; los porcentajes usan el total de cada grupo de edad como denominador. País y destino incluyen los controles «Vista general · Explorar por edad · Explorar por sexo»; los cruces se calcularon desde las filas del CSV oficial. Los cruces de destino usan solo las 6,059 filas con destino distinto de `NA`; las 34,741 `NA` quedan en un indicador aparte. El destino no confirma cruce fronterizo, destino final ni permanencia en México.
- UPMRIP/INM: **«Eventos de personas en situación migratoria irregular registrados en México»**, serie anual 2021–2025 completa y 2026 enero–septiembre parcial. Usa el Cuadro 3.1 del Boletín Estadístico; 2021: 309,692; 2022: 441,409; 2023: 778,907; 2024: 1,234,698; 2025: 155,730; 2026 parcial: 31,077. La serie cuenta eventos administrativos, no personas únicas; 2026 no se proyecta ni se anualiza. 2020 se excluye porque su cuadro reporta «extranjeros presentados» con otra definición y columnas. Fuente y definición: UPMRIP/SEGOB con base en registros del INM.
- UPMRIP/INM, **«Respuesta y alojamiento registrados»**: devoluciones por año y tipo de resolución (Cuadro 3.2.3) en pequeños múltiplos con escalas independientes: total 130,275; 121,963; 54,728; 20,834; 11,804 y 10,829 parcial para 2026. Los tipos son «Eventos de deportación», «Retorno asistido» y «Retorno asistido de niñas, niños o adolescentes»; no se apilan ni se suman con los eventos de movilidad. No se localizó una serie periódica comparable de personas alojadas en estaciones migratorias; el tablero informa ese dato faltante y no dibuja una serie ficticia.
- ICIJ/CLIP: casos documentados por año, entidad, modo de detección y precisión. En el mapa de Panorama se dibujan 148 puntos naranjas con coordenadas; en el mapa hexagonal de Muertes los 148 registros se agregan en hexágonos naranjas, con una fuente conmutable y sin sumarse con MMP.
- Cartografía de Panorama: «Corredor, ferrocarril e incidentes documentados» reúne corredor OIM DTM, incidentes ICIJ/CLIP, red ferroviaria ARTF/IDE y zonas INM 2023. La leyenda está bajo el mapa, las fuentes en un acordeón cerrado y la tabla accesible integra corredor, vías, zonas e incidentes.
- Panorama comparte el lenguaje visual del mapa: base blanca, superficies gris azulado muy tenue, bordes finos, tipografía editorial del mapa y acento índigo. La matriz edad × sexo usa una escala secuencial índigo–lavanda; país y destino usan índigo para la categoría y lavanda para «Otros», con «No especificado» y `NA` en gris. La búsqueda e identificación se presenta en bloques editoriales agrupados por fuente y corte, sin puntos ni líneas que sugieran una evolución. Los colores semánticos del mapa —azul del corredor, naranja de incidentes, morado ferroviario y grises de límites— no cambian y no se reutilizan para demografía.
- OIM DTM: registros agregados por país, tipo de sitio y estado publicado, con recuentos explícitos de los campos incompletos.
- EAAF · Proyecto Frontera: explorador de Desapariciones con los cuatro agregados del corte 28-feb-2025 (2 351 casos no localizados, 2 240 familias, 6 000 donantes de ADN y 406 identificaciones) y los agregados separados del 14-ago-2026 (>2 500 casos y >490 identificaciones). Permite abrir banco o mecanismo, serie anual, entidad de México* —solo después de seleccionar el subtotal— y país de hallazgo para identificaciones. Las barras y la tabla accesible conservan el mismo indicador, unidad, corte y nivel.
- REDODEM · Atención y perfiles (v0.34.0): UpSet de las 14 combinaciones observadas de motivos; matriz de coaparición violencia × perpetrador calculada desde las filas originales, con umbral de privacidad 5; rankings de puntos para 14 violencias y 10 perpetradores; y puntos conectados de cobertura del campo `violencias` por año (2023: 317/22 123; 2024: 182/18 677).
- Tablas accesibles detrás de cada visualización.

Los conteos no se combinan entre fuentes. Las filas de incidentes no son personas únicas. La entidad UPMRIP es entidad de registro; no necesariamente ubicación del hecho. La capa OIM es parcial y no certifica que cada feature sea un albergue activo para población migrante. Los calendarios de «Fechas de registro de MMP y El Paso» se conservan plegados en Fuentes y método, no en Panorama: usan `reported_date` (MMP) y `Pronouncement Date` (El Paso), no fechas de fallecimiento; una celda sin fila fechada no es un cero de muertes ni ausencia de observación.

## Explorador EAAF · decisiones de lectura

- Grano de `eaaf_public_detail`: una observación por indicador × corte × dimensión de desglose × categoría publicada. No son microdatos ni personas identificadas.
- Unidades separadas: casos no localizados, familias participantes, donantes de ADN reportados e identificaciones. No se suman entre sí ni se presentan como fases del mismo conjunto de personas.
- El corte detallado es 28-feb-2025 y cubre 2010–2025. Los años son la fecha del evento que titula cada gráfica (toma/registro, recolección de ADN o identificación), no la fecha de desaparición.
- `México*` es un banco/mecanismo de la fuente y, a la vez, el subtotal del desglose por entidad. Al seleccionarlo se ofrece abrir las 22 entidades publicadas; las entidades ausentes no se imputan a cero. Chiapas y Oaxaca aparecen como bancos separados y no forman parte de ese subtotal.
- El corte 14-ago-2026 solo publica agregados con operador `>`; no tiene desglose comparable y no se interpola ni se conecta como tendencia con 2025.
- El reporte no publica edad, sexo ni nacionalidad para estos indicadores; no se infieren. La transcripción del corte 2025 reconcilió con los totales impresos y sigue pendiente una segunda revisión humana.
- Si `data.json` no está disponible, el explorador y el Panorama EAAF se dibujan con el respaldo embebido `#eaaf-inline-data`; el resto del tablero requiere el servidor local.

## Atención y perfiles · decisiones de lectura

- La unidad es la **fila de atención u observación** del extracto REDODEM 2023–2024: 40,800 filas. No es una persona única, una muestra representativa ni una medida de prevalencia.
- **Motivos:** 6,338 filas con algún motivo, 34,462 con `NA` y 7,863 menciones de categoría. El UpSet cuenta cada fila una vez en su combinación exacta; `NA` no es un motivo y no se reparte entre combinaciones.
- **Violencias × perpetradores:** 469 filas con ambos campos, 30 con violencias pero sin perpetrador, 0 con perpetrador pero sin violencias y 40,301 sin valor en ninguno. Las 469 filas sostienen 950 coapariciones de categoría porque una ficha puede declarar varias violencias y varios perpetradores.
- **Privacidad:** el proyecto no tenía un umbral para esta matriz. Se adopta **5**: las celdas con 1–4 filas se muestran como rango suprimido y no publican la cifra exacta; los pares con 0 filas no se listan. El umbral se declara en la interfaz, el dato y la documentación.
- **Rankings:** 14 categorías de violencia (499 filas con valor; 737 menciones) y 10 de perpetrador (469 filas con valor; 597 menciones). Una fila puede aportar varias menciones; las categorías no son excluyentes ni suman 100 %. «No especificado» es una respuesta explícita, distinta del literal `NA`.
- **Cobertura del campo:** 2023: 317 de 22,123 filas (1,43 %); 2024: 182 de 18,677 filas (0,97 %). La línea solo conecta los dos años: describe la presencia del campo, no la prevalencia ni la evolución de la violencia.

## Inventario

El detalle de las visualizaciones nuevas está en `INVENTARIO_GRAFICAS.md`. La portada incorpora un esquema regional por países descrito por OIM, no una trayectoria vial; el mapa seleccionable de incidentes es histórico 2018–2023 y no representa una ruta migrante.

## Archivos

- `index.html`: aplicación del tablero.
- `burbujas.js`: componente de burbujas empaquetadas (port del Atlas vial, con
  empaquetado circular de d3-hierarchy, ISC). Lo usan los paneles de origen y
  destino en Panorama; Atención y perfiles ya usa UpSet, matriz y rankings de puntos.
- `data.json`: datos derivados de las visualizaciones previas (MMP, El Paso, EAAF y REDODEM), incluidos los agregados de motivos, coaparición y cobertura anual.
- `fuentes_ampliadas.json`: agregados y puntos publicados necesarios para esta ampliación.
- `derive_data.py`: reproducción de agregados UPMRIP/ICIJ/ArcGIS a partir de fuentes descargadas localmente y del servicio ArcGIS.
- `preparar_redodem.py`: calcula y publica en `web/data.json` los cruces país/destino × grupo etario y género, el UpSet de motivos, la matriz de coaparición con umbral de privacidad y la cobertura anual desde el CSV oficial de REDODEM; valida filas, menciones, combinaciones y coapariciones con identificadores de fila distintos.
- `preparar_eaaf.py`: herramienta offline que reconstruye `eaaf_public_detail` desde la transcripción estructurada del PDF y actualiza el respaldo embebido. No forma parte del runtime ni se ejecuta en `construir.py`. Uso: `python pipeline/preparar_eaaf.py` desde la raíz del clon.
- `FUENTES_Y_LIMITES.md`: fuentes, definiciones, periodos, licencias y exclusiones.

Los archivos de origen XLS y CSV no se redistribuyen en este paquete. El script espera que se descarguen manualmente a la carpeta de insumos excluidos, con los nombres indicados en `FUENTES_Y_LIMITES.md` y en `pipeline/README.md`.
