from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, min, max, year, to_date

spark = SparkSession.builder \
    .appName("AnalisisTRM") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 1. Cargar dataset desde HDFS
ruta = "hdfs://localhost:9000/Tarea3/rows.csv"

df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv(ruta)

print("\n=== DATOS ORIGINALES ===")
print("Cantidad de registros:", df.count())
df.show(10)

# 2. Limpieza
df_limpio = df.dropna(subset=["VALOR", "VIGENCIADESDE"])

df_limpio = df_limpio.withColumn(
    "VIGENCIADESDE",
    to_date(col("VIGENCIADESDE"), "dd/MM/yyyy")
)

print("\n=== DESPUES DE LA LIMPIEZA ===")
print("Cantidad de registros:", df_limpio.count())

# 3. Analisis exploratorio
print("\n=== ESTADISTICAS GENERALES ===")
df_limpio.select("VALOR").describe().show()

print("\n=== VALOR MINIMO, MAXIMO Y PROMEDIO ===")
df_limpio.select(
    min("VALOR").alias("TRM_MINIMA"),
    max("VALOR").alias("TRM_MAXIMA"),
    avg("VALOR").alias("TRM_PROMEDIO")
).show()

# 4. Transformacion: obtener año
df_anual = df_limpio.withColumn(
    "ANIO",
    year(col("VIGENCIADESDE"))
)

# 5. Promedio de TRM por año
print("\n=== PROMEDIO DE TRM POR AÑO ===")
promedio_anual = df_anual.groupBy("ANIO") \
    .agg(avg("VALOR").alias("PROMEDIO_TRM")) \
    .orderBy("ANIO")

promedio_anual.show(50, truncate=False)

# 6. Valores mas altos registrados
print("\n=== 10 VALORES MAS ALTOS DE TRM ===")
df_limpio.select(
    "VALOR",
    "VIGENCIADESDE",
    "VIGENCIAHASTA"
).orderBy(col("VALOR").desc()).show(10, truncate=False)

spark.stop()
