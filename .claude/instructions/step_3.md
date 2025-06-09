# **Step 3 (Final): KINIT as User Checkbox**

### **Objective**

* The user confirms (by checkbox) that they have run KINIT and have valid Kerberos credentials.
* The application **does not** check, validate, or invoke any Kerberos process.
* All DB/report actions are gated on this checkbox being ticked.

---

### **A. UI Panel Changes**

* **Add a Checkbox:**

  * Label: “I have run KINIT and have a valid Kerberos ticket for this session.”
* **Enable “Run Report” and other actions** only if the checkbox is checked.
* **Show warning or tooltip** if user tries to proceed without checking.

**Sample Pseudocode:**

```python
self.kinit_checkbox = ctk.CTkCheckBox(self, text="I have run KINIT and have a valid Kerberos ticket")
self.kinit_checkbox.pack()
self.run_report_button = ctk.CTkButton(self, text="Run Report", state="disabled")

def on_kinit_checkbox_change():
    if self.kinit_checkbox.get():
        self.run_report_button.configure(state="normal")
    else:
        self.run_report_button.configure(state="disabled")
```

* Hook `on_kinit_checkbox_change` to the checkbox’s state change event.

---

### **B. Controller Changes**

* No need for a KinitService module or any subprocess/validation logic.
* The controller **only checks the state of the checkbox** before running report/DB actions.

---

### **C. Logging and UX**

* Optionally log when the checkbox is checked/unchecked (for audit).
* Provide a tooltip:
  “Check this box only after running ‘kinit’ in your terminal and obtaining a valid Kerberos ticket.”

---

### **D. Documentation/Instructions**

* Update user guide/docs:

  * “You are responsible for ensuring your Kerberos credentials are current.
    Before using this app, open your terminal and run: `kinit`.”

---

## **Other Sections Requiring Update**

### **Section Updates Needed:**

1. **Step 3 – KinitService & Integration**

   * **Remove** all references to `KinitService`, subprocess, or Kerberos ticket checking code.
   * **Replace** with checkbox UI logic as above.

2. **UI Panel Description (Run Analysis Section):**

   * Instead of “Run KINIT” or “Check Kerberos Status” buttons, describe the checkbox.
   * State that this must be checked to enable “Run Report”.

3. **Testing Section:**

   * **No need** to test Kerberos or subprocess behavior.
   * Instead, test:

     * Checkbox must be checked to proceed.
     * State of app if checkbox is unchecked.

4. **Logging Section:**

   * Log only UI-level events (checkbox checked/unchecked), not system state.

5. **Documentation/User Guide:**

   * Clearly document the user’s manual responsibility for KINIT.
   * Remove all workflow for “automatically checking Kerberos credentials.”

---

### **No Changes Needed For:**

* **Database connection module (`ez_connect_oracle.py`):**
  This continues to assume credentials are valid and does not require changes.
* **Configuration/ConfigManager logic.**
* **Query, reporting, email, or OneNote sections.**

---

## **Summary Table: Step 3 (Checkbox Approach)**

| Sub-Step     | New Action                                   | Previous Actions to Remove         |
| ------------ | -------------------------------------------- | ---------------------------------- |
| UI Checkbox  | Add a manual “KINIT completed” checkbox      | Remove any “Run/Check KINIT” logic |
| Controller   | Gate all DB/report actions on checkbox       | Remove KinitService integration    |
| Logging/Docs | Log/guide on checkbox only                   | Remove Kerberos ticket checking    |
| Testing      | Test only checkbox gating, not kinit process | Remove process-mocking tests       |

---
