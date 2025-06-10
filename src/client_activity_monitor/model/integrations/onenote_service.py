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