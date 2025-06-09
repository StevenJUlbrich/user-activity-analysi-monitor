# **Step 6: Report Generation & Export**

## **Objective**

* **Export the filtered, merged DataFrame (from Step 5) as an Excel file** (and optionally CSV).
* Save the file to a reports directory with a timestamped filename.
* Allow the report path to be copied to clipboard via the UI.
* Prepare the report for attachment to an email (in the next step).

---

## **A. ReportingService Module**

**Directory:**
`src/client_activity_monitor/model/services/reporting_service.py`

**Core Responsibilities:**

* Export DataFrame to Excel (and optionally CSV).
* Return/save file path for use in UI, email, and OneNote integration.

**Example Implementation:**

```python
import pandas as pd
from pathlib import Path
from datetime import datetime

class ReportingService:
    """
    Handles exporting results to Excel and CSV, manages report paths.
    """
    def __init__(self, report_dir="reports"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(exist_ok=True)

    def export_to_excel(self, df: pd.DataFrame, prefix: str = "user_activity_report") -> Path:
        """
        Saves DataFrame to an Excel file in the reports directory.

        Args:
            df: DataFrame to export
            prefix: Filename prefix (default: user_activity_report)

        Returns:
            Path to the saved Excel file
        """
        if df.empty:
            raise ValueError("No data to export.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.report_dir / f"{prefix}_{timestamp}.xlsx"
        df.to_excel(file_path, index=False)
        return file_path

    def export_to_csv(self, df: pd.DataFrame, prefix: str = "user_activity_report") -> Path:
        """
        Saves DataFrame to a CSV file.

        Returns:
            Path to the saved CSV file
        """
        if df.empty:
            raise ValueError("No data to export.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.report_dir / f"{prefix}_{timestamp}.csv"
        df.to_csv(file_path, index=False)
        return file_path
```

---

## **B. Clipboard Utility Module**

**Directory:**
`src/client_activity_monitor/common/clipboard_utils.py`

**Core Responsibility:**
Allow copying the generated report file path to the clipboard (for easy email attachment).

**Example Implementation:**

```python
import pyperclip
from pathlib import Path

def copy_path_to_clipboard(path: Path):
    pyperclip.copy(str(path))
```

> **Install**: `poetry add pyperclip`

---

## **C. Controller/Workflow Integration**

* After merge/filter, controller calls `ReportingService.export_to_excel(filtered_df)`.
* Stores returned file path.
* If export succeeds, **enables “Copy Report Path to Clipboard” button** in the UI.
* User can then click the button to copy the path (for manual attachment in Outlook).

---

## **D. UI Integration**

* Show report path in the UI (e.g., label or readonly textbox).
* “Copy Path” button calls clipboard utility.
* **If no results:**

  * Show message: “No report generated—no qualifying users.”

---

## **E. Error Handling**

* Block export/copy if DataFrame is empty.
* Show user-friendly error if export fails (e.g., file permission, disk full).
* Log all export actions/results.

---

## **F. Testing**

* **Unit test:**

  * Check export with real/small DataFrames.
  * Try export with empty DataFrame (should raise).
* **Manual test:**

  * Confirm files save correctly, clipboard utility works.

---

## **G. Example AI Prompt**

> Write a Python class that exports a pandas DataFrame to a timestamped Excel file in a reports directory, and a function to copy the file path to clipboard using pyperclip.

---

## **Summary Table: Step 6**

| Sub-Step          | Action/Behavior                                           |
| ----------------- | --------------------------------------------------------- |
| ReportingService  | Exports merged DataFrame to Excel (and CSV), returns path |
| Clipboard Utility | Copies report path to clipboard for email/manual use      |
| Controller        | Calls export, manages UI state, enables copy button       |
| UI                | Shows report path, enables copy button only on success    |
| Error Handling    | Handles empty DataFrame, export errors, logs actions      |
| Testing           | Ensures correct file generation, clipboard works          |

---

**Ready to proceed with Step 7 (Email Integration), or want code samples/UI stubs for report export and copy-to-clipboard?**
Let me know how deep you want to go for this brick!
