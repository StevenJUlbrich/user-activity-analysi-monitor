# Client Activity Monitor

A desktop application for monitoring user activity across multiple Oracle databases for Security Operations Center (SOC) teams.

## **Project Design Document: Client Activity Monitor**

### 1. Introduction & Goals

**1.1. Project Objective**
To create a desktop application that identifies users who have made all four critical security changes (password, email, phone, and token) within a 24-hour window by querying multiple Oracle databases concurrently. The application provides comprehensive reporting and facilitates quick incident response for SOC teams.

**1.2. Core Technologies**

* **Language:** Python 3.12+
* **Dependency Management:** Poetry
* **GUI Framework:** CustomTkinter
* **Data Manipulation:** Pandas
* **Database Driver:** `oracledb` with Kerberos support
* **Configuration Validation:** Pydantic v2
* **Logging:** Loguru
* **Testing:** Pytest
* **Clipboard:** Pyperclip
* **Excel Generation:** Openpyxl

### 2. System Architecture

**2.1. Architectural Pattern**
The application strictly adheres to the **Model-View-Controller (MVC)** architectural pattern:

* **Model:** Manages all data access, business logic (data processing and analysis), and output formatting. It is completely independent of the UI.
* **View:** Renders the user interface and captures all user input. Contains no business logic.
* **Controller:** Acts as the intermediary, receiving user requests from the View and orchestrating the Model's components to fulfill those requests.

**2.2. Concurrency Model**
To ensure the UI remains responsive during database operations, the application uses a multi-threaded approach:

* A `ThreadPoolExecutor` with workers equal to the number of configured databases executes queries in parallel
* The entire database execution process runs in a separate thread from the main UI thread
* A `threading.Event` object is used as a cancellation flag for graceful query termination
* Thread-safe queue mechanism for UI progress updates from worker threads
* All UI updates are marshaled back to the main thread

**2.3. Threading Architecture**
```
Main Thread (UI)
    ↓
Analysis Thread (Orchestration)
    ↓
ThreadPoolExecutor (n workers = n databases)
    ├── Worker Thread 1 → Database 1
    ├── Worker Thread 2 → Database 2
    └── Progress Callbacks → Queue → UI Updates
```

### 3. Project & Directory Structure (Poetry)

The project will be organized using a standard Poetry layout to manage dependencies and packaging effectively.

```text
client_activity_monitor/
│
├── .gitignore
├── pyproject.toml              # Poetry configuration
├── poetry.lock                 # Locked dependencies
├── README.md                   # Project documentation
│
├── configs/
│   ├── databases.yaml          # Database connections and queries
│   └── app_settings.yaml       # User configuration
│
├── queries/
│   ├── get_all_email_changes.sql
│   ├── get_phone_changes_by_client_id.sql
│   ├── get_token_changes.sql
│   └── get_all_password_changes.sql
│
├── reports/                    # Generated reports directory
├── logs/                       # Application logs
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
└── src/
    └── client_activity_monitor/
        ├── __init__.py
        ├── main.py             # Application entry point
        │
        ├── controller/
        │   ├── __init__.py
        │   └── main_controller.py
        │
        ├── model/
        │   ├── __init__.py
        │   ├── config_manager.py
        │   ├── repositories/
        │   │   ├── __init__.py
        │   │   ├── ez_connect_oracle.py
        │   │   └── query_repository.py
        │   ├── services/
        │   │   ├── __init__.py
        │   │   ├── database_executor.py
        │   │   ├── merge_filter_service.py
        │   │   └── report_generator.py
        │   └── integrations/
        │       ├── __init__.py
        │       ├── email_service.py
        │       └── onenote_service.py
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
        └── common/
            ├── __init__.py
            ├── validators.py
            ├── exceptions.py
            ├── error_handler.py
            └── clipboard_utils.py
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
  email_recipients: ["security@example.com", "soc@example.com"]

user_settings:
  sid: "A12345"  # User's SID for audit trail only
```

**4.2. Database Definitions (`configs/databases.yaml`)**

* **Purpose:** Defines target databases and their specific queries (admin-managed)
* **Structure:**

```yaml
databases:
  - name: client_activity_analysis
    host: oracle.client.example.com
    port: 6036  # Custom Oracle port
    service_name: CLIENT_AUDIT
    default_schema: "audit_logs"
    sql_queries:
      - name: "Get all email changes"
        query_location: "queries/get_all_email_changes.sql"
      - name: "Get phone changes by client ID"
        query_location: "queries/get_phone_changes_by_client_id.sql"
      - name: "Get token changes"
        query_location: "queries/get_token_changes.sql"
        
  - name: account_activity_analysis
    host: oracle.account.example.com
    port: 6036
    service_name: ACCOUNT_AUDIT
    default_schema: "audit_logs"
    sql_queries:
      - name: "Get all password changes"
        query_location: "queries/get_all_password_changes.sql"
```

**4.3. SQL Queries (`queries/*.sql`)**

* **Purpose:** External SQL files for maintainability
* **Parameters:** All queries use only `:start_date` parameter (30 days before current date)
* **Example:**

```sql
SELECT 
    user_id,
    change_timestamp,
    old_value,
    new_value
FROM 
    email_audit_log
WHERE 
    change_timestamp >= :start_date
ORDER BY 
    change_timestamp DESC
```

### 5. Component Deep Dive (MVC Implementation)

#### **5.1. Model Layer**

**Configuration Management**
* `config_manager.py`: Handles dual YAML file management with Pydantic validation
  - Loads and validates `app_settings.yaml` and `databases.yaml`
  - Provides methods to get connection parameters per database
  - Updates user settings while keeping database configs read-only

**Database Operations**
* `repositories/ez_connect_oracle.py`: Existing Oracle connection module
* `repositories/query_repository.py`: Single database query execution
* `services/database_executor.py`: Concurrent multi-database orchestration
  - Creates ThreadPoolExecutor with workers = number of databases
  - Manages progress callbacks and cancellation
  - Handles partial failures gracefully

**Business Logic**
* `services/merge_filter_service.py`: Core analysis logic
  - Merges results from different databases by change type
  - Filters for users with ALL four changes
  - Applies 24-hour window filter based on UI input
* `services/report_generator.py`: Excel/CSV generation with metadata

**External Integrations**
* `integrations/email_service.py`: Mailto URL generation
* `integrations/onenote_service.py`: Clipboard formatting for OneNote

#### **5.2. View Layer**

**Main Application**
* `app_ui.py`: Main window with grid layout
  - Left column: Configuration and Run Analysis panels
  - Right column: Database Status (top) and Logs (bottom)

**UI Panels**
* `panels/configuration_panel.py`: Oracle/Kerberos paths and SID entry
* `panels/run_analysis_panel.py`: KINIT checkbox and action buttons
* `panels/database_status_panel.py`: Dynamic status per database/query
* `panels/log_panel.py`: Scrollable color-coded log display

#### **5.3. Controller Layer**

* `main_controller.py`: Central orchestration
  - Initializes all components
  - Handles UI events and delegates to services
  - Manages threading for non-blocking operations
  - Coordinates error handling and user feedback

### 6. Error Handling Strategy

**6.1. Exception Hierarchy**
```python
ClientActivityMonitorError (Base)
├── ConfigurationError
├── DatabaseConnectionError
├── QueryExecutionError
├── ReportGenerationError
└── ExternalIntegrationError
```

**6.2. Error Handling Approach**
* Input validation before processing (validators.py)
* Try-except blocks with specific exception types
* User-friendly error messages mapped from technical errors
* Graceful degradation for partial database failures
* All errors logged with full stack traces

**6.3. Recovery Strategies**
* Automatic retry with exponential backoff for connection failures
* Partial result processing when some databases fail
* Clear user guidance for recovery actions

### 7. Logging Implementation

**7.1. Logging Configuration**
* **Library:** Loguru for structured logging
* **Destinations:**
  - UI Log Panel with color coding (INFO, WARNING, ERROR)
  - Rotating file: `logs/client_activity_monitor.log`
* **Rotation:** Daily rotation, 7-day retention
* **Format:** `[timestamp] [level] [module] message`

**7.2. What Gets Logged**
* All database connections and disconnections
* Query execution with row counts
* User actions (configuration saves, report generation)
* Errors with full context
* Performance metrics (query duration)

### 8. Validation Strategy

**8.1. Configuration Validation**
* Pydantic models for both YAML configurations
* Path validation for Oracle client and Kerberos files
* SID format validation (5-10 alphanumeric characters)
* Email format validation for recipients

**8.2. Runtime Validation**
* DateTime format for "Last Event Time" input
* KINIT checkbox state before enabling Run Report
* Database connectivity before query execution
* Result data integrity before report generation

### 9. Testing Approach

**9.1. Unit Testing**
* Validators with valid/invalid inputs
* Configuration save/load operations
* Data merging logic with various scenarios
* Report generation with empty/full data

**9.2. Integration Testing**
* Full workflow with mocked databases
* Error scenarios and recovery
* Cancellation at various stages
* Thread safety verification

**9.3. Manual Testing**
* UI validation messages
* Progress updates during execution
* Clipboard operations
* Email client integration

### 10. Security Considerations

**10.1. Authentication**
* Kerberos handled externally via `kinit`
* Simple checkbox confirmation in UI
* No credential storage in application

**10.2. Audit Trail**
* User SID logged for all operations
* Report metadata includes who/when
* All actions logged with timestamps

**10.3. Data Protection**
* Reports stored locally with OS permissions
* No sensitive data in logs
* Secure clipboard handling

### 11. Performance Considerations

* Concurrent database queries reduce total execution time
* Progress callbacks keep UI responsive
* Lazy configuration loading
* Efficient DataFrame operations for large result sets
* Connection reuse where possible

### 12. Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.12"
pandas = "^2.2.0"
openpyxl = "^3.1.2"
customtkinter = "^5.2.0"
pyyaml = "^6.0.1"
oracledb = {version = "^2.0.0", extras = ["kerberos"]}
pyperclip = "^1.8.2"
pydantic = "^2.5.0"
loguru = "^0.7.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-cov = "^4.1.0"
black = "^23.0.0"
pylint = "^3.0.0"
mypy = "^1.7.0"
```

### 13. Future Enhancements

* Scheduled/automated report generation
* Historical trend analysis
* Additional change types monitoring
* REST API for integration
* Web-based UI option