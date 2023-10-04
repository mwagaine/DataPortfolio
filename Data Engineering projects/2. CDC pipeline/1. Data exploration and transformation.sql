-- Enable PostgreSQL for logical replication before loading data
CREATE EXTENSION pglogical;
SELECT * FROM pg_catalog.pg_extension;


-- ***PART ONE: DATA EXPLORATION***
-- Display table data after being loaded by PySpark
SELECT * FROM mwag_pyspark.songsales;

-- Give the table a primary key before starting the DMS migration task
ALTER TABLE mwag_pyspark.songsales
ADD PRIMARY KEY ("ChartDate_WeekEnding");
SELECT * FROM mwag_pyspark.songsales;

-- Before starting the CDC pipeline
-- make sure when creating DB to make a custom parameter group, and edit the parameter
-- called rds.force_ssl to 0 since for PostgreSQL 15 onwards, SSL is turned on by default
-- Others the connection between your database and the replication instance will fail

-- ***PART TWO: DATA TRANSFORMATION***
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

-- Ensure that transformed table is in chronological order 
-- before its data is migrated to the target database by
-- giving the table an index and clustering data accordingly
CREATE INDEX date_index 
ON mwag_pyspark.songsales ("ChartDate_WeekEnding" ASC);

CLUSTER mwag_pyspark.songsales USING date_index;
SELECT * FROM mwag_pyspark.songsales;


-- Delete table
DROP TABLE mwag_pyspark.songsales CASCADE;

SELECT *,
       SUM("Sales") OVER (ORDER BY "ChartDate_WeekEnding") AS Cumulative_Sales,
       ROUND((SUM("Sales") OVER (ORDER BY "ChartDate_WeekEnding")) / (SELECT SUM("Sales")
															FROM mwag_pyspark.songsales) * 100, 2) AS Percentage_Sales
FROM mwag_pyspark.songsales;

