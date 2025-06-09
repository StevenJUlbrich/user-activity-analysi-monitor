# **Step 9: UI Panels and Status Feedback**

## **Objective**

* Organize the main application window using CustomTkinter panels for configuration, running analysis, status, actions, and logs.
* **Display real-time status and results** for DB connections, query execution, reporting, and user-triggered actions.
* Make each panel modular and testable, and wire them up via your main controller.

---

## **A. Main Panels to Implement**

1. **Configuration Panel**

   * Purpose: One-time setup for Oracle/Kerberos info.
   * Fields: Oracle Client Path, KRB5 Config, KRB5 Cache, User ID.
   * “Save Config” button.
   * **Disable after save.**

2. **Run Analysis Panel**

   * Fields: Last Event Timestamp, user KINIT confirmation checkbox.
   * Button: “Run Report” (enabled only if KINIT checkbox is checked and config is valid).
   * Button: “Generate Email Report” (enabled if report exists).
   * Button: “Copy Report Path to Clipboard” (enabled if report exists).
   * Button: “Copy OneNote Entry to Clipboard” (enabled if report exists).

3. **Database Status Panel**

   * Shows:

     * Connection status (“Connecting...”, “Connected”, “Error”).
     * Query status for each query (“Running”, “Done”, “Failed”).
     * Row count per query.
     * Last successful event time.

4. **Log Panel**

   * Scrollable, read-only text box or list.
   * Appends log lines in real-time (e.g., connection, query, export, error messages).
   * Shows critical events and errors in red, info in black/grey.

---

## **B. Modular Panel Implementation**

**Each panel is its own class** in `src/oracle_activity_monitor/view/panels/`:

* `configuration_panel.py`
* `run_analysis_panel.py`
* `database_status_panel.py`
* `log_panel.py`

**Sample directory:**

```text
src/oracle_activity_monitor/view/panels/
    configuration_panel.py
    run_analysis_panel.py
    database_status_panel.py
    log_panel.py
```

---

## **C. Main Application Layout**

* Use a grid or vertical/horizontal box layout in your main window (e.g., `app_ui.py`).
* Example layout:

  * Left: Configuration and Run Analysis Panels (vertical stack)
  * Right: Database Status Panel (top) and Log Panel (bottom)

---

## **D. Status/Feedback Mechanisms**

* **Status Labels:**
  Change color or icon based on result (green for success, red for error, yellow for running/warning).
* **Progress Indicators:**
  Optional: Use a progress bar for long-running query/report tasks.
* **Button States:**
  Enable/disable action buttons as appropriate (e.g., disable report actions until config and KINIT are set).
* **Log Entries:**
  Each user action, query, or error appends a line to the log panel.

---

## **E. Controller Wiring**

* The controller is responsible for:

  * Routing data between panels and services.
  * Updating status and log panels in response to service callbacks.
  * Enabling/disabling buttons based on current workflow state.

---

## **F. Example AI Prompt for a Panel**

> Write a CustomTkinter panel class called DatabaseStatusPanel that displays status for four queries (password, email, phone, token), with labels that turn green/yellow/red depending on status, and show the number of rows returned.

---

## **G. Testing**

* Manually verify each panel updates correctly in response to:

  * Configuration changes.
  * Query/DB success/failure.
  * Reporting/clipboard actions.
  * User errors (e.g., missing config, unchecked KINIT).
* Unit test logic for log/status updates (if separated from UI).

---

## **Summary Table: Step 9**

| Panel/Class         | Key Purpose/Behavior                                         |
| ------------------- | ------------------------------------------------------------ |
| ConfigurationPanel  | Setup and (optional) validation for Oracle/Kerberos settings |
| RunAnalysisPanel    | User input for report analysis, all action buttons           |
| DatabaseStatusPanel | Shows connection/query status, row counts, errors            |
| LogPanel            | Appends log messages in real-time, highlights errors         |
| Controller (Main)   | Orchestrates all UI flow, state, and event updates           |

---
