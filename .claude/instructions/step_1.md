# Step 1: Project Structure and Setup

## Objective
Create the foundational directory structure and configuration files for the client Activity Monitor application that queries MULTIPLE client databases concurrently.

## A. Complete Directory Structure

Create the following directory structure:

```text
client_activity_monitor/
│
├── .gitignore
├── pyproject.toml
├── README.md
├── LICENSE
│
├── configs/
│   └── databases.yaml              # Single configuration file for all settings
│
├── queries/
│   ├── get_all_password_changes.sql
│   ├── get_all_email_changes.sql
│   ├── get_all_phone_changes.sql
│   └── get_all_token_changes.sql
│
├── reports/                        # Output directory for generated reports
│
├── logs/                          # Application logs directory
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── __init__.py
│
└── src/
    └── client_activity_monitor/
        ├── __init__.py
        │
        ├── model/
        │   ├── __init__.py
        │   ├── config_manager.py
        │   ├── repositories/
        │   │   ├── __init__.py
        │   │   ├── ez_connect_oracle.py    # Your existing Oracle connection module
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
        ├── controller/
        │   ├── __init__.py
        │   └── main_controller.py
        │
        └── main.py
```

## B. Configuration File Structure

create `configs/app_settings.yaml` with the following structures:

    ```yaml
    # Oracle Kerberos Client Configuration (SHARED across all databases)
    oracle_client:
      instant_client_dir: "/opt/oracle/instantclient"
      krb5_conf: "/etc/krb5.conf"
      krb5_cache: "/tmp/krb5cc_user"
      trace_level: 16
      trace_directory: "/tmp/oracle_trace"
    
    # application settings
    app_settings:
      report_output_dir: "reports"
      log_dir: "logs"
      log_level: "INFO"
      email_recipients: ["email1.abc.com", "email2.abc.com"]  

    # user settings
    user_settings:
      sid: "A12345"
    ```

Create `configs/databases.yaml` with the following structure:

```yaml

# Database Configurations (multiple databases)
databases:
  - name: client_activity_analysis
    host: localhost
    port: 6336
    service_name: client_activity_analysis
    default_schema: "audit_logs"
    sql_queries:
      - name: "Get all email changes"
        query_location: "queries/get_all_email_changes.sql"
      - name: "Get phone changes by client ID"
        query_location: "queries/get_all_phone_changes.sql"
      - name: "Get token changes"
        query_location: "queries/get_token_changes.sql"
  - name: account_activity_analysis
    host: localhost
    port: 6336
    service_name: account_activity_analysis_activity_analysis
    default_schema: "audit_logs"
    sql_queries:
      - name: "Get all password changes"
        query_location: "queries/get_all_password_changes.sql"
```

## C. SQL Query Files

Create placeholder SQL files in the `queries/` directory. Each file should use these standard parameters:
- `:start_date` - The datetime to search from

Example `queries/get_all_password_changes.sql`:
```sql
SELECT 
    user_id,
    change_timestamp,
    'password' as change_type
FROM 
    user_password_history
WHERE 
    change_timestamp >= :start_date
ORDER BY 
    change_timestamp DESC
```

## D. Poetry Configuration

Create `pyproject.toml`:

```toml
[tool.poetry]
name = "client-activity-monitor"
version = "0.1.0"
description = "Monitor user activity across multiple Oracle databases"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.12"
oracledb = {version = "^2.0.0", extras = ["kerberos"]}
pydantic = "^2.0.0"
customtkinter = "^5.2.0"
pandas = "^2.2.0"
openpyxl = "^3.1.2"
pyyaml = "^6.0"
loguru = "^0.7.0"
pyperclip = "^1.8.2"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-cov = "^4.1.0"
black = "^23.0.0"
pylint = "^3.0.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.scripts]
client-monitor = "client_activity_monitor.main:main"
```

## E. Git Configuration

Create `.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env

# Poetry
dist/
*.egg-info/

# Application
reports/*.xlsx
reports/*.csv
logs/*.log
configs/databases_local.yaml  # Local override config

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

## F. Module Placement

1. Place your existing `ez_connect_client.py` file in:
   `src/client_activity_monitor/model/repositories/ez_connect_oracle.py`

2. Create empty `__init__.py` files in all directories to make them Python packages

## G. Initial Validation

After creating the structure:

1. Initialize Poetry:
   ```bash
   poetry install
   ```

2. Verify the structure:
   ```bash
   tree client_activity_monitor -I '__pycache__|*.pyc'
   ```

3. Test import of your client module:
   ```python
   from client_activity_monitor.model.repositories.ez_connect_client import OracleKerberosConnection
   ```

## Key Points for Implementation

1. **Single Oracle Client Configuration**: The `oracle_client` section is defined once and shared across all database connections
2. **Multiple Databases**: The `databases` list contains multiple database endpoints
3. **Standard SQL Parameters**: All queries use  `:start_date`
4. **MVC Structure**: Clear separation between Model, View, and Controller
5. **Your Existing Module**: `ez_connect_oracle.py` is placed in the repositories layer
