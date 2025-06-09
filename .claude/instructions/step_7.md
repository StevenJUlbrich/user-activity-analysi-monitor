# **Updated Step 7: Email Integration (Mailto/Web URL Only)**

## **Key Points**

* No `win32com`, no desktop Outlook automation.
* **Always use a mailto link**—opens the user’s default mail client (Outlook Web, desktop, or other), pre-filling the message but not attaching files.
* User will **manually attach the report file** (using the copy-to-clipboard button you provide).

---

### **A. OutlookService (Web/Mailto Only)**

**File:** `src/client_activity_monitor/model/integrations/outlook_service.py`

```python
import webbrowser
from urllib.parse import quote

def create_outlook_email(recipients, subject, body, attachment_path=None):
    """
    Launches default mail client with pre-filled fields.
    If attachment_path is provided, include instructions in the body.
    """
    to_str = ";".join(recipients)
    body_full = body
    if attachment_path:
        body_full += f"\n\n[Please manually attach the report: {attachment_path}]"

    mailto_url = (
        f"mailto:{to_str}"
        f"?subject={quote(subject)}"
        f"&body={quote(body_full)}"
    )
    webbrowser.open(mailto_url)
```

* **recipients:** List of strings (email addresses)
* **subject:** E.g., “User Activity Report – {date or time window}”
* **body:** May include a summary (e.g., number of users reported)
* **attachment\_path:** (optional) Will appear as a reminder line in the body

---

### **B. UI Integration**

* **Button:** “Generate Email Report” (enabled only if a report exists)
* **Behavior:**

  * Reads recipients from config file.
  * Prepares subject and body, referencing the time window and report summary.
  * Calls `create_outlook_email()`.
  * Shows a message in the UI:
    “Draft email created in your mail client. Please use ‘Copy Report Path’ to attach the exported report file.”

---

### **C. Controller/Workflow**

* Validates recipients and report existence.
* Handles errors (e.g., if no mail client is available, logs the failure and notifies user).

---

### **D. Documentation/User Instructions**

* “This application does not attach the report automatically due to security policy.
  When the email draft opens, use the ‘Copy Report Path’ button to locate and attach the exported file.”

---

### **E. Testing**

* Confirm that clicking “Generate Email Report” opens the mail client, pre-fills all fields, and includes the reminder for attachment.
* Check with different platforms (Windows, Mac, Linux, Outlook Web, etc.).

---

### **What to Remove**

* **No use of win32com or any desktop/COM automation.**
* No logic attempting direct file attachment in the draft email.

---

## **Summary Table: Step 7 (Web/Mailto Only)**

| Sub-Step       | Action/Behavior                                                   |
| -------------- | ----------------------------------------------------------------- |
| OutlookService | Generates mailto URL; opens email draft in browser/mail client    |
| UI             | Button for “Generate Email Report”; includes attach reminder      |
| Controller     | Fills fields, calls OutlookService, logs and shows result/failure |
| Error Handling | Informs user if browser/mail client is not available              |
| Docs           | User must attach file manually, using Copy Path button            |

---
