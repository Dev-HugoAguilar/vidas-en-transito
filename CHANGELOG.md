# Historial de cambios

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y
las versiones usan [Versionado Semántico](https://semver.org/lang/es/).

## [1.0.0] — 2026-11-26

### Añadido

- Primera publicación como repositorio independiente.
- Tablero autocontenido con seis vistas: Panorama, Muertes, Desapariciones,
  Contexto, Rutas y Método.
- Capas de Panorama: corredor OIM DTM, incidentes ICIJ/CLIP, red ferroviaria y
  zonas INM, con leyenda, fuentes y tabla accesible.
- Mapa hexagonal de muertes con fuente conmutable, sin sumarse con otros
  registros.
- Explorador EAAF con cuatro unidades separadas y dos cortes que no se enlazan
  como tendencia.
- Eventos registrados por UPMRIP (Cuadro 3.1) y devoluciones por tipo de
  resolución (Cuadro 3.2.3), sin anualizar el corte parcial de 2026.
- Bloque REDODEM «Atención y perfiles»: UpSet de motivos, matriz de coaparición
  violencia × perpetrador con **umbral de privacidad 5**, rankings de menciones y
  cobertura anual del campo.
- Contrato de datos ejecutable en `tests/test_datos.py`, incluida una guarda que
  falla si se versionan insumos crudos.
- Documentación de fuentes, cartografía, inventario de gráficas y método.

### Nota

Los XLS y CSV de origen no se redistribuyen: se publican solo los agregados.
El proyecto se extrae del portafolio de datos de Hugo Aguilar.
