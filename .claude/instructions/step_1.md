# **Step 1: Project Structure and Setup (With Oracle Connection Module Integration)**

## **A. Directory Layout**

Establish your main project directory and core folders, **placing your existing Oracle connection module in the proper place for the MVC architecture**:

```text
client_activity_monitor/
│
├── .gitignore
├── pyproject.toml                    # Poetry configuration
├── README.md
├── LICENSE
│
├── configs/                          # Configuration files for the app
│   ├── app_settings.yaml             # App config: Oracle/Kerberos/paths/recipients
│
├── queries/                          # Standalone .sql files (one per query type)
│   ├── password_change.sql
│   ├── email_change.sql
│   ├── phone_change.sql
│   ├── token_change.sql
│
├── reports/                          # Output directory for generated reports
│
├── docs/                             # Documentation and diagrams
│   ├── architecture.md
│   └── user_guide.md
│
├── tests/                            # Unit/integration tests
│
└── src/
    └── client_activity_monitor/
        │
        ├── __init__.py
        │
        ├── model/
        │   ├── __init__.py
        │   ├── config_manager.py             # For reading/writing YAML config
        │   ├── domain/                       # Data classes (UserChange, etc.)
        │   ├── repositories/
        │   │   ├── __init__.py
        │   │   └── ez_connect_oracle.py      # <-- Place your module here!
        │   ├── services/                     # Business logic, KINIT, merge, report
        │   └── integrations/                 # Outlook, OneNote, clipboard
        │
        ├── view/
        │   ├── __init__.py
        │   ├── app_ui.py
        │   └── panels/
        │       ├── __init__.py
        │       ├── configuration_panel.py
        │       ├── run_analysis_panel.py
        │       ├── database_status_panel.py
        │       └── log_panel.py
        │
        ├── controller/
        │   ├── __init__.py
        │   └── main_controller.py
        │
        ├── common/
        │   ├── __init__.py
        │   └── utils.py
        │
        └── main.py
```

***Key point:***
Your `ez_connect_oracle.py` will be the **core database access layer**. Other code will import and use its classes/methods for all Oracle DB and Kerberos connections.

---

## **B. Initial Files and Conventions**

* **Create all directories and `__init__.py` files** as above.
* **Add your `ez_connect_oracle.py` module** into `src/client_activity_monitor/model/repositories/`.
* **In your README.md**, note:
  “This project uses an in-house Oracle Kerberos connection module for all database operations. Configuration must follow the expected schema for DatabaseConnectionConfig and OracleClientConfig.”

---

## **C. Initial Configuration File**

* Create a `configs/app_settings.yaml` file (can be empty for now).
* Make sure field names match what your `ez_connect_oracle.py` expects:

  * host, port, service\_name, default\_schema
  * oracle\_client:

    * instant\_client\_dir, krb5\_conf, krb5\_cache, \[trace\_level], \[trace\_directory]

**Example YAML Skeleton:**

```yaml
host: "proddbgo.example.com"
port: 1521
service_name: "ORCL"
default_schema: "MYSCHEMA"
oracle_client:
  instant_client_dir: "/path/to/instantclient"
  krb5_conf: "/path/to/krb5.conf"
  krb5_cache: "/path/to/krb5cc"
  trace_level: 16
  trace_directory: "/path/to/trace"
```

---

## **D. Poetry & Version Control**

* **Initialize Poetry:**

  ```bash
  poetry init
  poetry add oracledb pydantic customtkinter pandas pyyaml
  ```

* **Initialize Git:**

  ```bash
  git init
  echo "reports/\n__pycache__/\n*.pyc" > .gitignore
  ```

---

## **E. Validation**

* **Test your connection:**
  Before building more, validate that `ez_connect_oracle.py` works with your test YAML config by running a simple script (you can use your existing module’s test block).

---

## **F. What Comes Next**

* Once your project structure is in place and you have a working connection,
  **proceed to Step 2: Implementing the ConfigManager and Configuration UI Panel**.

---

## **Summary Table (Step 1, Updated)**

| Sub-Step                   | What to Do                                     | Why/Result                                      |
| -------------------------- | ---------------------------------------------- | ----------------------------------------------- |
| Directory/Module Setup     | Place code files as above                      | Ensures clean MVC and reusable code             |
| Add ez\_connect\_oracle.py | To `model/repositories/`                       | Centralizes Oracle DB/Kerberos code             |
| Create config YAML         | Use structure matching Pydantic models         | Immediate compatibility and validation          |
| Poetry & Git Init          | Initialize, add dependencies, commit structure | Ready for modular, versioned development        |
| Validate DB Connect        | Use sample/test config, run sample query       | Ensures base “Model” layer is operational early |

---
