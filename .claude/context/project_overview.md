# **Client Activity Monitor - Development Plan**

## **Phase 1: Foundations & Setup**

---

## 📣 Project Addendum & Errata: Canonical Guidance for Implementation

### This addendum clarifies the actual implementation requirements based on the finalized design

---

### 🔴 1. Multi-Database Configuration is Canonical

- All database queries, connections, and UI status displays are designed for **multiple Oracle databases**, as defined in `configs/databases.yaml`.
- Oracle client configuration is **shared** across all databases (defined once in `app_settings.yaml`).
- Configuration uses **TWO separate YAML files**:
  
    ```yaml
    # app_settings.yaml - User-editable settings
    oracle_client:
      instant_client_dir: "/opt/oracle/instantclient"
      krb5_conf: "/etc/krb5.conf"
      krb5_cache: "/tmp/krb5cc_user"
    app_settings:
      report_output_dir: "reports"
      email_recipients: ["email1@example.com"]
    user_settings:
      sid: "A12345"  # For audit/reporting only
    
    # databases.yaml - Database definitions (admin-managed)
    databases:
      - name: "client_activity_analysis"
        host: "client.db.example.com"
        port: 1521
        service_name: "CLIENTPROD"
        default_schema: "AUDIT_LOGS"
        sql_queries:
          - name: "Get all email changes"
            query_location: "queries/get_all_email_changes.sql"
          - name: "Get phone changes by client ID"
            query_location: "queries/get_phone_changes_by_client_id.sql"
          - name: "Get token changes"
            query_location: "queries/get_token_changes.sql"
      - name: "account_activity_analysis"
        host: "account.db.example.com"
        port: 1521
        service_name: "ACCOUNTPROD"
        default_schema: "AUDIT_LOGS"
        sql_queries:
          - name: "Get all password changes"
            query_location: "queries/get_all_password_changes.sql"
    ```

---

### 🔴 2. Query Parameters - CRITICAL CORRECTION

- **All SQL query files use ONLY ONE named bind parameter:**
  - `:start_date` — Always set to 30 days before current date (NOT user-configurable)
- **The User SID is NOT used in queries** - it's only for audit/reporting purposes
- **Different databases run different queries** as defined in their sql_queries list

---

### 🔴 3. Directory Structure

- **The canonical directory structure is:**
  ```
  client_activity_monitor/
  ├── configs/
  │   ├── app_settings.yaml
  │   └── databases.yaml
  ├── queries/
  │   ├── get_all_email_changes.sql
  │   ├── get_phone_changes_by_client_id.sql
  │   ├── get_token_changes.sql
  │   └── get_all_password_changes.sql
  ├── src/
  │   └── client_activity_monitor/
  │       ├── model/
  │       │   ├── repositories/
  │       │   ├── services/
  │       │   └── integrations/
  │       ├── view/
  │       │   └── panels/
  │       └── controller/
  ```

---

### 🔴 4. Concurrency and Query Execution Architecture

- **DatabaseExecutor** manages all concurrent query execution:
  - For each database in `databases.yaml`, it launches a `QueryRepository` in a separate thread
  - Each database runs ONLY its configured queries (not all databases run the same queries)
  - Start date is ALWAYS calculated as 30 days ago
  - Supports cancellation via a `threading.Event`
  - **Progress callback signature**: `(database_name, query_name, status, row_count)`

---

### 🟡 5. UI Controls Based on Wireframe

- **Configuration Panel:**
  - Oracle Client Path (entry + browse)
  - KRB5 Config Path (entry + browse)
  - KRB5 Config Cache Path (entry + browse)
  - User SID (entry)
  - Save Config button

- **Run Analysis Panel:**
  - Last Time Event Reported (datetime entry) - used for 24-hour filtering
  - KINIT Executed? (checkbox - enables Run Report)
  - Run Report button
  - Generate Email Report button
  - Copy Excel Path to Clipboard button
  - OneNote Entry to Clipboard button
  - Optional Save Report button

- **Database Status Panel:**
  - Dynamic display based on configured databases
  - Shows per-database and per-query status

---

### 🟡 6. Business Logic Clarification

- **Analysis Flow:**
  1. Query all databases for changes since (current_date - 30 days)
  2. Merge results from all databases
  3. Filter to users who made ALL 4 change types (password, email, phone, token)
  4. Further filter to only changes within 24 hours before "Last Time Event Reported"
  5. Generate report with qualifying users

- **OneNote Entry Format:**
  - Simple 4-field summary: SID, Run Time, Last Event Time, User Count
  - NOT a copy of Excel data

---

### 🟡 7. Logging Implementation

- **Use the `loguru` library for all logging**
- Logger writes to both:
  - UI Log Panel (with colored status)
  - Rotating log file in logs/ directory

---

### ✅ Implementation Guidelines

- SID is for audit trail only - it identifies who ran the report
- Start date is always 30 days ago - not configurable
- Different databases contribute different types of changes
- Email uses mailto URL (no auto-attachment)
- OneNote is clipboard-based (no API)
- KINIT is a simple checkbox (no validation)

---

## **Development Phases**

### **Phase 1: Foundations & Setup**
1. Project Structure (Poetry, directories)
2. Configuration Module (dual YAML files)

### **Phase 2: Core Functionality**
3. Run Analysis Panel (KINIT checkbox)
4. Database Query Execution (multi-DB concurrent)
5. Data Merging & Filtering (24-hour window)

### **Phase 3: Reporting & Communication**
6. Report Generation (Excel/CSV)
7. Email Integration (mailto URL)
8. OneNote Integration (clipboard summary)

### **Phase 4: UI & User Experience**
9. UI Panels (Database Status, Logs)
10. Validation & Error Handling
11. Documentation & Polish

---

**This corrected addendum reflects the actual implementation as built in the step-by-step guides.**