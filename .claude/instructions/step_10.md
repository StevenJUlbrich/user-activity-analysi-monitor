# **Step 10: Validation, Error Handling, and Testing**

## **Objective**

* Ensure **all user inputs, configuration, and external actions** are validated before execution.
* Provide clear, user-friendly error messages and log all major failures.
* Build a strong foundation for automated and manual testing to catch regressions and ensure future-proofing.

---

## **A. Input and Configuration Validation**

**Where to Validate:**

* **Configuration Panel:**

  * Ensure all fields (Oracle client path, KRB5 config, cache, user ID) are not empty and point to valid files/directories (where possible).
  * Validate before enabling the “Save Config” button.
* **Run Analysis Panel:**

  * Only allow “Run Report” when config is valid and KINIT checkbox is checked.
  * Last Event Timestamp must be a valid date/time format.
* **Email/OneNote Actions:**

  * Buttons enabled only if a report exists (and path is available).

**How to Implement:**

* Use field-level validation (on change/blur events) in CustomTkinter.
* For file path validation, use Python’s `Path.exists()` or similar.
* Add tooltips or warning icons for invalid fields.

---

## **B. Error Handling**

**In Each Layer:**

* **Model/Service:**

  * Wrap all external actions (file I/O, DB, clipboard, mailto launch) in try/except blocks.
  * Raise or log exceptions with clear, actionable messages.
* **Controller:**

  * Catch all errors from services; update log panel and show message dialogs to the user.
* **UI:**

  * Show pop-up messages or status color changes for failures (e.g., file not found, DB connect error, clipboard unavailable).

**Example for Logging and User Feedback:**

```python
try:
    result = repo.run_query(sql_path, params)
except Exception as e:
    log_panel.append(f"Query failed: {e}")
    messagebox.showerror("Database Error", f"Failed to execute query: {e}")
```

---

## **C. Testing Strategy**

1. **Unit Tests (tests/unit/)**

   * For config read/write logic (test with valid/invalid YAML).
   * For query repository (mock OracleKerberosConnection, test error handling).
   * For merge/filter logic (edge cases: empty/partial DataFrames).
   * For report export (ensure files are created, test with empty DataFrame).
   * For clipboard utils (mock pyperclip, test with/without data).

2. **Integration/Workflow Tests (tests/integration/)**

   * Simulate “happy path”: full run from config → report → clipboard/email.
   * Simulate failures: invalid config, failed DB connection, empty results.

3. **Manual/UX Testing**

   * Test all UI flows:

     * Config entry and validation
     * KINIT checkbox gating
     * Query/run with good and bad config
     * Reporting and email/OneNote clipboard steps
     * Error dialogs and log output for every failure point

---

## **D. User Guidance and Documentation**

* **README.md and user\_guide.md:**

  * List common errors and troubleshooting steps.
  * Describe validation logic (e.g., which fields must be present, how errors are shown).
* **In-app tooltips/help:**

  * “What does this mean?” links or hover help for non-obvious fields or error messages.

---

## **E. Example AI Prompt for Unit Test**

> Generate a pytest unit test for the ConfigManager’s save and load methods, testing with valid, invalid, and missing config files.

---

## **Summary Table: Step 10**

| Aspect           | What to Validate/Test                           | Where Implemented               |
| ---------------- | ----------------------------------------------- | ------------------------------- |
| Input Validation | Config, analysis inputs, paths, time fields     | UI, config\_manager, controller |
| Error Handling   | All I/O, DB, export, clipboard, mailto failures | Services, controller, UI        |
| Testing          | Unit, integration, manual/UX                    | tests/unit, tests/integration   |
| Documentation    | Describe validation, errors, troubleshooting    | README, user\_guide, tooltips   |
| Logging          | Log all errors/actions for transparency/audit   | Log panel, file log if desired  |

---
