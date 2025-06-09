# **Step-by-Step Development Plan**

## **Phase 1: Foundations & Setup**

---

## 📣 Project Addendum & Errata: Canonical Guidance for Implementation and AI Code Generation

### This addendum supersedes and clarifies all previous ambiguities in planning, documentation, and configuration

---

### 🔴 1. Multi-Database Configuration is Canonical

- All database queries, connections, and UI status displays are designed for **multiple Oracle databases**, as defined in `configs/databases.yaml`.
- The YAML config must contain a list of database entries, each mapping **directly** to the expected `DatabaseConnectionConfig` and nested `OracleClientConfig` Pydantic models in `ez_connect_oracle.py`.
- Example:
  
    ```yaml
    databases:
      - name: "IDM_DATABASE"
        host: "idm.proddb.example.com"
        port: 1521
        service_name: "IDMPROD"
        default_schema: "REPORTS"
        oracle_client:
          instant_client_dir: "/path/to/instantclient"
          krb5_conf: "/path/to/krb5.conf"
          krb5_cache: "/path/to/krb5cc"
    ```

---

### 🔴 2. Query Parameters Must Be Standardized

- **All SQL query files in `queries/` must accept two named bind parameters:**
  - `:user_id` — the user SID (string)
  - `:start_date` — the last event reported timestamp (datetime)
- The UI must provide both of these inputs and pass them to all queries.

---

### 🔴 3. Directory Structure

- **The canonical directory structure is that defined in `project_step_1.md`.**  
  All new code and AI prompts must adhere to this structure, including:
  - `model/repositories/`, `model/services/`, `model/integrations/`, `view/panels/`, etc.

---

### 🔴 4. Concurrency and Query Execution Architecture

- **DatabaseExecutor** (in `model/services/database_executor.py`) manages all concurrent query execution:
  - For each database in `databases.yaml`, it launches a `QueryRepository` in a separate thread via `ThreadPoolExecutor`.
  - It runs all required queries (password, email, phone, token) with the provided parameters, collects results, and supports cancellation via a `threading.Event`.
  - **A `progress_callback` function is used to update the UI status panel with per-database and per-query results in real time.**
- **QueryRepository** (in `model/repositories/query_repository.py`) is responsible for connecting to a single Oracle DB and running queries with the given parameters.

---

### 🟡 5. UI Controls Clarification

- **Optional Save Report:**  
  - This button must export the report to CSV (in addition to the default Excel format).
- **Cancel Button:**  
  - Required in the "Run Analysis" panel. This triggers cancellation of in-progress queries by setting the shared `threading.Event`.
- **Database Status Panel:**  
  - Must be dynamic, displaying per-database and per-query status based on the config.

---

### 🟡 6. Logging Implementation

- **Use the `loguru` library for all logging.**
  - Logger must write to both:
    - The UI Log Panel (with colored status: info, warning, error)
    - A rotating log file (e.g., `activity_monitor.log`) in the project root.

---

### 🟡 7. Input Mapping and Integration

- All code using `ez_connect_oracle.py` must accept config objects that directly match the structure of each database entry in `databases.yaml`.

---

### ✅ Prompting & Implementation Guidelines

- Always **reference this addendum** in AI prompts and onboarding docs.
- Be explicit about which step, file, or class is to be implemented and which config fields are required.
- When implementing UI status or progress updates, ensure callbacks and logging conform to this addendum.

---

**This addendum ensures that any developer or AI agent working on this project will operate from a single, authoritative source of truth, maximizing maintainability and reducing errors.**

1. **Define Project Structure**

   - Establish the directory layout (src/, model/, view/, controller/, integrations/, common/, tests/, configs/, etc.).
   - Initialize version control (git), Poetry environment, and README.

2. **Establish Configuration Module**

   - Design the config schema (YAML).
   - Implement ConfigManager for reading/writing config values.
   - Create and test a UI panel for config entry and one-time save.

---

## **Phase 2: Core Functionality Bricks**

3. **Kerberos Authentication Integration**

   - Implement logic to run and validate `kinit` as an external process.
   - Show result/status in UI.

4. **Database Query Execution**

   - Build repository classes to execute each of the four required queries.
   - Parameterize queries for time ranges, return pandas DataFrames.

5. **Data Merging & Filtering Logic**

   - Implement a service to merge/aggregate all query results by user.
   - Filter to users meeting the “all four criteria in last 24 hours” rule.

---

## **Phase 3: Reporting & Communication**

6. **Report Generation**

   - Export qualifying users to Excel and/or CSV.
   - Store file in a user-accessible path.

7. **Clipboard Utility**

   - Enable copying the report file path to clipboard in the UI.

8. **Email Integration**

   - Implement logic to generate an Outlook draft email via web call.
   - Attach report or provide its path.

9. **OneNote Integration**

   - Insert or update a table with report info on a given OneNote page via MS Graph API.

---

## **Phase 4: UI & User Experience**

10. **Develop Main UI Panels**

    - Build CustomTkinter panels: Configuration, Run Analysis, Database Status, Logs, Actions.
    - Wire up all UI components to the controller and model.

11. **Status & Logging Feedback**

    - Implement real-time status updates for DB queries, report generation, external calls.
    - Show logs and errors in a scrollable log panel.

12. **Input Validation & Error Handling**

    - Add checks for all user inputs and configuration.
    - Graceful error messages for failures (DB, kinit, report, integrations).

---

## **Phase 5: Finalization & Quality**

13. **Testing**

    - Write unit tests for config, query, and merge logic.
    - Add integration/smoke tests for UI flows and external integrations.

14. **Documentation**

    - Expand README with setup, configuration, and usage instructions.
    - Add an architecture.md explaining the MVC structure and workflows.

15. **Review & Polish**

    - UI refinements, accessibility, help/tooltips.
    - Performance review (optimize query execution, minimize UI blocking).

---

## **Example: Expandable Sub-Plan (for Each Step)**

For each step above, you can later request or build:

- AI prompt templates (“Generate a ConfigManager class that reads/writes YAML files…”)
- Code stubs or detailed implementation guides
- Testing checklists and validation rules
- UX notes or diagrams

---

## **Summary Table (For Your Tracking)**

| Step | Area                 | Brick/Module                    | When to Expand with Detail?          |
| ---- | -------------------- | ------------------------------- | ------------------------------------ |
| 1    | Project Setup        | Structure, Poetry, README       | At project start                     |
| 2    | Configuration        | ConfigManager, ConfigPanel      | Before DB integration                |
| 3    | Kerberos Integration | KinitService                    | Before DB query testing              |
| 4    | Query Execution      | QueryRepository                 | Once kinit is tested                 |
| 5    | Merge/Filter         | AnalysisService                 | After query code is running          |
| 6    | Report Export        | ReportingService                | After data pipeline is working       |
| 7    | Clipboard            | ClipboardUtils                  | After reporting works                |
| 8    | Email                | OutlookService                  | After reporting/clipboard are tested |
| 9    | OneNote              | OneNoteService                  | After basic email flow is proven     |
| 10   | UI Panels            | All CustomTkinter panels        | Start with Config, then rest         |
| 11   | Status/Logs          | StatusPanel, LogPanel           | As queries/services are built        |
| 12   | Validation/Errors    | Input checks, try/except blocks | Continuously                         |
| 13   | Testing              | Pytest/unit/integration tests   | After every brick                    |
| 14   | Docs                 | README, architecture.md         | As each area stabilizes              |
| 15   | Review/Polish        | Final UI, perf, help            | Last                                 |

---

## **How to Use This Plan**

- **Pick a step:** When ready, say “expand step 4 (Query Execution)” and I’ll provide the specific prompt(s) and best-practice details.
- **Mix and match:** You can expand steps in parallel if you want to speed things up or clarify dependencies.
- **Review and revise:** Each brick is independent and testable, so you can iterate as your requirements evolve.

---

**Ready to expand a step? Tell me which one, or let’s start from the top and go brick by brick!**
