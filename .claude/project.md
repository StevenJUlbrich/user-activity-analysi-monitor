# Project User Activity Monitor

The following is the project outline.  It need more work.

## **Project Design Document: User Activity Analysis Monitor**

### 1. Introduction & Goals

**1.1. Project Objective**
To create a desktop application that provides a unified view of a specific user's recent activity (password changes, contact info changes, etc.) by querying multiple Oracle databases concurrently. The application will feature a user-friendly interface and provide reporting capabilities in various formats (Excel, Email, OneNote).

### 1.2. Core Technologies

* **Language:** Python 3.12+
* **Dependency Management:** Poetry
* **GUI Framework:** CustomTkinter
* **Data Manipulation:** Pandas
* **Database Driver:** `oracledb` with Kerberos support

### 2. System Architecture

**2.1. Architectural Pattern**
The application will strictly adhere to the **Model-View-Controller (MVC)** architectural pattern to ensure a clean separation of concerns, enhance testability, and promote long-term maintainability.

* **Model:** Manages all data access, business logic (data processing and analysis), and output formatting. It is completely independent of the UI.
* **View:** Renders the user interface and captures all user input. Contains no business logic.
* **Controller:** Acts as the intermediary, receiving user requests from the View and orchestrating the Model's components to fulfill those requests.

**2.2. Concurrency Model**
To ensure the UI remains responsive during database operations, the application will use a multi-threaded approach:

* A `ThreadPoolExecutor` will be used to execute query sets against different databases in parallel.
* The entire database execution process will be run in a separate `threading.Thread` from the main UI thread.
* A `threading.Event` object will be used as a cancellation flag to allow the user to gracefully stop long-running queries.

### 3. Project & Directory Structure (Poetry)

The project will be organized using a standard Poetry layout to manage dependencies and packaging effectively.

```text
client_activity_monitor/
│
├── .gitignore
├── pyproject.toml           # Poetry's config for dependencies & project info
├── poetry.lock              # Auto-generated lock file for deterministic builds
├── README.md                # Project documentation
│
├── configs/
│   ├── databases.yaml       # Defines database connections and SQL file paths
│   └── app_settings.yaml    # Stores user-specific saved paths
│
├── queries/
│   ├── idm_password_changes.sql
│   └── ... (other .sql files) ...
│
├── reports/                 # Default output directory for generated reports
│
└── src/
    └── client_activity_monitor/ # Main application package
        │
        ├── __init__.py
        │
        ├── controller/
        │   ├── __init__.py
        │   └── main_controller.py # Application orchestrator
        │
        ├── model/
        │   ├── __init__.py
        │   ├── ez_connect_oracle.py     # Core Oracle connection class
        │   ├── config_manager.py      # Handles app_settings.yaml
        │   ├── database_executor.py   # Manages concurrent query execution
        │   ├── data_analyzer.py       # Merges and analyzes results
        │   └── report_generator.py    # Creates all report formats
        │
        ├── view/
        │   ├── __init__.py
        │   └── app_ui.py              # Defines all GUI components
        │
        └── main.py                  # Application entry point
```

### 4. Configuration Management

**4.1. Application Settings (`configs/app_settings.yaml`)**

* **Purpose:** Stores user-specific file paths to avoid re-entry. Managed by the UI.
* **Structure:**

    ```yaml
    oracle_client:
      instant_client_dir: "/opt/oracle/instantclient"
      krb5_conf: "/etc/krb5.conf"
      krb5_cache: "/tmp/krb5cc_user"
      trace_level: 16
      trace_directory: "/tmp/oracle_trace"
    app_settings:
      report_output_dir: "reports"
      log_dir: "logs"
      log_level: "INFO"
      email_recipients: []  # Will be populated via UI
    user_settings:
      sid: "A12345"
    ```

**4.2. Database Definitions (`configs/databases.yaml`)**

* **Purpose:** Defines the target multiple databases and the queries to run against them.
* **Structure:**

    ```yaml
    databases:
    - name: "IDM_DATABASE"
        host: "idm.proddb.example.com"
        port: 1521
        service_name: "IDMPROD"
        default_schema: "REPORTS"
      
    - name: "AUDIT_DATABASE"
        host: "audit.proddb.example.com"
        port: 1521
        service_name: "AUDITPROD"
        default_schema: "AUDIT_LOGS"

    # ... other database definitions ...
    ```

**4.3. SQL Queries (`queries/*.sql`)**

* **Purpose:** Each `.sql` file contains a single, complex SQL query. Using external files keeps the YAML clean and makes queries easier to maintain.
* **Parameters:** Queries must use `oracledb` named placeholders (e.g. `:start_date`) for dynamic values.

### 5. Component Deep Dive (MVC Implementation)

#### **5.1. Model Layer (`src/client_activity_monitor/model/`)**

* **`ez_connect_oracle.py`**
  * **Class:** `OracleKerberosConnection`
  * **Responsibility:** The provided, robust class for establishing and managing a single Oracle database connection using Kerberos. It will be used by the `DatabaseExecutor`.

* **`config_manager.py`**
  * **Functions:** `save_settings(path, settings_data)`, `load_settings(path)`
  * **Responsibility:** Handles YAML serialization and deserialization for the `app_settings.yaml` file.

* **`database_executor.py`**
  * **Class:** `DatabaseExecutor`
  * **Methods:**
    * `run_all(sid, start_date, progress_callback, cancel_event)`: Main entry point. Creates a `ThreadPoolExecutor` and submits a task for each database defined in `databases.yaml`.
    * `_execute_queries_for_db(...)`: Private worker function. Connects to one database, reads and executes all associated `.sql` files, and returns the results. It will periodically check `cancel_event.is_set()` between steps to allow for graceful cancellation.
  * **Responsibility:** Orchestrates all database interactions, manages concurrency, and provides progress updates via the `progress_callback`.

* **`data_analyzer.py`**
  * **Function:** `analyze_user_activity(dict_of_dfs)`
  * **Responsibility:** Implements the core business logic. It takes the dictionary of Pandas DataFrames (output from the executor), performs the necessary `merge` and `filter` operations to find users who appear in all required datasets, and returns a single, consolidated DataFrame for reporting.

* **`report_generator.py`**
  * **Functions:**
    * `generate_excel(df, output_dir)`: Saves the final DataFrame to a timestamped `.xlsx` file in the specified directory.
    * `generate_onenote_table_string(df_row)`: Formats a single row of data into a tab-separated string suitable for pasting into a OneNote table.
    * `generate_mailto_link(df)`: Creates a `mailto:` URL with a pre-formatted subject and an HTML table in the body, summarizing the report DataFrame.

#### **5.2. View Layer (`src/client_activity_monitor/view/`)**

* **`app_ui.py`**
  * **Class:** `AppUI(customtkinter.CTk)`
  * **Responsibility:** Defines and organizes all UI widgets. It is initialized with a reference to the controller and links all widget commands (e.g., button clicks) to controller methods.
  * **Key Widgets:**
    * **Setup Frame:** `CTkEntry` widgets for Oracle/Kerberos paths, `CTkButton` for "Save Settings".
    * **Controls Frame:** `CTkEntry` for SID and Start Date, `CTkCheckBox` for "kinit" confirmation, `CTkButton` for "Run Analysis" and "Cancel".
    * **Status Frame:** `CTkProgressBar` and `CTkLabel` for status updates.
    * **Results Frame:** A `ttk.Treeview` styled widget to display the tabular results from the final DataFrame.
    * **Actions Frame:** Buttons for "Generate Email", "Copy Report Path", and "Copy Row for OneNote".
  * **Public Methods (for Controller use):** `update_results(df)`, `set_progress(value, text)`, `show_message(title, message)`, `set_controls_state(is_running)`.

#### **5.3. Controller Layer (`src/client_activity_monitor/controller/`)**

* **`main_controller.py`**
  * **Class:** `MainController`
  * **Responsibility:** The central hub of the application.
  * **`__init__`:** Initializes the View and all Model components. Loads initial settings using `config_manager` and populates the View. Binds View events to its handler methods.
  * **Key Event Handlers:**
    * `on_save_settings()`: Gets paths from the View and tells `config_manager` to save them.
    * `on_run_analysis()`: Validates user input. Disables/enables relevant buttons. Creates the `threading.Event` for cancellation. Starts the `_run_analysis_thread`.
    * `on_cancel()`: Calls `self.cancel_event.set()`.
    * `on_generate_excel()`: Calls `report_generator`, then updates the View with a success message and the file path.
    * ...and other handlers for each action button.
  * **Private Methods:**
    * `_run_analysis_thread()`: The target function for the worker thread. It calls the `DatabaseExecutor`, then the `DataAnalyzer`, and finally calls back to the UI thread to update the view with the final results. This keeps the UI from freezing.

### 6. Application Entry Point & Dependencies

**6.1. Entry Point (`src/client_activity_monitor/main.py`)**

* A simple script to instantiate and launch the application.

    ```python
    from .controller.main_controller import MainController

    def start_app():
        app = MainController()
        app.run() # This calls the mainloop on the view

    if __name__ == "__main__":
        start_app()
    ```

**6.2. Dependencies (`pyproject.toml`)**

* The `pyproject.toml` file will manage all dependencies and project metadata.

    ```toml
  [tool.poetry.dependencies]
  python = "^3.12"  
  pandas = "^2.2.0"
  openpyxl = "^3.1.2"
  customtkinter = "^5.2.0"
  pyyaml = "^6.0.1"
  oracledb = {version = "^2.0.0", extras = ["kerberos"]}
  pyperclip = "^1.8.2"
  pydantic = "^2.5.0"  # For robust config validation
  loguru = "^0.7.0"    # Better logging
  pytest = "^7.4.0"    # Testing framework
  pytest-asyncio = "^0.21.0"
  black = "^23.0.0"    # Code formatting
  mypy = "^1.7.0"      # Type checking
  ruff = "^0.1.0"      # Fast linting

  [tool.poetry.group.dev.dependencies]
  pre-commit = "^3.5.0"
  coverage = "^7.3.0"
    ```
