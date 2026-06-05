## Additional Architecture Decisions

### 002 — Use MinIO for Local S3-Compatible Storage

**Decision**

Use MinIO as the local object storage layer.

**Reasoning**

* Provides an S3-compatible interface without requiring an AWS account.
* Enables realistic data lake workflows during local development.
* Supports Parquet-based lakehouse patterns used in modern data platforms.
* Keeps development costs at zero while maintaining portability.

**Tradeoffs**

* MinIO is not a complete replacement for AWS S3.
* Production deployments require additional considerations such as:

  * IAM permissions
  * Bucket policies
  * Encryption
  * Network security
  * Monitoring and governance

---

### 003 — Store Raw and Curated Data in Separate Buckets

**Decision**

Maintain separate storage locations for raw and curated datasets.

**Reasoning**

* Preserves raw source extracts for auditing and reprocessing.
* Allows transformations to evolve without modifying source data.
* Improves data lineage and traceability.
* Simplifies debugging and root-cause analysis.
* Aligns with common lakehouse architecture patterns.

**Tradeoffs**

* Additional storage management overhead.
* More documentation is required to explain data movement between layers.
* Increased operational complexity compared to a single storage layer.

---

### 004 — Use Spark for Curated Transformations

**Decision**

Use Apache Spark to perform raw-to-curated data transformations.

**Reasoning**

* Spark is widely adopted across modern data engineering organizations.
* Supports distributed processing and horizontal scalability.
* Integrates well with Parquet and S3-compatible storage systems.
* Provides a realistic production-style transformation layer.
* Prepares the project for future growth beyond local-scale datasets.

**Tradeoffs**

* Increased operational complexity compared to Python-only pipelines.
* Longer startup times during local development.
* Additional dependency and package management requirements.

---

### 005 — Use dbt for Warehouse Modeling

**Decision**

Use dbt to build dimensions, facts, and business marts from warehouse staging tables.

**Reasoning**

* Encourages modular and maintainable SQL development.
* Provides built-in testing and validation capabilities.
* Creates clear lineage between models.
* Generates project documentation automatically.
* Reflects common analytics engineering practices.

**Tradeoffs**

* Introduces additional tooling and project structure.
* Requires maintenance of source definitions and model dependencies.
* Adds a learning curve for contributors unfamiliar with dbt.

---

### 006 — Use Airflow for Orchestration

**Decision**

Use Apache Airflow to orchestrate the end-to-end pipeline.

**Reasoning**

* Industry-standard workflow orchestration platform.
* Makes task dependencies explicit and observable.
* Provides scheduling, retries, monitoring, and logging.
* Enables future expansion to production-style workflows.
* Separates orchestration concerns from transformation logic.

**Tradeoffs**

* Additional runtime and infrastructure requirements.
* More complex local setup compared to shell scripts or cron jobs.
* Requires ongoing maintenance of DAG definitions and environment configuration.

---

## Architecture Summary

The project follows a layered lakehouse architecture:

```text
PostgreSQL Source
        ↓
Python Ingestion
        ↓
MinIO Raw Layer
        ↓
Spark Curated Layer
        ↓
MinIO Curated Layer
        ↓
PostgreSQL Warehouse
        ↓
dbt Analytics Models
        ↓
Airflow Orchestration
```

The design prioritizes:

* Reproducibility
* Data lineage
* Scalability
* Maintainability
* Local-first development
* Production-style engineering practices
