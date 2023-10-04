-- Databricks notebook source
-- MAGIC %md
-- MAGIC ## 1. Prepare PostgreSQL for CDC
-- MAGIC
-- MAGIC Before starting the CDC pipeline, we need to ensure that PostgreSQL is enabled for logical replication - a method of replicating data objects and their changes based on a replication identity. PostgreSQL carries out logical replication by using the pglogical plugin which must be installed first.
-- MAGIC
-- MAGIC Next, we need to assign the table with a primary key (the replication identity). This allows PostgreSQL to identify which rows must be changed before replicating the data to the target database. If we don't do this, then it will ignore UPDATE and DELETE changes made to the table. For this project, we can simply use the 'ChartDate_WeekEnding' column as the primary key because there can only be one Number 1 song per week (i.e. this column only contains unique values). 

-- COMMAND ----------

-- Create a pglogical extension
CREATE EXTENSION pglogical;

-- Verify that the pglogical plugin has been installed successfully
SELECT * FROM pg_catalog.pg_extension;

-- Assign the table a primary key
ALTER TABLE mwag_pyspark.songsales
ADD PRIMARY KEY ("ChartDate_WeekEnding");
SELECT * FROM mwag_pyspark.songsales;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 2. Prepare MySQL for CDC
-- MAGIC
-- MAGIC Additionally, the target table in MySQL also needs a primary key for the CDC pipeline to work as planned. Open MySQL Workbench on your desktop, access the MySQL database created previously and create a new table as per below.
-- MAGIC
-- MAGIC NOTE: for MySQL you must quote these column names without any quotation marks, whereas you must quote them with a pair of double quotation marks (" ") in PostgreSQL.

-- COMMAND ----------

-- Create target table with primary key constraint
CREATE TABLE matt_schema.songsales (
    ChartDate_WeekEnding date,
    Song varchar(255),
    Artists varchar(255),
    Sales int,
    PRIMARY KEY (ChartDate_WeekEnding)
);

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 3. Transform PostgreSQL data
-- MAGIC
-- MAGIC We're now ready to start the CDC pipeline. Go to the AWS DMS Management Console and start the migration task you have created. Once the full load is complete, this should replicate all the PostgreSQL data in MySQL. Once that is done, head back to pgAdmin to perform the following data transformations.

-- COMMAND ----------

UPDATE mwag_pyspark.songsales 
SET "Artists" = 'NOBODY' 
WHERE "ChartDate_WeekEnding" = '1999-05-01';

UPDATE mwag_pyspark.songsales 
SET "Artists" = 'NOBODY' 
WHERE "ChartDate_WeekEnding" = '1999-05-08';

INSERT INTO mwag_pyspark.songsales 
VALUES ('2000-01-01','I Have a Dream / Seasons in the Sun','Westlife',231000);

INSERT INTO mwag_pyspark.songsales 
VALUES ('2000-01-08','I Have a Dream / Seasons in the Sun','Westlife',34500);

INSERT INTO mwag_pyspark.songsales 
VALUES ('2000-01-15','I Have a Dream / Seasons in the Sun','Westlife',34738);

DELETE FROM mwag_pyspark.songsales 
WHERE "ChartDate_WeekEnding" = '1999-01-02';

-- COMMAND ----------

-- MAGIC %md
-- MAGIC
-- MAGIC Finally, go back into MySQL Workbench and view the table with the query below. You should now see an updated table with all the previous data changes accounted for.

-- COMMAND ----------

SELECT * 
FROM matt_schema.songsales;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Project complete!
