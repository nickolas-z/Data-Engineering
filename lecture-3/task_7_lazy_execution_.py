from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import time

spark = SparkSession.builder.appName("MyGoitSparkSandbox").getOrCreate()
# nuek_df = spark.read.csv('./nuek-vuh3.csv', header=True)
local_file = "/tmp/nuek-vuh3.json"
nuek_df = spark.read.json(local_file)
# # --------- first example ------- lazy 1
# # Start the timer
# start_time = time.time()
#
# nuek_df \
#     .select('call_type') \
#     .where(col("call_type").isNotNull()) \
#     .distinct()
#
# # End the timer
# end_time = time.time()
#
# # Calculate the total processing time
# processing_time = end_time - start_time
# print(f"Processing time: {processing_time:.2f} seconds")

# # --------- second example ------- lazy 2
# start_time = time.time()
#
# nuek_df.select('call_type') \
#     .where(col("call_type").isNotNull()) \
#     .distinct() \
#     .show(1)
#
# end_time = time.time()
# print(f"Processing time: {end_time - start_time:.2f} seconds")

# --------- third example ------- without cache
df1 = nuek_df \
    .filter(col("call_number") > "063520371")

df1.show(1)  # action 1

start_time = time.time()
count = df1.count()  # action 2
print(count)

end_time = time.time()
print(f"Processing time: {end_time - start_time:.2f} seconds")

# --------- # 4th example ------- with cache
df1 = nuek_df \
    .filter(col("call_number") > "063520371") \
    .cache()

df1.show(1)  # action 1, cache happening here

start_time = time.time()
count = df1.count()  # action 2
print(count)

end_time = time.time()
print(f"Processing time: {end_time - start_time:.2f} seconds")
spark.stop()
