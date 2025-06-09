# **Step 4: Database Query Execution**

## **Objective**

* Use the configuration (from Step 2) and the user-confirmed KINIT state (from Step 3’s checkbox) to connect to Oracle and **run the four queries** (password, email, phone, token changes).
* Gather results as pandas DataFrames for further analysis.
* Provide real-time database and query status in the UI.
* Handle errors gracefully and log results.

---

## **A. Query Repository Module**

**Purpose:**
Centralizes all Oracle DB access using your existing `ez_connect_oracle.py` in the repository layer.

**Directory:**
`src/oracle_activity_monitor/model/repositories/query_repository.py`

**Example Implementation Outline:**

```python
from .ez_connect_oracle import OracleKerberosConnection
import pandas as pd

class QueryRepository:
    def __init__(self, db_config):
        self.db_config = db_config
        self.conn = None

    def connect(self):
        self.conn = OracleKerberosConnection(self.db_config)
        self.conn.connect()
        return self.conn

    def run_query(self, sql_path: str, params: dict = None):
        if self.conn is None:
            self.connect()
        with open(sql_path, "r") as f:
            sql = f.read()
        result = self.conn.execute_query(sql, params)
        return pd.DataFrame(result) if result else pd.DataFrame()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
```

---

## **B. Query Service Module**

**Purpose:**
Coordinates running all four queries, applies filters (using “last event time”), and merges results.

**Directory:**
`src/oracle_activity_monitor/model/services/query_service.py`

**Example Implementation Outline:**

```python
import pandas as pd

class QueryService:
    def __init__(self, repository):
        self.repo = repository

    def run_all_queries(self, last_event_time):
        # Map: query_name -> sql file path
        query_map = {
            "password": "queries/password_change.sql",
            "email": "queries/email_change.sql",
            "phone": "queries/phone_change.sql",
            "token": "queries/token_change.sql",
        }
        results = {}
        for name, sql_file in query_map.items():
            # For each query, pass the appropriate parameters
            params = {"start_time": last_event_time}
            df = self.repo.run_query(sql_file, params)
            results[name] = df
        return results

    def close(self):
        self.repo.close()
```

---

## **C. Controller Integration**

* On “Run Report” click (if KINIT checkbox is ticked), the controller:

  1. Loads the config from ConfigManager.
  2. Initializes `QueryRepository` and `QueryService` with config.
  3. Calls `run_all_queries(last_event_time)` (from UI input).
  4. Receives four DataFrames (or empty if no results).
  5. Passes them to the next processing step (merging/filtering/report).
  6. Updates UI panels for status, per-query and per-database status, and logs.

---

## **D. UI & Status Feedback**

* **Database Status Panel:**

  * Show “Connecting…”, “Querying…”, “Success”, or “Error” per query/database.
  * Show row counts for each DataFrame, or “No results” if none.
* **Log Panel:**

  * Log each stage: connection, query, errors, and completion.

---

## **E. Error Handling**

* Gracefully handle:

  * Connection errors (bad config, expired credentials)
  * Query errors (bad SQL, missing files)
  * No results found
* Log all exceptions, and show user-friendly errors in the UI.

---

## **F. Testing**

* **Unit tests:**

  * Mock repository and test query execution (return DataFrames).
* **Integration/manual test:**

  * Confirm correct DataFrame shape, proper filtering, and error handling.

---

## **G. Example AI Prompt for Each Brick**

**For QueryRepository:**

> Generate a Python class that uses an existing OracleKerberosConnection to run arbitrary SQL queries from file paths, returning results as pandas DataFrames.

**For QueryService:**

> Generate a service class that takes a repository and runs four queries (“password”, “email”, “phone”, “token”) with a given start time, returning results as DataFrames.

---

## **Summary Table: Step 4**

| Sub-Step        | Action/Behavior                                                 |
| --------------- | --------------------------------------------------------------- |
| QueryRepository | Oracle DB access (via config); runs queries, returns DataFrames |
| QueryService    | Runs all queries, returns dict of DataFrames                    |
| Controller      | Ties UI action to query run, collects results                   |
| UI/Status Panel | Real-time feedback on each query/database                       |
| Error Handling  | Graceful errors, user messages, logging                         |
| Testing         | Unit/integration tests with mock/fake data                      |

---
