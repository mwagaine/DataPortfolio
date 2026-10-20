# Project overview


## Contents

<ol>
    <li><a href='https://github.com/mwagaine/DataPortfolio/blob/main/Data%20Engineering%20projects/1.%20ETL%20pipeline/README.md#description'>Description</a></li>
    <li><a href='https://github.com/mwagaine/DataPortfolio/blob/main/Data%20Engineering%20projects/1.%20ETL%20pipeline/README.md#prerequisites'>Prerequisites</a>
      <ul>
        <li><a href='https://github.com/mwagaine/DataPortfolio/blob/main/Data%20Engineering%20projects/1.%20ETL%20pipeline/README.md#spark'>Spark</a></li>
        <li><a href='https://github.com/mwagaine/DataPortfolio/blob/main/Data%20Engineering%20projects/1.%20ETL%20pipeline/README.md#databricks'>Databricks</a></li>
        <li><a href='https://github.com/mwagaine/DataPortfolio/blob/main/Data%20Engineering%20projects/1.%20ETL%20pipeline/README.md#aws-amazon-web-services'>AWS (Amazon Web Services)</a></li>
        <li><a href='https://github.com/mwagaine/DataPortfolio/blob/main/Data%20Engineering%20projects/1.%20ETL%20pipeline/README.md#postgresql-database'>PostgreSQL database</a></li>
      </ul>
    </li>
</ol>


## Description 

The aim of this project is to create an ETL pipeline. ETL stands for "Extract, Transform and Load", so (as you might have guessed) we will be creating a pipeline that extracts data from a given source, and transforms it before loading it into a separate database. I wanted to venture into ETL because it is a common pipeline design used throughout data engineering that allows organisations to consolidate data from various databases into one hub in a standardised format, ready for analysis and further processing.

As someone with an interest in popular culture, I wanted to extract music sales data relating to songs that topped the UK Singles Chart throughout 1999. This was at the peak of physical CD sales and recording music industry revenue before the rise of the internet, file-sharing and illegal downloads through sites such as Napster decimated record sales.

The data will be extracted by web-scraping <a href='https://en.wikipedia.org/wiki/1999_in_British_music_charts#Charts'>this Wikitable</a>. After the data is loaded into the database, we will perform some exploratory data analysis with a series of SQL queries. You can also find the final data <a href='https://github.com/mwagaine/DataPortfolio/tree/main/Data%20Engineering%20projects/2.%20CDC%20pipeline/Data'>here</a>.

Please follow this project in the given order of files:
<ol>
    <li>ETL pipeline</li>
    <li>Exploratory data analysis</li>
</ol>


## Prerequisites

Before you start this project, you must to set up and access the following technologies. 

### <ins>Spark</ins>

Spark is an engine that executes all sorts of processing and analysis on large amounts of data. You can use different languages to communicate with Spark to perform these tasks; here we will be using Python (PySpark). For a more detailed guide on how to install Spark on Windows click <a href='https://www.knowledgehut.com/blog/big-data/how-to-install-apache-spark-on-windows'>here</a>, otherwise if you are a Mac user click <a href='https://medium.com/beeranddiapers/installing-apache-spark-on-mac-os-ce416007d79f'>here</a>. 


### <ins>Databricks</ins>

Next, you will need a platform that is powered by Spark where you can run your script in a notebook to extract, transform and load the data. I used Databricks which offers a free Community edition <a href='https://docs.databricks.com/en/getting-started/community-edition.html'>here</a> if you don't already have it. 


### <ins>AWS (Amazon Web Services)</ins>

AWS provides a whole range of services for cloud computing. For this project, we will use their RDS (Relational Database Service) to create the PostgreSQL database where our data will be loaded. You can create a free AWS account <a href='https://aws.amazon.com/free/'>here</a>.


### <ins>PostgreSQL database</ins>

Finally, you'll need to create the database where the data will be loaded. We will be using a database that runs on PostgreSQL, and this can be created using AWS (Amazon Web Services).

<ol>
  <li>Create a free-tier AWS account <a href='https://aws.amazon.com/free/'>here</a> if you don't already have one, and head to the RDS Management Console.</li>
  <li>Go to <i>Parameter groups</i> and create a custom parameter group for the database group family <i>postgres15</i>.
  <br>
  Then modify the parameters below with the following values:
    <ul>
      <li><i>rds.force_ssl</i> = 0</li>
      <li><i>rds.logical_replication</i>  = 1</li>
      <li><i>wal_sender_timeout</i> = 0</li>
      <li><i>max_worker_processes</i> = 12</li>
      <li><i>max_logical_replication_workers</i> = 1</li>
      <li><i>autovacuum_max_workers</i> = 3</li>
      <li><i>max_parallel_workers</i> = 8</li>
      <li><i>shared_preload_libraries</i> = pglogical</li>
    </ul>
  </li>
  <li>Go to <i>Databases</i> and create a free-tier PostgreSQL database running on the engine version <i>PostgreSQL 15</i>, 
  <br>
  following the instructions <a href='https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Tutorials.WebServerDB.CreateDBInstance.html'>here</a> except:
  <ul>
      <li>In the <i>Storage autoscaling</i> section, untick the <i>Enable storage autoscaling</i> box.</li>
      <li>In the <i>Connectivity</i> section, select <i>Don’t connect to an EC2 compute resource</i>.</li>
      <li>In the same section, ensure the default VPC, DB subnet group and VPC security group options are selected.</li>
      <li>In the same section, select <i>Yes</i> for <i>Public access</i>.</li>
      <li>In the <i>Additional configuration</i> section, leave the initial database name blank - it defaults to <i>postgres</i>.</li>
      <li>In the same section, select the DB parameter group you've just created.</li>
      <li>In the same section, untick the <i>Enable automated backups</i> box.</li>
      <li>In the same section, untick the <i>Enable encryption</i> box.</li>
      <li>In the same section, untick the <i>Enable auto minor version upgrade</i> box under <i>Maintenance</i>.</li>
    </ul>
  <li>Once created, under the database's <i>Connectivity & security</i> go to <i>Security</i> and click the link under <i>VPC security groups.</i>
  <br>
  Go to <i>Inbound rules</i> and edit the security group's inbound rules so that they only include the follow
    <ul>
      <li><i>Type</i>: All traffic, <i>Source type</i>: Custom, <i>Source</i>: ::/0</li>
      <li><i>Type</i>: All traffic, <i>Source type</i>: Custom, <i>Source</i>: 0.0.0.0/0</li>
      <li><i>Type</i>: PostgreSQL, <i>Source type</i>: Custom, <i>Source</i>: ::/0</li>
      <li><i>Type</i>: PostgreSQL, <i>Source type</i>: Custom, <i>Source</i>: 0.0.0.0/0</li>
    </ul>
  </li>
  <li>Download and install PostgreSQL by following <a href='https://www.postgresqltutorial.com/postgresql-getting-started/install-postgresql/'>this guide</a>.</li>
  <li>Download and set up the PostgreSQL driver <a href='https://jdbc.postgresql.org/documentation/setup/'>here</a>.</li>
  <li>Open pgAdmin on your desktop and connect to the database just created by following <a href='https://www.postgresqltutorial.com/postgresql-getting-started/connect-to-postgresql-database/'>these instructions</a>, 
  <br>
  using the database's endpoint (found in RDS) as the hostname and keeping <i>postgres</i> as the maintanence database.</li>
</ol>
