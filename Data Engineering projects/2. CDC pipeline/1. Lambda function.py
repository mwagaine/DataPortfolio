# Databricks notebook source
# MAGIC %md
# MAGIC ## Lambda function
# MAGIC
# MAGIC Log-in to your AWS account, head to the Lambda Console and select the the Lambda function you created previously as per the instructions <a href='https://docs.aws.amazon.com/lambda/latest/dg/with-s3-example.html'>here</a>.
# MAGIC
# MAGIC Then, you can add the following script to the 

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setting-up the Lambda function
# MAGIC <br>
# MAGIC <ol>
# MAGIC   <li>Log-in to AWS and head to the IAM Management Console to create a new role with a Lambda use case, attaching the following policies:
# MAGIC     <ul>
# MAGIC       <li><i>S3FullAccess</i></li>
# MAGIC       <li><i>CloudWatchFullAccess</i></li>
# MAGIC     </ul>
# MAGIC   </li>
# MAGIC   <li>Go to the Lambda Console and create a new function, selecting the option <i>Author from scratch</i>.
# MAGIC   <br>
# MAGIC   In the <i>Change default execution role</i> section, select <i>Use an existing role</i> to add the IAM role you've created.
# MAGIC   </li>
# MAGIC   <li>Once the function has been created, add an S3 trigger. Select the bucket created earlier and used for DMS where data will be loaded into.
# MAGIC   <li>In the <i>Code</i> tab, delete the default code present and replace it with the code in this notebook below, before clicking <i>Deploy</i>.</li>
# MAGIC </ol>

# COMMAND ----------

# Import libraries
import json
import boto3

# Create function to extract the filename of the data and the name of its S3 bucket
def lambda_handler(event, context):
    
    bucketName = event["Records"][0]["s3"]["bucket"]["name"]
    fileName = event["Records"][0]["s3"]["object"]["key"]

    glue = boto3.client('glue')
    
    # The JobName specified here should be used when naming the Glue job to be created in the next step of this project
    response = glue.start_job_run(
        JobName = 'glueCDC-pyspark',
        Arguments = {
            '--s3_target_path_key': fileName,
            '--s3_target_path_bucket': bucketName
        } 
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
