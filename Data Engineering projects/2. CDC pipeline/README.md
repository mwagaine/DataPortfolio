# Project overview


## Contents

<ol>
    <li><a href='https://github.com/mwagaine/DataPortfolio/tree/main/Data%20Engineering%20projects/2.%20CDC%20pipeline#description'>Description</a></li>
    <li><a href='https://github.com/mwagaine/DataPortfolio/tree/main/Data%20Engineering%20projects/2.%20CDC%20pipeline#prerequisites'>Prerequisites</a></li>
        <ul>
            <li><a href='https://github.com/mwagaine/DataPortfolio/tree/main/Data%20Engineering%20projects/2.%20CDC%20pipeline#rds-for-postgresql-and-mysql-databases'>RDS for PostgreSQL and MySQL</a></li>
            <li><a href='https://github.com/mwagaine/DataPortfolio/tree/main/Data%20Engineering%20projects/2.%20CDC%20pipeline#s3-bucket'>S3 bucket</a></li>
            <li><a href='https://github.com/mwagaine/DataPortfolio/tree/main/Data%20Engineering%20projects/2.%20CDC%20pipeline#dms-data-migration-service'>DMS (Data Migration Service)</a></li>
            <li><a href='https://github.com/mwagaine/DataPortfolio/tree/main/Data%20Engineering%20projects/2.%20CDC%20pipeline#lambda-and-glue'>Lambda and Glue</a></li>
            <li><a href='https://github.com/mwagaine/DataPortfolio/tree/main/Data%20Engineering%20projects/2.%20CDC%20pipeline#cloudwatch'>CloudWatch</a></li>
            <li><a href='https://github.com/mwagaine/DataPortfolio/tree/main/Data%20Engineering%20projects/2.%20CDC%20pipeline#iam-identity-and-access-management'>IAM (Identity and Access Management)</a></li>
        </ul>
</ol>

## Description 

This project follows on from the previous ETL project, and the aim is to create a CDC pipeline. CDC stands for "Change Data Capture", allowing organisations to not only pool data from different sources into one place, but also make changes to the data at the source that can be quickly reflected in the target storage area. This is very efficient as it saves time having to manually apply changes repeatedly across the board.

Our pipeline will consist of a source database (PostgreSQL) that loads music sales data into a storage folder (S3 bucket) via a migration task - this is known as a full load. This data or load is then written into a final target database (MySQL). Afterwards, changes will be made at the source (e.g. adding, deleting and updating table rows) that will be replicated in the target table. 

Please follow this project in the given order of files:
<ol>
    <li>Lambda function</li>
    <li>Glue job</li>
    <li>Data transformation</li>
    <li>Project review</li>
</ol>


## Prerequisites

Before you start this project, you must set up and access the following AWS services. 

### <ins>RDS for PostgreSQL and MySQL databases</ins>

The source PostgreSQL database would have already been set up in RDS (Relational Database Service) if you completed the previous ETL project. If not, click <a href='https://github.com/mwagaine/DataPortfolio/blob/main/Data%20Engineering%20projects/1.%20ETL%20pipeline/README.md#postgresql-database'>here</a> where you can find details of how to do so. Afterwards, import the data for this project (found in the Data folder) into the database by following <a href='https://learnsql.com/blog/how-to-import-csv-to-postgresql/'>these instructions</a>. If you completed the ETL project, you would have already loaded the data there.

Next, you'll need to create a MySQL database as the ultimate target of the CDC pipeline.

<ol>
    <li>Log-in to your AWS account <a href='https://aws.amazon.com/free/'>here</a> and head to the RDS Management Console.</li>
    <li>Go to <i>Parameter groups</i> and create a custom parameter group for the database group family <i>postgres15</i>.
    <br>
    Then modify the parameter below with the following value:
        <ul>
            <li><i>binlog_format</i> = ROW</li>
        </ul>
    </li>
    <li>Go to <i>Databases</i> and create a free-tier PostgreSQL database running on the engine version <i>PostgreSQL 15</i>, following the instructions <a href='https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Tutorials.WebServerDB.CreateDBInstance.html'>here</a> except:
    <ul>
      <li>In the <i>Connectivity</i> section, select <i>Don’t connect to an EC2 compute resource</i>.</li>
      <li>In the same section, ensure the default VPC, DB subnet group and VPC security group options are selected.</li>
      <li>In the <i>Additional configuration</i> section, leave the initial database name blank.</li>
      <li>In the same section, select the DB parameter group you've just created.</li>
    </ul> 
    <li>In the <i>Additional configuration</i> section, select the DB parameter group you've just created, not the default group available.</li>
    <li>Once created, under the database's <i>Connectivity & security</i> go to <i>Security</i> and click the link under <i>VPC security groups.</i>
    <br>
    Go to <i>Inbound rules</i> and edit the security group's inbound rules so that they only include the follow
    <ul>
      <li><i>Type</i>: All traffic, <i>Source type</i>: Custom, <i>Source</i>: ::/0</li>
      <li><i>Type</i>: All traffic, <i>Source type</i>: Custom, <i>Source</i>: 0.0.0.0/0</li>
      <li><i>Type</i>: MySQL, <i>Source type</i>: Custom, <i>Source</i>: ::/0</li>
      <li><i>Type</i>: MySQL, <i>Source type</i>: Custom, <i>Source</i>: 0.0.0.0/0</li>
    </ul>
    </li>
    <li>Download and install MySQL from here.</li>
    <li>Download and install MySQL driver <a href='https://jdbc.postgresql.org/'>here</a>. You can follow these instructions.</li>
    <li>Open MySQL Workbench on your desktop and connect to the database just created by following <a href='https://dev.mysql.com/doc/workbench/en/wb-mysql-connections-new.html'>these instructions</a>, using the database's endpoint as the hostname.</li>
</ol>


### <ins>S3 bucket</ins>

The Amazon S3 service lets you to store data as .csv files inside directories or buckets. For this task, one S3 bucket will be made to act as the target for the DMS migration task (more on that soon). It will essentially act as staging area in the middle of the pipeline, before the data finally reaches the final target MySQL database. During the full load, data from the source is stored in a .csv titled with the prefix <i>LOAD</i>. Once changes are made to the data at the source, a separate file containing this CDC data (titled with a timestamp) is also added to the same bucket folder.

To create a bucket, go to the S3 management console in AWS and click <i>Create bucket</i>. In the set-up, untick the <i>Block all public access</i></li> box (this isn't usually advisable, but for this project do so to minimise the chances of connection issues).

 
### <ins>DMS (Data Migration Service)</ins>

DMS lets you to migrate data between two different locations. For this project, we will be using DMS to migrate data from our source PostgreSQL database to our S3 bucket. To do so, we need to create a <b>replication instance</b> (which connects the RDS PostgreSQL database to the S3 bucket), <b>two endpoints</b> and <b>a migration task</b> (which will move data from RDS to S3).

To create the replication instance:
<ol>
    <li>Go the DMS Management Console and go to <i>Replication instances</i> to create a new one.
    <li>For <i>Instance class</i>, select dms.t3.micro.</li>
    <li>For <i>Connectivity and security</i>, make sure that the IPv4 network type is selected alongside the default options for VPC, replication subnet groups and VPC security groups.</li>
    <li>In the same section, make sure that <i>Public accessible</i> box is ticked.</li>
</ol>

Next, we need to an endpoint for the PostgreSQL database.
<ol>
    <li>Go the DMS Management Console and go to <i>Endpoints</i> to create a new one.
    <br>
        <ul>
            <li>For <i>Endpoint type</i>, select Source endpoint. </li></li>
            <li>Tick the <i>Select RDS instance</i> box and choose the PostgreSQL database created earlier.</li>
            <li>Under <i>Access to endpoint database</i>, select <i>Provide access information manually</i>.</li>
            <li>For <i>Server name</i>, use the database's endpoint (which can be found by going to the database in RDS and copying/pasting its endpoint link in Connectivity & security tab.</li>
            <li>For <i>Password</i> enter the one used when creating the database, and for <i>Database name</i> enter <i>postgres</i>.</li>
            <li>Run a test connection to the replication instance.</li>
        </ul>
    </li>
</ol>

Afterwards we need to create the endpoint for the S3 bucket.
<ol>
    <li>Go the IAM Management Console and create a new role with a DMS use case, selecting the following policy:
    <br>
        <ul>
            <li><i>S3FullAccess</i></li></li>
        </ul>
    </li>
    <li>Go the DMS Management Console and go to <i>Endpoints</i> to create a new one.
    <br>
        <ul>
            <li>For <i>Endpoint type</i>, select Target endpoint.</li></li>
            <li>Untick the <i>Select RDS instance</i> box.</li>
            <li>Under <i>Target engine</i>, select <i>Amazon S3</i>.</li>
            <li>For <i>Amazon Resource Name (ARN) for service access role</i>, copy and paste the ARN of the IAM role created previously.</li>
            <li>Under <i>Bucket name</i>, use the name of the S3 bucket created earlier.</li>
            <li>Under <i>Bucket folder</i>, create a name of a new folder in the bucket where data will loaded.</li>
            <li>Run a test connection to the replication instance.</li>
        </ul>
    </li>
</ol>

Lastly, let's create the migration task.
<ol>
    <li>Select the replication instance, source endpoint and target endpoint created previously.</li>
    <li>Under <i>Migration type</i>, select <i>Migrate existing data and replicate ongoing changes</i>.</li>
    <li>For <i>Advanced task settings</i>, set the maximum number of tables to load in parallel to 1.</li>
    <li>In <i>Table mappings</i>, add a new selection rule specifying the following:
        <ul>
            <li><i>Schema</i>: Enter a schema</li>
            <li><i>Source name</i>: mwag_pyspark</li>
            <li><i>Source table name</i>: songsales</li>
            <li><i>Action</i>: Include</li>
        </ul>    
    </li>
    <li>For <i>Migration task startup configuration</i>, select <i>Manually later</i>.</li>
</ol>


### <ins>Lambda and Glue</ins>

The final part of the CDC pipeline involves writing data from the S3 bucket to the target MySQL database. Any time new data enters the S3 bucket, this triggers a Lambda function that extracts the location of the file. This then invokes a Glue job which uses this information to read in this file and make any changes, before writing it to MySQL. 

After the full load of the DMS migration task is complete, the S3 bucket will contain one file with the original data before it is written into MySQL. When changes are made to the source data, a second file containing CDC data (i.e. information about the changes made to the data) will also be added to the S3 bucket. Lambda and Glue uses this CDC data to overwrite the target MySQL table with changes made at the source.

Set-up for both the Lambda function and Glue job will take place later on in the project within their respective scripts. 


### <ins>CloudWatch</ins>

This is a handy monitoring service that stores logs of each job that’s being run within AWS. This is great for debugging as you’ll be able to check why and how your Lambda function or Glue job may have failed.


### <ins>IAM (Identity and Access Management)</ins>

At the beginning of some of these AWS set-ups, you would have noticed IAM being involved. In IAM, you can create roles that are assigned to a particular AWS service, giving it permission to access other services to perform tasks that are dependent on them. 

For instance, we needed to give DMS permission to access S3 so that an S3 bucket can be linked to a DMS target endpoint. Later when you create a Lambda function and Glue job, you'll need to give them both access to the services containing the data they'll be reading (i.e. S3 and RDS). You'll also have to give Lambda and Glue access to CloudWatch for their logs to be stored and tracked otherwise you won't be able to troubleshoot any issues.
