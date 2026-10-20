# Near-Real-Time Data Pipeline

## Overview

This project demonstrates the development of a data pipeline in two stages, using UK music chart data from 1999 as its underlying dataset.

The first stage builds a traditional Extract, Transform, Load (ETL) pipeline to collect, process and store the data for analysis. The second stage extends this work by introducing Change Data Capture (CDC), allowing inserts, updates and deletions in the source database to be reflected in a downstream database.

Together, the two stages demonstrate the progression from initial data ingestion and transformation to incremental, near-real-time data replication.

## Project Components

### 1. [ETL Pipeline](./1.%20ETL%20pipeline/)

Extracts UK music chart data from Wikipedia, transforms it and loads it into a PostgreSQL database, followed by exploratory data analysis using SQL.

### 2. [CDC Pipeline](./2.%20CDC%20pipeline/)

Builds upon the ETL pipeline by replicating data from PostgreSQL to MySQL through an AWS-based CDC workflow. Demonstrates how changes to source records can be propagated downstream without repeatedly performing a full data load.

## Project Structure

```text
near-real-time-data-pipeline/
├── README.md
├── 1. ETL pipeline/
│   ├── README.md
│   └── ...
└── 2. CDC pipeline/
    ├── README.md
    └── ...
```

Each component contains its own documentation, implementation details and instructions. **Start with the ETL pipeline**, as the CDC pipeline builds upon the database and data created in the first stage.