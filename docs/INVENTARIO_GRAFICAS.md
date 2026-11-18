# Inventario de visualizaciones v0.34.0

## Gráficas nuevas por fuente

### Corredor regional

1. Esquema por países del corredor centroamericano descrito por OIM DTM (Panamá–México). No representa caminos exactos.

### UPMRIP

2. Serie anual de victimización declarada (2016–2025).
3. Corte mensual preliminar (enero–septiembre 2026).
4. Categorías específicas de delito en la serie 2016–2025.
5. Edad registrada (adultos / niñas, niños y adolescentes) por año.
6. Sexo registrado H/M por año.
7. Nacionalidades individuales por acumulado anual.
8. Nacionalidades individuales en enero–septiembre 2026.
9. Edad por mes en 2026.
10. Sexo por mes en 2026.
11. Entidad de registro acumulada (2016–2025).
12. Categorías específicas de delito en 2026.

### ICIJ / CLIP

13. Incidentes documentados por año.
14. Mapa de las 148 filas con coordenadas (punto seleccionable; color por precisión).
15. Incidentes por entidad.
16. Modo de detección registrado.
17. Precisión de coordenadas.

### OIM DTM · Shelter Service

18. Features registrados por país.
19. Etiquetas publicadas de tipo de sitio.
20. Completitud de campos de tipo, estado y coordenadas.

Cada visualización incluye tabla accesible. Los paneles KPI son métricas auxiliares, no cuentan como gráficas independientes. Las 13 áreas preexistentes de MMP, El Paso, EAAF y REDODEM permanecen en la primera parte del tablero.

## Cambio de forma en la serie REDODEM (v0.13.2)

Las gráficas categóricas de la sección «04 — REDODEM · universo de atención» ya no
usan puntos sueltos ni barras: usan el componente de burbujas empaquetadas del
Atlas vial (`burbujas.js`), con el área proporcional al conteo. Las cifras, los
títulos, las notas y los denominadores son los mismos de esta lista.

- 03 Origen declarado → 8 burbujas; «No especificado» (307) fuera del empaquetado.
- 04 Destino capturado → 8 burbujas; «NA» (34,741) fuera del empaquetado.
- 05 Motivos generales → 4 burbujas de menciones.
- 07 Violencias (14) y perpetradores (10) → burbujas en lugar de barras.

El mapa, la serie anual, la matriz edad × género y la trama de cobertura no
cambian de forma.


## Mapa hexagonal (v0.15.0)

21. Mapa hexagonal de muertes y desapariciones documentadas (OIM Missing Migrants
    Project con coordenadas), con modos Muertes/Desapariciones, medida de
    incidentes o personas, filtro por año, capas contextuales conmutables, ficha
    por celda, zoom/arrastre y tabla accesible. No es una gráfica de las fuentes
    anteriores: añade el universo georreferenciado de MMP y conserva separados
    MMP, El Paso, EAAF y REDODEM.

22. Eventos de personas en situación migratoria irregular registrados en México
    (UPMRIP/SEGOB, Cuadro 3.1, base INM), 2021–2025 completos y 2026
    enero–septiembre parcial. Columnas anuales, tooltips con estado del periodo,
    leyenda de año completo/parcial y tabla accesible. No se anualiza 2026 ni se
    suma con REDODEM; 2020 se excluye por definición y columnas distintas.

23. Respuesta y alojamiento registrados (UPMRIP/SEGOB, Cuadro 3.2.3):
    pequeños múltiplos por año para total de personas devueltas, eventos de
    deportación, retorno asistido y retorno asistido de NNA, con escalas
    independientes y 2026 parcial. No se apilan las medidas. La vista de
    alojamiento se deja fuera porque no se localizó una serie periódica
    comparable; se informa el dato faltante.

24. Explorador EAAF de Desapariciones (v0.33.0): cuatro indicadores del corte
    28-feb-2025 con barras y tabla accesible por banco/mecanismo, serie anual y
    entidad de México*; las identificaciones añaden el país de hallazgo. El
    subtotal México* se abre a 22 entidades y las ausentes no se imputan a cero.
    El corte 14-ago-2026 se muestra aparte, solo con >2 500 casos y >490
    identificaciones, sin desglose ni tendencia. Las barras y la tabla conservan
    el mismo indicador, unidad, corte y nivel de categoría.

25. UpSet de combinaciones de motivos (v0.34.0): 14 combinaciones observadas,
    barras de filas, matriz de pertenencia a las cuatro categorías y detalle
    agregado. Las 34,462 filas con `NA` se informan aparte; no son un motivo.
    Tabla accesible con combinación, filas y número de categorías.

26. Matriz de coaparición violencia × perpetrador (v0.34.0): 14 × 10 categorías,
    celdas calculadas desde filas originales con identificador sintético de
    posición; 469 filas con ambos campos, 30 solo violencias, 0 solo
    perpetradores y 40,301 sin valor en ninguno. Umbral de privacidad 5: 38
    celdas visibles, 38 suprimidas como `1–4` y 64 pares con 0 fuera de la
    matriz. La tabla accesible no publica cifras exactas de celdas suprimidas.

27. Ranking de puntos de violencias (v0.34.0): 14 categorías, 737 menciones y
    499 filas con valor; denominador separado y tabla completa.

28. Ranking de puntos de perpetradores (v0.34.0): 10 categorías, 597 menciones y
    469 filas con valor; «No especificado» se conserva como respuesta explícita
    (7 menciones, 3 filas que solo declaran esa categoría).

29. Cobertura del campo `violencias` por año de captura (v0.34.0): puntos
    conectados 2023 (317/22,123; 1.43 %) y 2024 (182/18,677; 0.97 %), con
    numerador, denominador y NA; la línea no es una tendencia ni una medida de
    prevalencia.
