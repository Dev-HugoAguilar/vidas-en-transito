# Política de seguridad

## Alcance

El tablero se ejecuta por completo en el navegador sobre JSON estáticos. No procesa datos personales: publica agregados con umbral de privacidad. Los insumos crudos de las fuentes no se redistribuyen.



## Cómo reportar

Si encuentras una vulnerabilidad, usa los **avisos privados de seguridad** de
GitHub: pestaña *Security* → *Report a vulnerability*. Evita abrir un *issue*
público con detalles explotables.

Incluye, cuando aplique:

- versión o commit afectado;
- pasos mínimos para reproducir;
- impacto esperado y observable;
- cualquier mitigación que ya hayas probado.

## Buenas prácticas para quien despliega

- No añadas credenciales al repositorio; usa variables de entorno.
- Sirve la demo detrás de HTTPS si la expones fuera de `127.0.0.1`.
- Revisa el resultado de la verificación de credenciales de la integración
  continua antes de fusionar cambios.

Este es un proyecto de portafolio mantenido de forma individual: se revisan los
reportes por orden de llegada y se responde con una evaluación inicial cuando el
reporte contiene pasos reproducibles.
