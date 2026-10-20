# GitHub API ETL Pipeline

## Overview

A Python ETL pipeline that extracts repository data from the GitHub REST API, validates and normalises the incoming records, applies business transformations, and persists the resulting dataset to SQLite.

The project was built as a practical exercise in Python data engineering, with a particular focus on:

* Python decomposition and clean function responsibilities
* Data validation and quality handling
* Data normalisation and transformation
* Pandas DataFrame construction and type enforcement
* Error handling and dead-letter queue (DLQ) design
* Automated testing
* Database persistence

The project is intentionally scoped as a local learning project rather than a production deployment.

---

## Architecture

The pipeline follows the following flow:

```text
                         GitHub REST API
                                │
                                ▼
                         List[dict] response
                                │
                                ▼
                           Validation
                          /          \
                     VALID            INVALID
                       │                 │
                       ▼                 ▼
                  Normalisation         DLQ
                  /          \
             successful     failed
                  │             │
                  ▼             ▼
            Transformation     DLQ
                  │
                  ▼
             Pandas DataFrame
                  │
                  ▼
                SQLite
```

The pipeline therefore separates the **clean data path** from records that cannot safely be processed.

---

## Pipeline stages

### 1. Extraction

Repository data is retrieved from the GitHub REST API.

The API response naturally arrives as a list of dictionaries, with each dictionary representing one repository.

The pipeline retains this record-oriented structure during validation and transformation before converting the valid records into a Pandas DataFrame.

Only the fields required by the downstream dataset are selected from the much larger API response.

---

### 2. Validation

Each repository is validated against a defined schema.

The schema specifies properties such as:

* source field name
* output field name
* expected Python type
* default value
* whether the field is required

Validation checks include:

* field existence
* null values
* expected data types
* required versus optional fields

Validation produces a structured result containing:

* overall validation status
* field-level issue codes

Example issue codes include:

```text
MISSING
IS_NULL
WRONG_TYPE
```

Validation statuses are:

```text
VALID
VALID_WITH_WARNING
INVALID
```

A record with an optional-field issue can continue through the pipeline, while records containing unrecoverable problems are eventually routed to the DLQ.

---

### 3. Normalisation

Normalisation handles compatible differences in data representation.

For example, an optional integer field may arrive as a numeric string. Where the normalisation policy explicitly permits the conversion, the value can be converted into the expected representation.

Normalisation is deliberately separated from validation:

> Validation determines whether a record conforms to the expected contract; normalisation changes compatible representations into the form required downstream.

Required fields are treated more strictly. A value being technically convertible does not automatically make it acceptable when the source contract requires the field to already have the correct type.

Records that cannot be safely normalised remain invalid and are routed to the DLQ.

---

### 4. Transformation

After successful validation and normalisation, business-facing transformations are applied.

For example:

```text
forks_count      → forks
open_issues_count → open_issues
stargazers_count → stargazers
watchers_count   → watchers
name             → repo_name
```

This separates **technical normalisation** from **business/output transformation**.

---

### 5. Pandas DataFrame

Valid repository records are converted into a Pandas DataFrame.

The DataFrame schema explicitly controls the expected representation of each column.

Nullable fields use Pandas' nullable extension dtypes where appropriate.

For example:

```python
{
    "repo_name": str,
    "language": str,
    "size": int,
    "open_issues": int,
    "stargazers": int,
    "watchers": int,
    "forks": "Int64",
    "private": "boolean",
    "has_projects": "boolean",
    "has_pages": "boolean",
    "has_discussions": "boolean"
}
```

`forks` is nullable because it is an optional source field. Pandas' `Int64` extension dtype allows integer values and `<NA>` to coexist without converting the column to floating point.

---

### 6. SQLite persistence

The transformed DataFrame is written to a local SQLite database.

The database is generated locally when the pipeline runs and is excluded from version control.

The database mapping converts DataFrame types into SQLite-compatible types, for example:

```text
Pandas Int64 → SQLite INTEGER
Pandas boolean → SQLite BOOLEAN
Pandas string/object → SQLite TEXT
```

SQLite was chosen as a lightweight persistence layer so that the project could demonstrate the complete ETL-to-database workflow without introducing cloud infrastructure prematurely.

---

### 7. Dead-Letter Queue

Records that cannot successfully pass validation or normalisation are routed to a dead-letter queue.

The DLQ preserves both the original record and information about why it failed.

The conceptual structure is:

```text
repository_dlq
├── repo_name
├── raw_data
├── issues
└── loaded_at
```

This avoids silently discarding bad data while also preventing invalid records from contaminating the clean dataset.

The validation result is kept separate from the raw repository data, allowing the original API response to remain serialisable.

---

## Testing

The project uses automated tests to verify behaviour at multiple stages of the pipeline.

Tests cover:

* valid records
* missing optional fields
* missing required fields
* null values
* incorrect data types
* optional-field warnings
* required-field failures
* normalisation behaviour
* DataFrame columns and dtypes
* DLQ routing
* SQLite persistence
* database round-trip behaviour

The tests focus on the behaviour and contracts of each stage rather than simply testing implementation details.

---

## Configuration and secrets

API credentials are not stored directly in the source code.

A local `.env` file is used for the GitHub token:

```text
GITHUB_TOKEN=your_token_here
```

The `.env` file is excluded from version control through `.gitignore`.

The repository therefore contains no GitHub personal access token.

---

## Setup

Clone the repository and create a Python virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment and install the project dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```text
GITHUB_TOKEN=your_token_here
```

The token is loaded by the application using `python-dotenv`.

---

## Running the pipeline

Run the main pipeline from the project root:

```bash
python main.py
```

The pipeline will:

1. Retrieve repository data from GitHub.
2. Validate the API response.
3. Normalise compatible values.
4. Transform the valid records.
5. Create the Pandas DataFrame.
6. Persist the clean dataset to SQLite.
7. Route failed records to the DLQ.

---

## Project structure

```text
github-api-project/
│
├── README.md
├── config.py
├── main.py
├── ...
│
├── tests/
│   └── ...
│
├── docs/
│   └── lessons-learned.md
│
├── .env.example
├── .gitignore
└── requirements.txt
```

---

## Key design decisions

### Retaining the list-of-dictionaries structure

The GitHub API already returns repository records as dictionaries. Keeping this structure through validation and transformation provides a natural mapping between API records and eventual DataFrame rows without unnecessary restructuring.

### Separate validation and normalisation

Validation and normalisation have different responsibilities. Validation identifies whether a record conforms to the expected contract, while normalisation handles explicitly permitted representation differences.

### Separate clean data and DLQ data

Invalid records are not silently discarded. They are retained separately with their original data and validation issues so that failures can be investigated without affecting the clean dataset.

### Explicit nullable DataFrame types

Optional integer and boolean fields require Pandas nullable dtypes so that missing values can be represented without losing the intended semantic type.

---

## Limitations

This is a local learning project rather than a production implementation.

It currently does not include:

* cloud infrastructure
* infrastructure as code
* external orchestration
* CI/CD
* production secrets management
* managed database/warehouse infrastructure
* production monitoring and alerting
* distributed processing

These were deliberately excluded so that the project could focus on Python, data-quality and ETL fundamentals.

---

## Future production considerations

A production implementation could replace the local SQLite database with a managed database or cloud data warehouse.

Additional components could include:

* external workflow orchestration
* infrastructure as code
* managed secrets
* destination-level data-quality testing
* CI/CD
* structured logging and monitoring
* alerting and operational metrics
* incremental processing and recovery strategies

Tools such as dbt or Great Expectations could be introduced for data-quality testing directly against the persisted dataset where appropriate.

The goal of this project was not to reproduce an entire production platform, but to build a complete and understandable ETL pipeline while developing the underlying engineering fundamentals.