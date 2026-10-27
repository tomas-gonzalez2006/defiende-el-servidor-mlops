from pathlib import Path
import json, csv, textwrap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'informe_mlop_defiende_servidor.pdf'

def page(pdf, title, sections):
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.patch.set_facecolor('white')
    y = 0.94
    fig.text(0.08, y, title, fontsize=18, weight='bold', color='#16324F')
    y -= 0.06
    for heading, body in sections:
        fig.text(0.08, y, heading, fontsize=11, weight='bold', color='#245B7A')
        y -= 0.028
        for paragraph in body.split('\n'):
            for line in textwrap.wrap(paragraph, 96) or ['']:
                fig.text(0.09, y, line, fontsize=8.7, color='#222222')
                y -= 0.019
            y -= 0.008
    fig.text(0.08, 0.035, 'MLOps — Defiende el servidor | Grupo Visualización 2 de 2-4', fontsize=7, color='#666666')
    pdf.savefig(fig, bbox_inches='tight'); plt.close(fig)

with PdfPages(OUT) as pdf:
    page(pdf, 'MLOps — Defiende el servidor', [
        ('Grupo e integrantes', 'Visualización 2 de 2-4\nSuleily Estefania Moreno Contreras\nTomás Alejandro González Forero'),
        ('Objetivo', 'Clasificar conexiones de red como normales (label=0) o ataques (label=1) usando UNSW-NB15, con trazabilidad de datos, código, experimentos y modelos.'),
        ('Datos y procedencia', 'Se utilizaron las particiones publicadas de entrenamiento (175.341 filas) y test (82.332 filas). La fuente de atribución es UNSW-NB15 y la descarga reproducible provino de un mirror fijado a un commit. Los SHA-256 y la advertencia de procedencia están en evidencias/auditoria.json.'),
        ('Integridad', 'Ambas particiones tienen 45 columnas, no presentan valores faltantes y comparten esquema. El entrenamiento contiene 68,1 % de ataques y el test 55,1 %. El análisis encontró duplicados por predictores y grupos con etiquetas contradictorias; se conservaron sin alterar.'),
    ])
    page(pdf, 'Preparación y control de fuga', [
        ('Variables', 'El objetivo es label. Se excluyeron id, label y attack_cat de las entradas del modelo. Las variables categóricas proto, service y state se codifican con OneHotEncoder; las numéricas se escalan con StandardScaler dentro del pipeline.'),
        ('Partición', 'El CSV de entrenamiento se dividió con GroupShuffleSplit, semilla 42 y objetivo de 20 % de grupos en validación. Los grupos se definieron por hash exacto de predictores, excluyendo identificador y etiquetas.'),
        ('Resultado', 'Train: 140.145 filas y 80.832 grupos. Validation: 35.196 filas y 20.208 grupos. Grupos de predictores compartidos entre ambos: 0. La asignación y sus hashes están en evidencias/splits.json.'),
        ('Test', 'El test se auditó descriptivamente sin usar sus etiquetas para escoger modelo o umbral. Se observó solapamiento predictor entre entrenamiento y test en 8.541 filas (10,37 %), por lo que las conclusiones deben interpretarse con cautela.'),
    ])
    page(pdf, 'Experimentos y selección', [
        ('Diseño', 'Se compararon dos familias: regresión logística, árbol de decisión y bosque aleatorio. Las cuatro configuraciones usaron las mismas particiones, semilla 42, pipeline de preprocesamiento y umbral 0,5.'),
        ('Resultados de validación', 'Logística C=0,1: recall 0,9885, precision 0,9210, FPR 0,1834, Macro-F1 0,9202. Logística C=1: recall 0,9870, precision 0,9244, FPR 0,1748, Macro-F1 0,9226. Árbol: recall 0,9714, precision 0,9519, FPR 0,1062, Macro-F1 0,9378. Bosque: recall 0,9827, precision 0,9471, FPR 0,1189, Macro-F1 0,9415.'),
        ('v1 y v2', 'v1 es la regresión logística C=1. v2 es el bosque aleatorio de 100 árboles, profundidad 20 y mínimo 10 observaciones por hoja. v2 fue elegida solo con validación: mejora Macro-F1 y reduce FPR frente a v1, aceptando una pequeña reducción de recall.'),
        ('Trazabilidad', 'Los cuatro run ID y métricas están en evidencias/experimentos.csv. La decisión está congelada en evidencias/seleccion.json, antes de la evaluación final.'),
    ])
    page(pdf, 'Evaluación final y recuperación', [
        ('Test completo', 'v2 se evaluó una sola vez sobre 82.332 filas con umbral 0,5. Recall de ataque: 0,9921. Precision: 0,7959. FPR: 0,3118. Macro-F1: 0,8470. Matriz de confusión [0,1]: [[25464,11536],[357,44975]].'),
        ('Interpretación', 'El modelo detecta la gran mayoría de ataques, pero en test produce más falsos positivos que en validación. Esto puede reflejar cambio de distribución entre particiones y las limitaciones históricas del dataset.'),
        ('Recuperación', 'En un entorno temporal nuevo se recuperaron datos con DVC, v1 y v2 por SHA completo desde Hugging Face, y se predijeron 20 filas fijas de validation. Las etiquetas coincidieron en ambas versiones; la diferencia máxima de score fue 0 para v1 y 4,44e-16 para v2.'),
    ])
    page(pdf, 'Entrega, limitaciones y referencias', [
        ('Artefactos', 'README.md y entrega.md documentan instalación, DVC, MLflow, Hugging Face y reproducción. Las evidencias incluyen auditoría, experimentos, selección, test y recuperación. Los modelos publicados están en suliely/defiende-el-servidor-modelos, ramas v1 y v2.'),
        ('Limitaciones de entrega', 'El remote DVC operativo es local (/home/suleily/dvc-storage). Google Drive no aceptó la cuenta de servicio en Mi unidad por falta de cuota; por ello la recuperación compartida queda pendiente de un almacenamiento autorizado. No se incluyen tokens ni credenciales.'),
        ('Conclusión', 'El pipeline es reproducible localmente y la versión final está identificada por commits, run ID, SHA del modelo y hash del dataset. Antes de entregar al docente debe configurarse un remote DVC compartido y verificarse el acceso de lectura.'),
        ('Referencias', 'UNSW-NB15: https://research.unsw.edu.au/projects/unsw-nb15-dataset\nRepositorio de código: https://github.com/tomas-gonzalez2006/defiende-el-servidor-mlops\nRepositorio de modelos: https://huggingface.co/suliely/defiende-el-servidor-modelos'),
    ])
print(OUT)
