## This program is to read the datavol and clense the date
from pyspark.sql import SparkSession
from pyspark.sql import Window
from pyspark.sql.functions import  col, row_number,regexp_replace,desc,split,coalesce,lit,concat_ws,trim,upper
from category_cleanup import category_mapping
from pyspark.sql.functions import udf
from pyspark.sql.types import *
quotes_match_expression = """\'|\"|,"""

def refine_category(x):
    try:
        category       = category_mapping[x]
    except:
        category = x
    return category

refine_category_udf = udf(refine_category, StringType())

def cleanseData(kaggle_data_set,input_data_set,cleansed_output_dir):
    spark           = SparkSession.builder.master("local[2]")\
                                    .appName("SparkByExamples.com")\
                                    .getOrCreate()

    ## This would have the fields {id, title,published_time,summary,source,category}
    kaggledf        = spark.read.csv(kaggle_data_set, quote="\"",header=True)
    rssfeed         = spark.read.csv(input_data_set, quote="\"",header=True)


    df              = kaggledf.unionAll(rssfeed)\
                              .withColumn("categoryU",refine_category_udf(upper(trim(col("category")))))\
                              .drop(col("category"))\
                              .withColumnRenamed("categoryU","category")


    firstRowWindow  = Window.partitionBy("id").orderBy(desc("published_time"))
    deduped_df      = df.withColumn("rn", row_number().over(firstRowWindow))\
                        .where(col("rn") == 1).drop(col("rn"))
    ## Clean the datavol
    ##.withColumn("bare_summary", substring(col("summary1"), 1, locate(col("summary1"), image_tag_starting))) \
        # .drop(col("title"),col("summary"),col("summary1"))\


    refined_df      = deduped_df.filter(col("published_time").isNotNull()) \
                        .withColumn("title1", regexp_replace(col("title"), quotes_match_expression, "")) \
                        .withColumn("summary1", regexp_replace(col("summary"), quotes_match_expression, "")) \
                        .withColumn("bare_summary", split("summary1", "<img")[0])\
                        .select(col("id"),
                                col("published_time"),
                                coalesce(col("title1"),lit("-")).alias("title"),
                                coalesce(col("bare_summary"),lit("-")).alias("summary"),
                                col("source"),
                                coalesce(col("category"),lit("others")).alias("category"))\
                        .withColumn("text",trim(concat_ws(" ", trim(col("title")), trim(col("summary")))))\
                        .filter(col("text")!="--")\
                        .filter(col("category").isNotNull())
    refined_df.show()

    categoryCountDF = refined_df.groupby(col("category")).count()
    categoryCountDF.show(100)
    print(f"cleansed_output_dir={cleansed_output_dir}")
    ##So just a single part- file will be created
    refined_df.coalesce(1) \
    .write.mode("overwrite") \
    .option("mapreduce.fileoutputcommitter.marksuccessfuljobs","false") \
    .option("header","true") \
    .csv(cleansed_output_dir)
