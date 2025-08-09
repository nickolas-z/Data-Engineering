from pyspark.sql import SparkSession
# from pyspark.sql.functions import col
import pyspark.sql.functions as F

spark = SparkSession.builder.appName("MyGoitSparkSandbox").getOrCreate()
# nuek_df = spark.read.csv('./nuek-vuh3.csv', header=True)
local_file = "/tmp/nuek-vuh3.json"
nuek_df = spark.read.json(local_file)

nuek_df.select("received_dttm", "response_dttm").printSchema()

# df = nuek_df.select('call_type') \
#       .where(F.col("call_type").isNotNull()) \
#       .distinct()

# df.show()

spark.stop()
