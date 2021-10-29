from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.sql.types import StructType
from pyspark.sql.types import StringType
from pyspark.sql.functions import col,from_json
import os
## install pip3 install pyspark-stubs==2.3.0
# from pyspark.streaming.kafka import KafkaUtils

BROKER = os.getenv("KAFKA_BROKER")
BROKER = BROKER if BROKER !=None else 'kafka:9092'
TOPIC = os.getenv("TOPIC")
TOPIC = TOPIC if TOPIC !=None else 'newsfeeds'

sc = SparkContext(appName="RssConsumer")
ssc = StreamingContext(sc, 5)
ss = SparkSession.builder.master("local[1]").appName("Something").getOrCreate()

ss.sparkContext.setLogLevel('WARN')

# ks = KafkaUtils.createDirectStream(ssc, ['newsfeeds'], {'metadata.broker.list': 'kafka:9092'})

df = ss.readStream\
    .format("kafka")\
    .option("kafka.bootstrap.servers", BROKER)\
    .option("subscribe", TOPIC)\
    .option("failOnDataLoss", "false") \
    .option("startingOffsets", "earliest").load()

df.printSchema()


schema = StructType()\
            .add("id",StringType())\
            .add("title", StringType())\
            .add("published_time", StringType())\
            .add("summary",StringType())\
            .add("source",StringType())\
            .add("category",StringType())
# df.select( \
#   col("key").cast("string"),
#   from_json(col("value").cast("string"), schema))
datadf = df.select(from_json(col("value").cast("string"), schema).alias("datavol")).select("datavol.*")

##datadf = df.select(col("value").cast("string"))

query = datadf\
    .writeStream\
    .outputMode("append")\
    .trigger(processingTime="10 seconds")\
    .format("csv")\
    .option("header",True)\
    .option("checkpointLocation", "file:///app/datavol/raw/checkpoint/")\
    .option("path", "file:///app/datavol/raw/newsfeeds/")\
    .start().awaitTermination()

# csvDF = spark \
#     .readStream \
#     .option("sep", ";") \
#     .schema(userSchema) \
#     .csv("/path/to/directory")






# ks = KafkaUtils.createDirectStream(ssc, ['newsfeeds'], {'metadata.broker.list': 'localhost:9092'})
# lines = ks.map(lambda x: x[1])


