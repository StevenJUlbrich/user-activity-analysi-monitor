# **Step 2 (Updated): ConfigManager & Configuration UI Panel**

## **Objective**

* Allow the user to enter and save Oracle/Kerberos configuration and related info via the UI.
* Store this configuration in a YAML file, fully compatible with your `ez_connect_oracle.py` connection module.

---

## **A. ConfigManager Module**

* **Purpose:**
  Centralizes reading and writing of the YAML configuration file.
* **Key Actions:**

  * Implements `load()` and `save()` methods for the app’s settings.
  * Ensures file schema matches what your Oracle DB connection code expects.

---

## **B. Configuration UI Panel**

* **Purpose:**
  Provides a GUI form for users to enter:

  * Oracle Instant Client path
  * KRB5 config path
  * KRB5 cache file path
  * User ID (and other needed info)
* **Key Actions:**

  * Labeled entry fields for each parameter.
  * “Save Config” button (validates and persists to YAML).
  * Pre-fills fields with saved config (if present).
  * On successful save, optionally disables further edits or shows confirmation.
* **No logic for Kerberos ticket (KINIT) handling here**—that’s handled in Step 3 with a simple checkbox.

---

## **C. Controller Wiring**

* The controller ensures:

  * On first launch, user fills config and saves it.
  * Other app logic only proceeds if a valid config exists.
  * Reads config via ConfigManager, passes to connection logic as needed.

---

## **D. Validation & UX**

* Validate all required fields before enabling “Save”.
* Show clear error messages for missing/invalid paths.
* **No Kerberos credential checking**—the UI is only for config.

---

## **E. Testing**

* **Unit tests** for ConfigManager (YAML save/load/overwrite).
* **UI/manual tests:** Fill/save/load config, confirm data persists and pre-fills correctly.

---

## **F. What Changed in This Update?**

* **No need** for any KINIT checkbox or status in the config panel itself.
* All Kerberos validation or user workflow is handled in the next step (Step 3), not during config entry.

---

## **Summary Table: Step 2**

| Sub-Step            | Action/Behavior                                      |
| ------------------- | ---------------------------------------------------- |
| ConfigManager       | Centralizes YAML config read/write for the app       |
| Configuration Panel | UI for config entry, validation, saving, pre-filling |
| Controller Wiring   | Gating workflow on presence of valid config          |
| Validation          | Ensures all fields are present/valid before saving   |
| Testing             | Focused on config I/O and UI field persistence       |
| Out of Scope        | No KINIT handling, status, or checkbox here          |

---
