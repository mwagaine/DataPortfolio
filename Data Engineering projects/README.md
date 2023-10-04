# CDC project overview


## Contents

<ol>
    <li>Project description</li>
    <li>Project prerequisites</li>
    <li></li>
</ol>

## Description 

This project follows on from the previous ETL project. The aim of this project is to create a CDC pipeline. CDC stands for "Change Data Capture", allowing organisations to not only pool data from different databases into one place, but also make changes to the original data in their sources that can be quickly reflected in the [target]. This is very efficient as it saves time having to manually apply these changes twice again to the target database.

Our pipeline will consist of a source database (PostgreSQL) that loads data into a storage bucket (S3) via a migration task, before the same data is written into a target database (MySQL). When changes are made to the source, CDC data is loaded into the storage bucket before. 

The data used in this project is the same data that was funnelled through my previous ETL project which can be found <a href='#'>here</a>. You can also download the data from the file in this repositry.

Please follow this project in the given order of files:
<ol>
    <li>Lambda</li>
    <li>Glue job</li>
    <li>Data transformation</li>
</ol>


## Prerequisites

Before you start this project, you must set up and access the following technologies. 

<ins>AWS</ins>
<br>
AWS (Amazon Web Services) provides a whole range of services for cloud computing. Below I go into more detail regarding the individual services and what they will be used for. For this project, we will use their RDS (Relational Database Service) to create the PostgreSQL database where our data will be loaded. You can create a free AWS account <a href='https://aws.amazon.com/free/'>here</a>. More information on how you can set up jobs and within these services can be found by clicking on the linked titles of each section. 


<ins>Create PostgreSQL database</ins>
<br>
This would have been set up at the end of the ETL project which you can find here. Follow the there if you haven't already, and upload the data used for this project found in the Data folder. Instructions

<ins>Create MySQL database</ins>
<br>
We need to create a MySQL database which we can access to load our data to as the end target for the CDC pipeline.

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


<ins>Create S3 bucket</ins>
<br>
The Amazon S3 service lets you to store data as .csv files inside directories or buckets. For this task, one S3 bucket will be made to act as the target for the DMS migration task. It will essentially act as staging area in the middle of the pipeline, before data is finally to the final target MySQL database. During the full load, data from the source is stored in a .csv titled with the prefix <i>LOAD</i>. Once changes are made to the data at the source, a separate file containing this CDC data (titled with a timestamp) is also added to the same bucket folder.

To create a bucket, go to the S3 management console in AWS and click <>Create bucket<>. In the set-up, untick the <i>Block all public access</i></li> box (this isn't usually advisable, but for this project this is to avoid any potential bugs).

 
<ins>Set up DMS (Data Migration Service)</ins>
<br>
DMS allows you to migrate data between two different locations. For this project, we will be using DMS to migrate data from our source PostgreSQL database to our S3 bucket. To do so, we need to create a <b>replication instance</b> (which connects the RDS PostgreSQL to S3), <b>two endpoints</b> and <b>a migration task (which defines the objectives)</b>.

To create the replication instance:
<ol>
    <li>Go the DMS Management Console and go to <i>Replication instances</i> to create a new one.
    <br>
        <ul>
            <li>For <i>Instance class</i>, select dms.t3.micro.</li>
            <li>For <i>Connectivity and security</i>, make sure that the IPv4 network type is selected alongside the default options for VPC, replication subnet groups and VPC security groups.</li>
            <li></li>
            <li></li>
        </ul>
    </li>
    <li></li>
    <li></li>
    <li></li>
    <li></li>
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

Afterwards we need to create another endpoint, this time for the S3 bucket.
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
<ul>
    <li>A replication instance </li>
    <li>Select the replication instance, source endpoint and target endpoint created previously.</li>
    <li>Under <i>Migration type</i>, select <i>Migrate existing data and replicate ongoing changes</i>.</li>
    <li>For <i>Migration task startup configuration</i>, select <i>Manually later</i>.</li>
</ul>


<ins>Lambda function and Glue job</ins>
<br>
The final part of the CDC pipeline to writing data from the S3 bucket to the target MySQL database.

Whenever new data or files enter the S3 bucket, this triggers the Lambda function to extract the filepath and location of the data within the bucket. Once extracted, this invokes the Glue job which uses this information to read, and write this to the target database. 

Set-up for both the Lambda function and Glue job will take place later on in the project within their respective scripts. 


<ins>CloudWatch</ins>
<br>
This is a handy monitoring service that stores logs and metrics of each job that’s being run within AWS. This is great for debugging as you’ll be able to check why and how any Lambda functions or Glue jobs may have failed. 

<ins>CloudWatch</ins>
<br>
You would have noticed the use. IAM (I Management) is a service that. It is. So. 

This is a handy monitoring service that stores logs and metrics of each job that’s being run within AWS. This is great for debugging as you’ll be able to check why and how any Lambda functions or Glue jobs may have failed. 
