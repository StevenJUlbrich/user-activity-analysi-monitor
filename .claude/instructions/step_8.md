# Step 8: OneNote Integration (Summary Entry)

## Objective
Create a simple summary entry for OneNote containing only:
- SID (who ran the report)
- Date/time the report was run
- Last date/time found in the report
- Number of users found

## A. OneNote Service Implementation

Create `src/client_activity_monitor/model/integrations/onenote_service.py`:

### Purpose
Create a simple tab-separated summary entry for OneNote logging.

### Implementation

```python
import pandas as pd
from datetime import datetime
import pyperclip
from loguru import logger

class OneNoteService:
    """
    Creates simple summary entries for OneNote logging.
    """
    
    def copy_summary_to_clipboard(
        self,
        user_sid: str,
        report_run_time: datetime,
        last_event_time: datetime,
        user_count: int
    ) -> bool:
        """
        Create and copy a summary entry to clipboard for OneNote.
        
        Args:
            user_sid: SID of user who ran the report
            report_run_time: When the report was generated
            last_event_time: Last event time used in analysis
            user_count: Number of users found in report
            
        Returns:
            True if successfully copied to clipboard
        """
        try:
            # Create tab-separated summary entry
            summary_entry = self._create_summary_entry(
                user_sid,
                report_run_time,
                last_event_time,
                user_count
            )
            
            # Copy to clipboard
            pyperclip.copy(summary_entry)
            
            logger.info(f"OneNote summary copied to clipboard")
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy OneNote summary: {e}")
            return False
            
    def _create_summary_entry(
        self,
        user_sid: str,
        report_run_time: datetime,
        last_event_time: datetime,
        user_count: int
    ) -> str:
        """
        Create the formatted summary entry.
        
        Format: SID\tRun Date/Time\tLast Event Date/Time\tUsers Found
        """
        # Format dates/times
        run_time_str = report_run_time.strftime("%Y-%m-%d %H:%M:%S")
        last_event_str = last_event_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Create tab-separated entry
        summary_parts = [
            user_sid,
            run_time_str,
            last_event_str,
            str(user_count)
        ]
        
        return '\t'.join(summary_parts)
        
    def get_summary_with_headers(
        self,
        user_sid: str,
        report_run_time: datetime,
        last_event_time: datetime,
        user_count: int
    ) -> str:
        """
        Create summary entry with headers (optional format).
        
        Returns:
            Multi-line string with headers and values
        """
        headers = ["SID", "Report Run Time", "Last Event Time", "Users Found"]
        values = [
            user_sid,
            report_run_time.strftime("%Y-%m-%d %H:%M:%S"),
            last_event_time.strftime("%Y-%m-%d %H:%M:%S"),
            str(user_count)
        ]
        
        # Create two-row table (headers and values)
        header_row = '\t'.join(headers)
        value_row = '\t'.join(values)
        
        return f"{header_row}\n{value_row}"
```

## B. Controller Integration

Update the controller to handle OneNote summary:

```python
class MainController:
    def on_copy_onenote(self):
        """Handle OneNote Entry to Clipboard button."""
        if self.last_report_data is not None and self.last_report_path:
            try:
                # Get required data
                user_sid = self.config_manager.get_user_sid()
                report_run_time = datetime.now()
                last_event_time = datetime.strptime(
                    self.run_analysis_panel.get_last_event_time(),
                    "%Y-%m-%d %H:%M"
                )
                user_count = len(self.last_report_data)
                
                # Create OneNote service
                onenote_service = OneNoteService()
                
                # Copy summary to clipboard
                success = onenote_service.copy_summary_to_clipboard(
                    user_sid=user_sid,
                    report_run_time=report_run_time,
                    last_event_time=last_event_time,
                    user_count=user_count
                )
                
                if success:
                    self.show_message(
                        "OneNote Summary Copied",
                        "Summary copied to clipboard:\n\n"
                        f"SID: {user_sid}\n"
                        f"Run Time: {report_run_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"Last Event: {last_event_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"Users Found: {user_count}\n\n"
                        "Paste into OneNote with Ctrl+V"
                    )
                else:
                    self.show_error(
                        "Copy Failed",
                        "Failed to copy summary to clipboard"
                    )
                    
            except Exception as e:
                logger.error(f"OneNote summary failed: {e}")
                self.show_error("OneNote Error", str(e))
        else:
            self.show_warning("No Report", "No report available for OneNote summary")
```

## C. OneNote Entry Format

### Standard Format (Tab-separated, single line):
```
A12345	2024-01-15 14:30:45	2024-01-15 14:00:00	5
```

This pastes into OneNote as a single row with 4 columns:
- SID: A12345
- Report Run Time: 2024-01-15 14:30:45
- Last Event Time: 2024-01-15 14:00:00
- Users Found: 5

### With Headers (Optional, if user needs column labels):
```
SID	Report Run Time	Last Event Time	Users Found
A12345	2024-01-15 14:30:45	2024-01-15 14:00:00	5
```

## D. Usage Workflow

1. User clicks "OneNote Entry to Clipboard"
2. System copies the 4-field summary to clipboard
3. User opens OneNote to their logging page/table
4. User presses Ctrl+V to paste
5. OneNote creates a table row with the 4 values

## E. Key Features

1. **Simple Summary Only**: Just 4 essential fields
2. **Tab-Separated**: Creates proper columns in OneNote
3. **Single Line**: Easy to append to existing OneNote logs
4. **Audit Trail**: Shows who ran report and when
5. **Quick Reference**: Key metrics without full data

## F. Benefits

1. **Minimal Data**: Only essential audit information
2. **Log-Friendly**: Perfect for maintaining activity logs
3. **Quick Entry**: Single line for easy tracking
4. **Consistent Format**: Same 4 fields every time
5. **No Excel Data**: Just the summary metrics

## Next Step
After implementing the corrected OneNote integration, proceed to Step 9: UI Panels and Status Feedback for the Database Status and Log panels.