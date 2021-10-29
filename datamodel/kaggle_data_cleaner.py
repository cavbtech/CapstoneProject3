## This program is to read the datavol and clense the date
from pyspark.sql import SparkSession
from pyspark.sql import Window
from pyspark.sql.functions import  \
    col, row_number,regexp_replace,date_format,split,coalesce,lit,concat_ws,substring,to_timestamp,count

quotes_match_expression = """\'|"\|\\n|\\r"""

def cleanseData(input_data_set,cleansed_output_dir):
    spark           = SparkSession.builder.master("local[1]")\
                                    .appName("SparkByExamples.com")\
                                    .getOrCreate()

    ## This would have the fields {id, title,published_time,summary,source,category}
    df              = spark.read.csv(input_data_set, header=True,escape="\\",quote="\"")

    ## Clean the datavol
    ##.withColumn("bare_summary", substring(col("summary1"), 1, locate(col("summary1"), image_tag_starting))) \
        # .drop(col("title"),col("summary"),col("summary1"))\


    refined_df      = df.filter(col("published_date").isNotNull()) \
                        .withColumn("published_time",
                                    date_format(to_timestamp(substring(col("published_date"),1,10),'yyyy-MM-dd'),'yyyyMMddHHmmss'))\
                        .withColumn("title1", regexp_replace(col("title"), quotes_match_expression, "")) \
                        .withColumn("summary1", regexp_replace(col("summary"), quotes_match_expression, "")) \
                        .withColumn("bare_summary", split("summary1", "<img")[0])\
                        .select(col("_id").alias("id"),
                                col("published_time"),
                                coalesce(col("title1"),lit(" ")).alias("title"),
                                coalesce(col("bare_summary"),lit(" ")).alias("summary"),
                                col("clean_url").alias("source"),
                                col("topic").alias("category"))\
                        .filter(col("published_time").isNotNull())\
                        .filter(col("category").isNotNull())

    refined_df = refined_df.withColumn("count_data",count("id")
                                       .over(Window.partitionBy("category")))\
                                        .where(col("count_data")>20)

    ##So just a single part- file will be created
    refined_df\
        .select("id","title","published_time","summary","source","category")\
        .coalesce(1) \
    .write.mode("overwrite") \
    .option("mapreduce.fileoutputcommitter.marksuccessfuljobs","false") \
    .option("header","true") \
    .csv(cleansed_output_dir)

cleanseData("C://Users/srinivasa/Downloads/news_articles/news_articles.csv","../datavol/raw/kagglestatic/")