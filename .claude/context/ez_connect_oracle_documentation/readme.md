# Oracle Multi-Database Connection Utility

A robust, type-safe Python toolkit for connecting to multiple Oracle databases with modern best practices—including Kerberos, password, or wallet authentication. Leverages concurrent execution, strict configuration validation (via Pydantic), and YAML-based config for flexible, secure multi-DB workflows.

The installation of the Oracle Instaclient is outside this project and will handle separately.  The key point is the the Oracle 23 Instaclient is available for the Kerberos connectivity.

---

## Features

* **Concurrent SQL Execution:** Run queries on multiple databases in parallel with `ThreadPoolExecutor`.
* **Secure Authentication:** Kerberos ticket, password, or Oracle Wallet-based auth—configured per database.
* **Strict Configuration:** Uses Pydantic models to validate all configuration files at startup.
* **YAML-Based Configuration:** Easy-to-audit YAML files for both user and database connection details.
* **Connection Pooling:** Built-in support for Oracle connection pools for high-concurrency use cases.
* **Detailed Logging:** Centralized, timestamped logs for all connections and queries.
* **Extensible Design:** Well-factored, class-based structure for future expansion.

---

## Project Structure

```text
your_project/
├── configs/
│   ├── user_config.yaml      # User-specific Oracle client and Kerberos details
│   └── databases.yaml        # List of databases, schemas, and SQL statements to run
├── ez_connect_oracle.py      # Main connection/utility class (Pydantic validated)
├── config_loader.py          # Safe, validated YAML loader (Pydantic integration)
├── multi_db_oracle_executor.py  # Entry point: orchestrates multi-DB queries concurrently
└── README.md                 # You are here!
```

---

## Requirements

* Python 3.9 or higher (Python 3.11+ recommended)
* Oracle Instant Client (must be installed and referenced in configs)
* **Dependencies:**
  See [`requirements.txt`](./requirements.txt)

  ```sh
  pip install -r requirements.txt
  ```

---

## Configuration

### 1. User Config (`configs/user_config.yaml`)

Specifies Oracle client, Kerberos config paths, and (optionally) tracing.

```yaml
oracle_client:
  instant_client_dir: /path/to/instantclient_21_9
  krb5_conf: /etc/krb5.conf
  krb5_cache: /tmp/krb5cc_12345
  trace_level: 16
  trace_directory: /var/tmp/oracle_traces
```

### 2. Databases Config (`configs/databases.yaml`)

Defines the list of target databases and queries to execute per database.
The section sql_statements section shows a possible method of storing SQL statements. However,
with complex sql statements should be stored separate files and referenced in the yaml

```yaml
databases:
  - name: production_db
    host: proddb.example.com
    port: 1521
    service_name: PROD
    default_schema: BANKING_APP
    sql_statements:
      - sql: "SELECT COUNT(*) AS total_accounts FROM accounts"
        dataset_name: "account_count"
      - sql: "SELECT * FROM transactions WHERE ROWNUM < 10"
        dataset_name: "recent_transactions"
  # Add more databases as needed...
```

---

## Usage

### 1. Prepare Your Environment

* Ensure the Oracle Instant Client is installed and accessible at the path in your config.
* Ensure Kerberos tickets and configs are set up (if using Kerberos authentication).
* Install all Python dependencies.

### 2. Edit Config Files

* Update `configs/user_config.yaml` and `configs/databases.yaml` to match your environment and needs.

### 3. Run the Executor

```sh
python multi_db_oracle_executor.py
```

* The script will:

  * Validate both YAML configs (using Pydantic)
  * Spin up a thread pool and connect to each listed database
  * Execute all configured queries per database
  * Log results and key statistics for review

---

## Logging

* Logs are saved to `oracle_multi_connection.log` in the project root.
* Each connection also logs activity, including errors, connection status, query results, and schema changes.

---

## Extension & Customization

* **Add Authentication Methods:** Enhance `ez_connect_oracle.py` to support more auth types if needed.
* **Add Query Types:** Configure new queries in your YAML—no code changes required for simple SELECTs.
* **Plug In Custom Logic:** Fork and extend the main executor for more advanced orchestration or ETL logic.

---

## Troubleshooting

* **Config Validation Errors:** All config files are strictly checked. Errors will be logged and must be resolved before execution.
* **Oracle Client Issues:** Ensure all paths in configs are correct and readable by your Python process.
* **Kerberos Authentication:** Verify your ticket cache, config paths, and that your principal is active.


---

## Authors & Credits

* **Original Author:** Steven (Application Support & Software Solutions)


---

## Changelog

* **v1.0.0:** Initial public release with YAML configs, Kerberos, connection pooling, multi-threaded query orchestration.

---
