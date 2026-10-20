# Lessons Learned

This document records the main engineering lessons and design decisions that emerged while developing the GitHub API ETL pipeline.

The purpose is not to document every debugging incident, but to capture the more general lessons that are transferable to other data-engineering projects.

---

## 1. Data contracts are more important than individual data types

One of the main lessons from the project was that a data pipeline crosses multiple type systems.

The same conceptual field can have different representations at different stages:

```text
GitHub API
    ↓
Python
    ↓
Pandas
    ↓
SQLite
    ↓
Pandas
```

For example, the `forks` field is optional.

In the Python representation it can therefore be:

```python
10
None
```

In Pandas it is represented using the nullable integer dtype:

```text
Int64
```

In SQLite it is stored as:

```text
INTEGER
```

When the SQLite table is subsequently read back into Pandas, however, a nullable integer column can be inferred as:

```text
float64
```

because standard NumPy integer types cannot represent missing values while floating-point columns can represent `NaN`.

This demonstrated an important principle:

> **Do not assume that types remain identical when data crosses system boundaries. Define and verify the data contract appropriate to each system.**

The important requirement is not necessarily that every system uses the same underlying type, but that the semantic contract is preserved.

For example:

```text
Business contract:

forks
- integer when present
- nullable
- non-negative
```

can legitimately be represented differently by Python, Pandas and SQLite.

---

## 2. Validation and normalisation are different responsibilities

Initially, it was tempting to treat validation and type conversion as part of the same operation.

The project highlighted why separating them is useful.

### Validation

Validation answers:

> Does this record conform to the expected contract?

### Normalisation

Normalisation answers:

> Can this compatible representation be safely converted into the expected representation?

For example:

```text
"12"
```

may be technically convertible into:

```text
12
```

but conversion should not automatically mean that the original value was valid.

This distinction becomes particularly important for required fields.

A required integer field represented as a string may be technically convertible, but if the source contract explicitly requires an integer, silently accepting it could hide a source-system quality problem.

The pipeline therefore treats conversion as an explicit policy rather than assuming that every convertible value should be accepted.

---

## 3. Required and optional fields should be treated differently

The schema defines whether a field is required.

This affects both validation and downstream handling.

For example:

```text
Required field
    missing → INVALID

Optional field
    missing → VALID_WITH_WARNING
```

Similarly:

```text
Required field
    null → INVALID

Optional field
    null → VALID_WITH_WARNING
```

This distinction prevents the pipeline from treating every data-quality problem as equally severe.

An optional field such as `forks` can legitimately remain null in the clean dataset.

A required field such as `language` cannot.

---

## 4. A schema can describe a contract, but it does not replace application logic

The project uses a schema to describe things such as:

* source field names
* output field names
* expected types
* defaults
* required/optional status

This provides a useful machine-readable representation of the input contract.

However, the schema itself does not necessarily determine what the pipeline should do next.

For example, the schema can state:

```text
forks_count
type = int
required = false
default = None
```

but the application still needs logic determining:

* what constitutes a null
* whether strings may be converted
* whether a failed conversion becomes a warning or an error
* whether the record should enter the DLQ

This helped distinguish **describing a contract** from **implementing pipeline behaviour**.

---

## 5. Keep validation results separate from source data

The validation process initially raised the question of whether validation metadata should be stored inside each repository dictionary.

The project ultimately kept these concerns separate.

Conceptually:

```text
repo
    ↓
validation(repo)
    ↓
ValidationResult
```

rather than:

```text
repo = {
    ...
    "validation_result": ...
}
```

This has several advantages.

The original repository remains a clean representation of the source data.

The validation result can contain behaviour and state appropriate to the validation process without making the repository object difficult to serialise.

This became particularly relevant when constructing the DLQ, where raw repository data needed to be serialised separately from validation metadata.

---

## 6. `ValidationResult` was useful as a class because it represents a stable concept

The project considered whether validation results should simply be dictionaries.

A dictionary would have been sufficient for storing arbitrary data, but `ValidationResult` represented a stable concept with behaviour and invariants.

It therefore provided a useful abstraction for operations such as:

* retrieving the status
* retrieving issues
* invalidating a result
* checking whether a result is valid

This reinforced a broader Python lesson:

> Use a class when the concept has meaningful behaviour or invariants; use a dictionary when the structure is primarily ad hoc data.

The project deliberately avoided introducing classes where simple dictionaries were sufficient.

---

## 7. Be careful with mutating methods that return `None`

Python methods such as `dict.update()` mutate an object in place and return `None`.

The same principle applied to the project's `ValidationResult.invalidate()` method.

The following is incorrect when `invalidate()` mutates the object:

```python
result = result.invalidate()
```

because `result` becomes `None`.

The correct approach is:

```python
result.invalidate()
```

This was a useful reminder to distinguish between:

```text
mutating an existing object
```

and:

```text
creating and returning a new object
```

---

## 8. The DLQ should preserve enough information to investigate failures

A data pipeline should avoid simply discarding records that fail processing.

The DLQ therefore retains:

```text
repo_name
raw_data
issues
loaded_at
```

The original API response is preserved as raw data, while validation issues are stored separately.

This provides enough information to answer:

* Which record failed?
* What did the source actually send?
* Why did validation fail?
* Can the source problem be reproduced or investigated?

The clean dataset can therefore maintain a stricter contract without losing problematic records.

---

## 9. Clean data and DLQ data have different requirements

The clean dataset and DLQ are not simply two versions of the same table.

The clean dataset should be:

* structured
* type-consistent
* suitable for downstream consumption

The DLQ should be:

* permissive
* traceable
* diagnostic

Trying to force failed records into the same strict schema as valid records would defeat part of the purpose of a DLQ.

This led to the design:

```text
Clean table
    → transformed, validated records

DLQ table
    → raw record + failure metadata
```

---

## 10. DataFrame dtypes are part of the data contract

Pandas' nullable extension dtypes became important when optional fields were introduced.

A normal NumPy integer column cannot represent missing values:

```text
int64
```

whereas Pandas' nullable integer dtype can:

```text
Int64
```

Similarly, nullable booleans can use:

```text
boolean
```

This matters because simply allowing Pandas to infer types can result in representations that don't match the intended contract.

For example:

```text
Optional integer + missing values
        ↓
Pandas inference
        ↓
float64
```

Explicitly enforcing:

```python
df["forks"] = df["forks"].astype("Int64")
```

preserves the intended representation.

The broader lesson is:

> **DataFrame dtypes should be treated as part of the dataset contract rather than an incidental implementation detail.**

---

## 11. Persistence boundaries need explicit testing

The SQLite round-trip test was initially intended to verify that the data written to the database could be read back successfully.

The test revealed the nullable integer dtype issue.

This demonstrated that persistence is a boundary where additional behaviour can occur.

A pipeline can therefore be conceptually tested at several boundaries:

```text
API
 ↓
validation
 ↓
normalisation
 ↓
transformation
 ↓
DataFrame
 ↓
database
```

Each boundary can potentially introduce:

* type conversion
* null handling differences
* truncation
* encoding differences
* schema mismatches
* unexpected coercion

The local round-trip test is therefore useful as an integration test, even though a production data platform would normally use additional destination-level data-quality testing.

---

## 12. Production data testing would operate at multiple levels

The project's tests are primarily Python-based because the project is a local application.

In a larger production pipeline, testing would normally be distributed across different layers.

### Application tests

Tools such as `pytest` can test:

* extraction logic
* validation
* transformation
* error handling
* routing behaviour

### Destination-level data tests

Tools such as dbt or Great Expectations can test the actual persisted dataset.

Examples include:

```text
repo_name must not be null
repo_name must be unique
forks must be >= 0
expected columns must exist
null rates must remain within expected limits
```

The important distinction is:

> The local project uses a Python process to verify the result because it is a small self-contained pipeline. A production platform would normally complement application tests with tests against the destination data itself.

The underlying concern — verifying the persisted data contract — remains the same.

---

## 13. Local SQLite is a deliberate simplification, not a production architecture

SQLite was deliberately selected because it allows the project to demonstrate:

```text
API → transformation → database
```

without requiring cloud infrastructure.

This makes it possible to focus on Python and data-engineering fundamentals first.

A production system might instead use:

* a managed relational database
* a cloud data warehouse
* a lakehouse
* object storage plus analytical processing

The important learning from this project is the ETL architecture and the data-quality principles rather than the specific choice of SQLite.

---

## 14. Avoid overengineering a learning project

One of the most useful lessons from the project was knowing when **not** to add another technology.

Potential additions included areas such as:

* dbt
* Docker
* CI/CD
* cloud infrastructure
* incremental loading
* complex database schema management
* extensive observability
* orchestration frameworks

These could all be legitimate in a production system, but adding them to a small learning project would have shifted the focus away from the core objectives.

The project therefore prioritised:

```text
Python fundamentals
+
data quality
+
testing
+
ETL design
+
persistence
```

over attempting to simulate an entire production platform.

This is an important engineering judgement:

> **A good system is not necessarily the system with the most components. Architecture should be proportional to the problem being solved.**

---

## 15. What I would change for production

If this pipeline were developed into a production system, several areas would change.

### Secrets

The local `.env` approach would be replaced by managed secrets or environment configuration provided by the deployment platform.

### Persistence

SQLite would likely be replaced with a managed database or cloud data warehouse/lakehouse.

### Orchestration

Pipeline execution would be managed by an orchestration platform rather than manually running `main.py`.

### Data quality

Destination-level data-quality checks could be implemented using tools such as dbt or Great Expectations.

### Infrastructure

Cloud resources could be managed using infrastructure-as-code tools such as Terraform.

### Observability

The pipeline would need structured logging, monitoring, metrics and alerting.

### Recovery

Production processing would need stronger handling for retries, partial failures, idempotency and potentially incremental processing.

### CI/CD

Automated tests and deployment would be integrated into a CI/CD pipeline.

These additions are intentionally outside the scope of the current project.

---

## 16. Overall takeaway

The project started as a relatively simple API-to-database exercise but became useful for understanding several fundamental data-engineering concepts:

```text
Source contracts
      ↓
Validation
      ↓
Normalisation
      ↓
Transformation
      ↓
Explicit data types
      ↓
Persistence boundaries
      ↓
Data-quality testing
      ↓
Failure handling
```

The most important lesson is that a data pipeline is not simply a sequence of transformations.

It is a sequence of **contracts and boundaries**.

At each boundary, the pipeline needs to understand:

* what data it receives
* what data it expects
* what transformations are permitted
* what constitutes failure
* how failures are handled
* what representation is required by the next system

That perspective is transferable well beyond this particular GitHub API project.