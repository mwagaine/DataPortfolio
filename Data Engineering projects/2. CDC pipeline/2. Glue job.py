# Databricks notebook source
# MAGIC %md
# MAGIC ## Setting-up the Glue job
# MAGIC <br>
# MAGIC <ol>
# MAGIC   <li>Log-in to AWS and head to the IAM Management Console to create a new role with a Glue use case, attaching the following policies:
# MAGIC     <ul>
# MAGIC       <li><i>S3FullAccess</i></li>
# MAGIC       <li><i>RDSFullAccess</i></li>
# MAGIC       <li><i>CloudWatchFullAccess</i></li>
# MAGIC     </ul>
# MAGIC   </li>
# MAGIC   <li>Go to the AWS Glue Studio and create a new job, selecting the option <i>Spark script editor</i>.
# MAGIC   <br>
# MAGIC   In the <i>Job details</i> tab, do the following:
# MAGIC     <ul>
# MAGIC       <li>For <i>Name</i>, use the same JobName defined in the Lambda function script <a href='#'>here</a>.</li>
# MAGIC       <li>For <i>IAM role</i>, select the role you have just created.</li>
# MAGIC       <li>Change the <i>Requested number of workers</i> to 2.</li>
# MAGIC     </ul>
# MAGIC   </li>
# MAGIC   <li>In the <i>Script</i>, delete the default code present and replace it with the code in this notebook below, before clicking <i>Save</i>.</li>
# MAGIC </ol>

# COMMAND ----------

# Import libraries
from awsglue.utils import getResolvedOptions
import sys
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import when

# Derive S3 location from which data will be extracted
args = getResolvedOptions(sys.argv,['s3_target_path_key','s3_target_path_bucket'])
bucket = args['s3_target_path_bucket']
fileName = args['s3_target_path_key']
print(bucket, fileName)
inputFilePath = f"s3a://{bucket}/{fileName}"

# Initialise Spark session to build dataframes where this data will be transformed
spark = SparkSession.builder.appName("CDC").getOrCreate()

# Prepare schema for this data
schema = StructType([
                    StructField("ChartDate_WeekEnding", DateType(), True),
                    StructField("Song", StringType(), True),
                    StructField("Artists", StringType(), True),
                    StructField("Sales", IntegerType(), True)])

# Prepare credentials to load transformed data into the target database
driver = "com.mysql.jdbc.Driver"
url = "jdbc:mysql://{insert database endpoint url}/"
table = "matt_schema.songsales"
user = "{insert database username}"
password = "{insert database password}"

# Read full load data into input dataframe
if "LOAD" in fileName:
    inputDF = spark.read.schema(schema).csv(inputFilePath)
    inputDF = inputDF.withColumnRenamed("_c0","ChartDate_WeekEnding").withColumnRenamed("_c1","Song").withColumnRenamed("_c2","Artists").withColumnRenamed("_c3","Sales")
    
    # Write original source data to target database
    inputDF.write.mode("overwrite").format("jdbc").option("driver", driver).option("url", url).option("dbtable", table).option("truncate", "true").option("mode", "append").option("user",user).option("password", password).save()

# Now consider what happens after the source data has been transformed        
else:
    # Read CDC data into info dataframe
    nu_schema = StructType([
                    StructField("Action", StringType(), True),
                    StructField("ChartDate_WeekEnding", DateType(), True),
                    StructField("Song", StringType(), True),
                    StructField("Artists", StringType(), True),
                    StructField("Sales", IntegerType(), True)])
    infoDF = spark.read.schema(nu_schema).csv(inputFilePath)
    infoDF = infoDF.withColumnRenamed("_c0","Action").withColumnRenamed("_c1","ChartDate_WeekEnding").withColumnRenamed("_c2","Song").withColumnRenamed("_c3","Artists").withColumnRenamed("_c4","Sales")

    # Read data from target database into output dataframe
    outputDF = spark.read.format("jdbc").option("driver", driver).option("url", url).option("dbtable", table).option("user", user).option("password", password).load(schema=schema)
    outputDF = outputDF.withColumnRenamed("_c0","ChartDate_WeekEnding").withColumnRenamed("_c1","Song").withColumnRenamed("_c2","Artists").withColumnRenamed("_c3","Sales")
    
    # Transform output dataframe based on information inside info dataframe
    for row in infoDF.collect():
        # Update rows
        if row['Action'] == 'U':
            outputDF = outputDF.withColumn("Artists", when(outputDF["ChartDate_WeekEnding"] == row["ChartDate_WeekEnding"], row["Artists"]).otherwise(outputDF["Artists"]))
        # Insert rows
        elif row['Action'] == 'I':
            insertedRow = [list(row)[1:]]
            newDF = spark.createDataFrame(insertedRow, schema)
            outputDF = outputDF.union(newDF)
        # Delete rows    
        elif row['Action'] == 'D':
            outputDF = outputDF.filter(outputDF.ChartDate_WeekEnding != row['ChartDate_WeekEnding'])
        
    # Finally, overwrite data in the target database with the final output data
    outputDF.write.mode("overwrite").format("jdbc").option("driver", driver).option("url", url).option("dbtable", table).option("truncate", "true").option("mode", "append").option("user",user).option("password", password).save()
