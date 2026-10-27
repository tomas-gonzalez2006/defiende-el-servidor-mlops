---
name: acceso-a-los-datos
description: "Use when obtaining, validating, versioning, or recovering the UNSW-NB15 training and test CSVs for the MLOps workshop. Covers source checks, SHA-256 verification, data auditing, DVC storage, and safe access."
---

# Acceso a los datos

Guía para obtener y recuperar los datos del taller MLOps "Defiende el servidor" sin perder su procedencia ni contaminar la evaluación.

## Alcance y reglas

- Usa únicamente `UNSW_NB15_training-set.csv` (175,341 filas) y `UNSW_NB15_testing-set.csv` (82,332 filas). No descargues PCAP ni el conjunto original completo.
- La fuente oficial de UNSW es la referencia de atribución. Si se usa el mirror de terceros mencionado en el material del taller, verifica las huellas de esta skill; esas huellas no autentican el archivo oficial.
- No inventes ni adivines URL de descarga. Localiza los enlaces oficiales o los enlaces del mirror en la documentación vigente del dataset o en las comunicaciones del curso.
- Mantén intactos los archivos recibidos. Guarda por separado los datos originales y los datos preparados con sus particiones; registra la transformación.
- No uses etiquetas de test ni sus métricas para escoger modelos, transformaciones o umbrales. El test completo se reserva para la evaluación final.
- Nunca copies tokens, contraseñas, datos personales innecesarios o credenciales a código, Git, archivos DVC, registros o mensajes.

## Huellas conocidas del mirror

SHA-256 de los CSV sin comprimir:

| Archivo | SHA-256 |
|---|---|
| `UNSW_NB15_training-set.csv` | `bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa` |
| `UNSW_NB15_testing-set.csv` | `734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559` |

Compara la huella calculada con la esperada solo cuando el archivo provenga de ese mirror. Si no coincide, no lo uses como si fuera el archivo esperado: conserva el original, revisa la fuente y reporta la discrepancia.

## Procedimiento

1. **Revisa antes de descargar.** Inspecciona README, configuración de DVC, directorios de datos y remotes existentes. Sigue las convenciones del proyecto; si no existen, usa una ubicación explícita como `data/raw/`. No sobrescribas archivos ni cambies un remote existente.
2. **Obtén las dos particiones.** Descarga los CSV publicados desde la fuente verificada. Anota URL o referencia de origen y fecha de descarga. No sustituyas los archivos por copias renombradas de otro split.
3. **Verifica contenido e integridad.** Calcula SHA-256 y compara con la huella del mirror si corresponde. Comprueba además los nombres y tamaños esperados de las particiones, encabezados, número de filas y estructura CSV. El nombre del archivo por sí solo no prueba que sea el dataset correcto. Si la fuente oficial entrega archivos distintos, documenta sus huellas y procedencia sin atribuirles las huellas del mirror.
4. **Audita antes de preparar.** Registra fuente, fecha, huellas, filas, columnas, clases, faltantes y tipos. Cuenta duplicados por variables predictoras, excluyendo identificadores y etiquetas; detecta entradas idénticas con etiquetas contradictorias y documenta la política adoptada.
5. **Evita fuga de información.** El objetivo es `label` (0 = normal, 1 = ataque). Excluye `label`, `attack_cat` e `id` de las entradas del modelo. Conserva `id` solo para auditoría y para asociar predicciones a filas. Forma entrenamiento y validación solo desde el CSV de entrenamiento; no separes duplicados entre ambas. Ajusta cualquier transformación solo con entrenamiento. Mantén las particiones y la semilla fijas en todos los experimentos.
6. **Prepara y versiona.** Conserva con DVC una versión de los archivos recibidos y otra de los datos preparados y particiones. Usa los directorios y comandos ya establecidos en el proyecto. Añade a Git los archivos de seguimiento DVC y las referencias necesarias, no los datos grandes ni las credenciales. Documenta cómo reproducir la preparación.
7. **Comprueba el almacenamiento remoto.** Antes de subir, confirma que el remote DVC previsto es el autorizado y accesible por el equipo/docente. Si no existe o su destino/permisos no están claros, detente y pide confirmación; no publiques datos ni cambies permisos por iniciativa propia. Protege las credenciales mediante el mecanismo local aprobado y prueba que los datos pueden recuperarse sin depender de la caché local.
8. **Recupera en un entorno limpio.** Desde la revisión Git que se desea comprobar, sigue el README del proyecto y recupera las versiones con DVC desde el almacenamiento entregado. Recalcula las huellas y compara con la evidencia registrada. Guarda los comandos, resultados y errores; no los presentes como recuperación satisfactoria si faltan archivos o no coinciden las huellas.
9. **Limita el uso del test.** Puedes inspeccionar esquema, duplicados y solapamientos sin usar las etiquetas para tomar decisiones. Evalúa una sola vez el modelo y umbral congelados, usando todas las filas de test, y conserva predicciones y métricas recalculables.

## Si falla el acceso

- Distingue entre URL caída, error de descarga, huella incorrecta, remote DVC no disponible y falta de permisos; conserva el mensaje de error sin incluir secretos.
- Reintenta únicamente con una fuente verificada y no reemplaces un archivo válido por una descarga parcial.
- Si no puedes verificar el origen o recuperar desde el almacenamiento entregado, informa el bloqueo al responsable/docente por el canal del curso antes del cierre. No cambies silenciosamente la fuente o la partición.
