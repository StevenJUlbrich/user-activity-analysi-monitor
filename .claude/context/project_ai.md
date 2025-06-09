---
## 🧠 AI Prompt Template for Client Activity Monitor Development

**Project Context:**  
This project is a cross-platform desktop application to monitor and report on user activity (password, email, phone, token changes) across multiple Oracle databases.  
It follows a strict Model-View-Controller (MVC) pattern and supports SRE/SOC workflows, with detailed UI and concurrent query execution.

**Key Project Clarifications:**
- Queries use only `:start_date` parameter (always 30 days ago)
- User SID is for audit/reporting only, NOT used in queries
- Different databases run different queries (defined in databases.yaml)
- Two YAML config files: app_settings.yaml (user settings) and databases.yaml (database definitions)

---

### ⬇️ **Prompting Template**

You are an expert Python developer.  
Your task is to implement the following "brick" of the Client Activity Monitor project according to all requirements in the architectural plan.

**[BRICK NAME & OBJECTIVE]**  
(Brief description, e.g. "DatabaseExecutor class for concurrent multi-DB query execution")

**File/Directory:**  
`[canonical project path, e.g. src/client_activity_monitor/model/services/database_executor.py]`

**Key Requirements:**  

- Adhere to the directory structure in the canonical architecture.
- Accept configuration(s) that match the format in `configs/databases.yaml` and `configs/app_settings.yaml`.
- All queries must use the standardized SQL parameter: `:start_date` (datetime) - calculated as 30 days before current date.
- Use the appropriate Pydantic models for config validation (see `ez_connect_oracle.py`).
- Implement robust error handling and logging with loguru, writing to both UI and file.
- If part of the UI, use CustomTkinter panels/components as modular classes.

**Configuration Structure Reference:**
```yaml
# app_settings.yaml
oracle_client:
  instant_client_dir: "/path/to/oracle"
  krb5_conf: "/etc/krb5.conf"
  krb5_cache: "/tmp/krb5cc"
user_settings:
  sid: "A12345"  # For audit only

# databases.yaml  
databases:
  - name: "client_activity_analysis"
    host: "host.example.com"
    port: 1521
    service_name: "SERVICE"
    default_schema: "SCHEMA"
    sql_queries:
      - name: "Get all email changes"
        query_location: "queries/get_all_email_changes.sql"
```

**Additional Behaviors:**  

- (e.g. If a progress_callback is required, describe its expected use and parameters.)
- (If supporting cancellation, specify threading.Event usage.)
- (Remember: start_date is always 30 days ago, not user-configurable)

**Testing/UX Notes:**  

- (Add relevant testing or user experience instructions for this brick.)

**Dependencies:**  

- Reference/require only those modules, libraries, and configs explicitly defined in the canonical architecture.

---

**When you generate code, please:**

- Include docstrings and type hints.
- Use clear naming and follow the project's style/conventions.
- Only generate the code for the [BRICK] described above.
- Remember that SID is for audit logging only, not query parameters.

---

**Sample Brick Description for Prompt:**

**[BRICK NAME & OBJECTIVE]**  
"DatabaseExecutor class: Manages ThreadPoolExecutor, running QueryRepository for each database in configs/databases.yaml. Accepts start_date parameter (always 30 days ago), supports cancellation with threading.Event, and updates the UI via a progress_callback (database name, query name, status, row count). Each database runs its own specific queries as defined in its sql_queries list. Logs all actions with loguru."

---

### ✨ **How to Use This Template**

- Replace the [BRICK NAME & OBJECTIVE], file path, and any brick-specific details.
- Copy this template as the top of your AI prompt or code generation request.
- Always clarify that queries use only :start_date (30 days ago) and that SID is for audit only.

---

> **This template ensures every AI/code generation effort is aligned with the actual project implementation.**