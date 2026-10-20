# Data Engineering projects

A collection of data engineering projects exploring data ingestion, transformation, data quality and incremental processing.

## Projects

### [Near-Real-Time Data Pipeline](./near-real-time-data-pipeline/)

An end-to-end data pipeline built in two stages: an ETL process that extracts and transforms UK music chart data for analysis, followed by a Change Data Capture (CDC) pipeline that replicates source database changes to a downstream database.

### [GitHub API ETL Pipeline](./github-api-project/)

A Python ETL pipeline that extracts repository data from the GitHub REST API, validates and normalises incoming records, and loads clean data into SQLite. Invalid records are routed to a dead-letter queue (DLQ) for investigation, with automated tests covering pipeline behaviour.