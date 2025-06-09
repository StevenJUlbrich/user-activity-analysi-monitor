# **Step 8: OneNote Integration (Clipboard-Based Entry)**

## **Objective**

* Convert the filtered report DataFrame (from Step 5) into a **tab-separated or table-formatted string**.
* Copy this string to the clipboard.
* Instruct the user to paste it into their desired OneNote page/table.

---

## **A. OneNoteService (Clipboard Generator)**

**Directory:**
`src/client_activity_monitor/model/integrations/onenote_service.py`

**Example Implementation:**

```python
import pyperclip
import pandas as pd

def dataframe_to_onenote_table(df: pd.DataFrame) -> str:
    """
    Converts a DataFrame into a OneNote-compatible tab-separated table string.
    """
    # Optional: Limit columns or rows, or reformat as needed for OneNote
    lines = []
    # Add headers
    lines.append('\t'.join(map(str, df.columns)))
    # Add rows
    for _, row in df.iterrows():
        lines.append('\t'.join(map(str, row.values)))
    return '\n'.join(lines)

def copy_onenote_entry_to_clipboard(df: pd.DataFrame):
    """
    Copies the DataFrame as a OneNote-compatible table to clipboard.
    """
    table_str = dataframe_to_onenote_table(df)
    pyperclip.copy(table_str)
```

> **(Install pyperclip if you haven’t: `poetry add pyperclip`)**

---

## **B. UI Integration**

* **Button:** “Copy OneNote Entry to Clipboard”
* **Behavior:**

  * Enabled only if report data exists.
  * When clicked, copies the pre-formatted table to clipboard.
  * Show a message:
    “Report data copied to clipboard. Paste into your OneNote page (Ctrl+V).”

---

## **C. Controller Workflow**

* After report is generated and merged DataFrame exists:

  * Enable the OneNote clipboard button.
  * When user clicks, call `copy_onenote_entry_to_clipboard(filtered_df)`.

---

## **D. User Guidance/Instructions**

* Display help text:
  “To log this event in OneNote, click ‘Copy OneNote Entry to Clipboard’, then go to your OneNote page or table and press Ctrl+V to paste.”
* Optional: Add “Copied!” or error feedback if clipboard action fails.

---

## **E. Testing**

* Use small, known DataFrames—copy to clipboard, then paste into OneNote and confirm correct appearance.
* Test with large/special character data for edge cases.

---

## **F. Example AI Prompt**

> Write a function that converts a pandas DataFrame to a tab-separated string for pasting into OneNote tables, and copies it to the clipboard using pyperclip.

---

## **Summary Table: Step 8**

| Sub-Step       | Action/Behavior                                               |
| -------------- | ------------------------------------------------------------- |
| OneNoteService | Formats DataFrame as tab-separated table, copies to clipboard |
| UI             | Button for “Copy OneNote Entry to Clipboard”                  |
| Controller     | Wires button to service, shows success/error to user          |
| Docs/UX        | Guides user to paste into OneNote (Ctrl+V)                    |
| Testing        | Ensures pasted format appears as a OneNote table              |

---
