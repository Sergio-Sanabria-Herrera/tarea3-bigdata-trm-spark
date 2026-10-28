import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, year, to_date

spark = SparkSession.builder \
    .appName("VisualizacionTRM") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Cargar dataset desde HDFS
ruta = "hdfs://localhost:9000/Tarea3/rows.csv"

df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv(ruta)

# Limpieza y transformación
df = df.dropna(subset=["VALOR", "VIGENCIADESDE"])

df = df.withColumn(
    "VIGENCIADESDE",
    to_date(col("VIGENCIADESDE"), "dd/MM/yyyy")
)

df = df.withColumn(
    "ANIO",
    year(col("VIGENCIADESDE"))
)

# Promedio por año
promedio = df.groupBy("ANIO") \
    .agg(avg("VALOR").alias("PROMEDIO_TRM")) \
    .orderBy("ANIO")

datos = promedio.collect()

anios = [fila["ANIO"] for fila in datos]
valores = [fila["PROMEDIO_TRM"] for fila in datos]

# Crear gráfica
plt.figure(figsize=(12, 6))
plt.plot(anios, valores, marker="o")
plt.title("Promedio anual de la TRM en Colombia")
plt.xlabel("Año")
plt.ylabel("TRM promedio (COP)")
plt.grid(True)
plt.tight_layout()

plt.savefig("trm_promedio_anual.png", dpi=150)

print("Grafica creada correctamente: trm_promedio_anual.png")

spark.stop()
