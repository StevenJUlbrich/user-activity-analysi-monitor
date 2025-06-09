# Step 3: Run Analysis Panel with KINIT Checkbox

## Objective
Create the Run Analysis Panel that matches the wireframe design with Last Time Event Reported field, KINIT checkbox, and action buttons.

## A. Run Analysis Panel Implementation

Create `src/client_activity_monitor/view/panels/run_analysis_panel.py`:

### Requirements (Based on Wireframe)
1. "Last Time Event Reported" field with datetime format
2. KINIT Executed checkbox
3. Run Report button (enabled only when KINIT is checked)
4. Report action buttons:
   - Generate Email Report
   - Copy Excel Path to Clipboard
   - OneNote Entry to Clipboard
   - Optional Save Report
5. All report actions disabled until a report exists

### UI Implementation

```python
import customtkinter as ctk
from datetime import datetime, timedelta
from typing import Callable, Dict

class RunAnalysisPanel(ctk.CTkFrame):
    def __init__(self, parent, callbacks: Dict[str, Callable]):
        """
        Args:
            parent: Parent widget
            callbacks: Dictionary of callback functions:
                - 'on_run_report': Called when Run Report clicked
                - 'on_generate_email': Called when Generate Email Report clicked
                - 'on_copy_excel_path': Called when Copy Excel Path clicked
                - 'on_copy_onenote': Called when OneNote Entry clicked
                - 'on_optional_save': Called when Optional Save Report clicked
        """
        super().__init__(parent)
        self.callbacks = callbacks
        self._create_widgets()
        self._initialize_datetime()
        
    def _create_widgets(self):
        """Create all UI widgets matching the wireframe."""
        # Title
        title = ctk.CTkLabel(self, text="Run Analysis", font=("Arial", 16, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Last Time Event Reported
        ctk.CTkLabel(self, text="Last Time Event Reported:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.datetime_entry = ctk.CTkEntry(self, placeholder_text="YYYY-MM-DD HH:MM")
        self.datetime_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # KINIT Checkbox
        self.kinit_var = ctk.BooleanVar()
        self.kinit_checkbox = ctk.CTkCheckBox(
            self, 
            text="KINIT Executed?",
            variable=self.kinit_var,
            command=self._on_kinit_toggle
        )
        self.kinit_checkbox.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Run Report Button
        self.run_report_button = ctk.CTkButton(
            self, 
            text="Run Report",
            command=self._on_run_report,
            state="disabled"
        )
        self.run_report_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Separator
        separator = ctk.CTkFrame(self, height=2, fg_color="gray70")
        separator.grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Report Action Buttons
        self.email_button = ctk.CTkButton(
            self,
            text="Generate Email Report",
            command=lambda: self.callbacks['on_generate_email'](),
            state="disabled"
        )
        self.email_button.grid(row=5, column=0, columnspan=2, pady=5)
        
        self.copy_excel_button = ctk.CTkButton(
            self,
            text="Copy Excel Path to Clipboard",
            command=lambda: self.callbacks['on_copy_excel_path'](),
            state="disabled"
        )
        self.copy_excel_button.grid(row=6, column=0, columnspan=2, pady=5)
        
        self.onenote_button = ctk.CTkButton(
            self,
            text="OneNote Entry to Clipboard",
            command=lambda: self.callbacks['on_copy_onenote'](),
            state="disabled"
        )
        self.onenote_button.grid(row=7, column=0, columnspan=2, pady=5)
        
        self.optional_save_button = ctk.CTkButton(
            self,
            text="Optional Save Report",
            command=lambda: self.callbacks['on_optional_save'](),
            state="disabled"
        )
        self.optional_save_button.grid(row=8, column=0, columnspan=2, pady=5)
        
        # Configure grid weights
        self.grid_columnconfigure(1, weight=1)
        
    def _initialize_datetime(self):
        """Set default datetime to current time."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.datetime_entry.delete(0, 'end')
        self.datetime_entry.insert(0, current_time)
        
    def _on_kinit_toggle(self):
        """Handle KINIT checkbox toggle."""
        if self.kinit_var.get():
            self.run_report_button.configure(state="normal")
        else:
            self.run_report_button.configure(state="disabled")
            
    def _on_run_report(self):
        """Handle Run Report button click."""
        # Get the last event time
        last_event_time = self.datetime_entry.get().strip()
        
        # Validate datetime format
        try:
            datetime.strptime(last_event_time, "%Y-%m-%d %H:%M")
        except ValueError:
            self._show_error("Invalid datetime format. Use YYYY-MM-DD HH:MM")
            return
            
        # Disable run button during execution
        self.run_report_button.configure(state="disabled", text="Running...")
        self.kinit_checkbox.configure(state="disabled")
        
        # Call the controller's run report callback
        self.callbacks['on_run_report'](last_event_time)
        
    def set_running_state(self, is_running: bool):
        """Update UI state when report is running or finished."""
        if is_running:
            self.run_report_button.configure(state="disabled", text="Running...")
            self.kinit_checkbox.configure(state="disabled")
        else:
            self.run_report_button.configure(
                state="normal" if self.kinit_var.get() else "disabled",
                text="Run Report"
            )
            self.kinit_checkbox.configure(state="normal")
            
    def enable_report_actions(self, enable: bool):
        """Enable or disable all report action buttons."""
        state = "normal" if enable else "disabled"
        self.email_button.configure(state=state)
        self.copy_excel_button.configure(state=state)
        self.onenote_button.configure(state=state)
        self.optional_save_button.configure(state=state)
        
    def get_last_event_time(self) -> str:
        """Get the last event time from the entry field."""
        return self.datetime_entry.get().strip()
        
    def update_last_event_time(self, timestamp: str):
        """Update the last event time field (for successful runs)."""
        self.datetime_entry.delete(0, 'end')
        self.datetime_entry.insert(0, timestamp)
        
    def _show_error(self, message: str):
        """Show error message."""
        # In a real implementation, use CTkMessagebox or similar
        print(f"Error: {message}")
```

## B. Controller Integration

The controller handles the Run Analysis panel callbacks:

```python
class MainController:
    def __init__(self):
        # ... other initialization ...
        self.report_path = None
        self.report_data = None
        
    def on_run_report(self, last_event_time_str: str):
        """
        Handle Run Report button click.
        
        Args:
            last_event_time_str: Last event time as string "YYYY-MM-DD HH:MM"
        """
        try:
            # Parse the last event time
            last_event_time = datetime.strptime(last_event_time_str, "%Y-%m-%d %H:%M")
            
            # Calculate start_date (30 days ago)
            start_date = datetime.now() - timedelta(days=30)
            
            # Log the analysis start
            user_sid = self.config_manager.get_user_sid()
            self.logger.info(f"Analysis started by {user_sid} at {datetime.now()}")
            self.logger.info(f"Last event time: {last_event_time}")
            self.logger.info(f"Query start date: {start_date}")
            
            # Start analysis in separate thread
            self.analysis_thread = threading.Thread(
                target=self._run_analysis_thread,
                args=(start_date, last_event_time)
            )
            self.analysis_thread.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start analysis: {e}")
            self.run_analysis_panel.set_running_state(False)
            
    def _run_analysis_thread(self, start_date: datetime, last_event_time: datetime):
        """Run the analysis in a separate thread."""
        try:
            # Execute queries (Step 4)
            results = self.database_executor.execute_all_databases(
                start_date=start_date,
                progress_callback=self.update_database_status,
                cancel_event=self.cancel_event
            )
            
            # Merge and filter results (Step 5)
            filtered_data = self.merge_filter_service.process_results(
                results, 
                last_event_time
            )
            
            # Generate report (Step 6)
            if not filtered_data.empty:
                self.report_path = self.report_generator.create_excel_report(filtered_data)
                self.report_data = filtered_data
                
                # Enable report actions
                self.run_analysis_panel.enable_report_actions(True)
                
                # Update last event time to now
                new_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                self.run_analysis_panel.update_last_event_time(new_time)
                
                self.logger.info(f"Report generated: {self.report_path}")
            else:
                self.logger.info("No users met all criteria")
                
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
        finally:
            self.run_analysis_panel.set_running_state(False)
            
    def on_generate_email(self):
        """Handle Generate Email Report button."""
        if self.report_path:
            # Implementation in Step 7
            pass
            
    def on_copy_excel_path(self):
        """Handle Copy Excel Path to Clipboard button."""
        if self.report_path:
            # Implementation in Step 6
            pass
            
    def on_copy_onenote(self):
        """Handle OneNote Entry to Clipboard button."""
        if self.report_data is not None:
            # Implementation in Step 8
            pass
            
    def on_optional_save(self):
        """Handle Optional Save Report button (CSV export)."""
        if self.report_data is not None:
            # Save as CSV
            csv_path = self.report_generator.create_csv_report(self.report_data)
            self.logger.info(f"CSV report saved: {csv_path}")
```

## C. Key Implementation Notes

1. **Last Time Event Reported**: 
   - User can view/edit this field
   - Updated to current time after successful report generation
   - Used for filtering results to last 24 hours

2. **KINIT Checkbox**: 
   - Must be checked to enable Run Report button
   - Simple user confirmation, no actual KINIT validation

3. **Start Date**: 
   - Always calculated as 30 days ago
   - NOT user-configurable
   - Passed to queries as `:start_date` parameter

4. **Report Actions**: 
   - All disabled until a report is successfully generated
   - Remain enabled for subsequent actions on the same report

5. **Threading**: 
   - Analysis runs in separate thread to keep UI responsive
   - UI updates via callbacks

## D. State Flow

1. **Initial State**: 
   - KINIT unchecked
   - Run Report disabled
   - All report actions disabled

2. **KINIT Checked**: 
   - Run Report enabled

3. **Running Analysis**: 
   - Run Report shows "Running..."
   - KINIT checkbox disabled
   - Report actions remain disabled

4. **Analysis Complete**: 
   - Run Report back to normal
   - KINIT checkbox enabled
   - Report actions enabled if report generated
   - Last event time updated

## Next Step
After implementing Run Analysis Panel, proceed to Step 4: Database Query Execution with concurrent multi-database support.