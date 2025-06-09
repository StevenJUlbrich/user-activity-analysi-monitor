# Step 9: UI Panels and Status Feedback

## Objective
Implement the Database Status Panel and Log Panel to provide real-time feedback during query execution and maintain an activity log.

## A. Database Status Panel Implementation

Create `src/client_activity_monitor/view/panels/database_status_panel.py`:

### Purpose
Display real-time status for each database and query during execution, matching the wireframe design.

### Implementation

```python
import customtkinter as ctk
from typing import Dict, Optional
from datetime import datetime
from loguru import logger

class DatabaseStatusPanel(ctk.CTkFrame):
    """
    Displays status for each database and its queries during execution.
    """
    
    def __init__(self, parent):
        """Initialize the database status panel."""
        super().__init__(parent)
        self.database_widgets = {}
        self.query_widgets = {}
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the initial UI structure."""
        # Title
        title = ctk.CTkLabel(self, text="Database Status", font=("Arial", 16, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Overall status
        self.overall_status_label = ctk.CTkLabel(self, text="Overall Status: Idle")
        self.overall_status_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Placeholder for dynamic database status
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
        self.status_frame.grid_columnconfigure(0, weight=1)
        
    def initialize_databases(self, database_configs):
        """
        Initialize status display for configured databases.
        
        Args:
            database_configs: List of database configurations from ConfigManager
        """
        # Clear existing widgets
        for widget in self.status_frame.winfo_children():
            widget.destroy()
        self.database_widgets.clear()
        self.query_widgets.clear()
        
        row = 0
        for db_config in database_configs:
            # Database name and status
            db_label = ctk.CTkLabel(
                self.status_frame,
                text=f"Database: {db_config.name}",
                font=("Arial", 12, "bold")
            )
            db_label.grid(row=row, column=0, sticky="w", pady=(10, 5))
            
            db_status = ctk.CTkLabel(
                self.status_frame,
                text="Status: Not Connected",
                text_color="gray"
            )
            db_status.grid(row=row, column=1, sticky="e", pady=(10, 5))
            
            self.database_widgets[db_config.name] = {
                'label': db_label,
                'status': db_status
            }
            row += 1
            
            # Query status for each query in this database
            for query_def in db_config.sql_queries:
                query_label = ctk.CTkLabel(
                    self.status_frame,
                    text=f"  • {query_def.name}:",
                    font=("Arial", 10)
                )
                query_label.grid(row=row, column=0, sticky="w", padx=(20, 0))
                
                query_status = ctk.CTkLabel(
                    self.status_frame,
                    text="Pending",
                    text_color="gray"
                )
                query_status.grid(row=row, column=1, sticky="e")
                
                # Store reference with database name and query name
                key = f"{db_config.name}:{query_def.name}"
                self.query_widgets[key] = {
                    'label': query_label,
                    'status': query_status
                }
                row += 1
                
        # Add spacing at bottom
        self.status_frame.grid_rowconfigure(row, weight=1)
        
    def update_database_status(
        self,
        database_name: str,
        query_name: str,
        status: str,
        row_count: Optional[int] = None
    ):
        """
        Update status for a specific database or query.
        
        Args:
            database_name: Name of the database
            query_name: Name of the query or "all" for database-level status
            status: One of "connecting", "running", "completed", "failed", "cancelled"
            row_count: Number of rows returned (only for completed queries)
        """
        if query_name == "all":
            # Database-level status update
            if database_name in self.database_widgets:
                status_widget = self.database_widgets[database_name]['status']
                self._update_status_widget(status_widget, status, True)
                
                # Update overall status
                self._update_overall_status()
        else:
            # Query-level status update
            key = f"{database_name}:{query_name}"
            if key in self.query_widgets:
                status_widget = self.query_widgets[key]['status']
                
                if status == "completed" and row_count is not None:
                    status_text = f"Complete ({row_count} rows)"
                else:
                    status_text = status.title()
                    
                self._update_status_widget(status_widget, status, False, status_text)
                
    def _update_status_widget(self, widget, status: str, is_database: bool, custom_text: str = None):
        """Update a status widget with appropriate color and text."""
        # Define status colors
        status_colors = {
            "connecting": "orange",
            "running": "blue",
            "completed": "green",
            "failed": "red",
            "cancelled": "gray",
            "idle": "gray"
        }
        
        color = status_colors.get(status.lower(), "gray")
        
        if custom_text:
            text = custom_text
        elif is_database:
            text = f"Status: {status.title()}"
        else:
            text = status.title()
            
        widget.configure(text=text, text_color=color)
        
    def _update_overall_status(self):
        """Update the overall status based on all database statuses."""
        # Check all database statuses
        all_statuses = []
        for db_widgets in self.database_widgets.values():
            status_text = db_widgets['status'].cget("text")
            if ":" in status_text:
                status = status_text.split(":")[1].strip().lower()
                all_statuses.append(status)
                
        # Determine overall status
        if any(s == "failed" for s in all_statuses):
            overall = "Failed"
            color = "red"
        elif any(s == "running" for s in all_statuses):
            overall = "Running"
            color = "blue"
        elif any(s == "connecting" for s in all_statuses):
            overall = "Connecting"
            color = "orange"
        elif all(s == "completed" for s in all_statuses) and all_statuses:
            overall = "Completed"
            color = "green"
        else:
            overall = "Idle"
            color = "gray"
            
        self.overall_status_label.configure(
            text=f"Overall Status: {overall}",
            text_color=color
        )
        
    def reset_all_status(self):
        """Reset all statuses to initial state."""
        self.overall_status_label.configure(
            text="Overall Status: Idle",
            text_color="gray"
        )
        
        for db_widgets in self.database_widgets.values():
            db_widgets['status'].configure(
                text="Status: Not Connected",
                text_color="gray"
            )
            
        for query_widgets in self.query_widgets.values():
            query_widgets['status'].configure(
                text="Pending",
                text_color="gray"
            )
```

## B. Log Panel Implementation

Create `src/client_activity_monitor/view/panels/log_panel.py`:

### Purpose
Display scrollable log messages with color-coded status levels.

### Implementation

```python
import customtkinter as ctk
from datetime import datetime
from typing import Literal
import queue
import threading

class LogPanel(ctk.CTkFrame):
    """
    Scrollable log panel for displaying application messages.
    """
    
    def __init__(self, parent):
        """Initialize the log panel."""
        super().__init__(parent)
        self.log_queue = queue.Queue()
        self._create_widgets()
        self._start_log_updater()
        
    def _create_widgets(self):
        """Create the log panel UI."""
        # Title
        title = ctk.CTkLabel(self, text="Logs:", font=("Arial", 14, "bold"))
        title.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        # Log text widget with scrollbar
        self.log_text = ctk.CTkTextbox(
            self,
            height=200,
            width=600,
            wrap="word",
            state="disabled"
        )
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configure grid weights
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Configure text tags for different log levels
        self.log_text.tag_config("INFO", foreground="black")
        self.log_text.tag_config("SUCCESS", foreground="green")
        self.log_text.tag_config("WARNING", foreground="orange")
        self.log_text.tag_config("ERROR", foreground="red")
        self.log_text.tag_config("DEBUG", foreground="gray")
        
    def log(
        self,
        message: str,
        level: Literal["INFO", "SUCCESS", "WARNING", "ERROR", "DEBUG"] = "INFO"
    ):
        """
        Add a log message to the panel.
        
        Args:
            message: The message to log
            level: The log level for color coding
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        # Queue the log entry for thread-safe updates
        self.log_queue.put((log_entry, level))
        
    def _start_log_updater(self):
        """Start a thread to update logs from the queue."""
        def update_logs():
            while True:
                try:
                    # Check for new log entries
                    while not self.log_queue.empty():
                        log_entry, level = self.log_queue.get_nowait()
                        self._append_log(log_entry, level)
                except queue.Empty:
                    pass
                    
                # Small delay to prevent excessive CPU usage
                threading.Event().wait(0.1)
                
        # Start updater thread as daemon
        updater_thread = threading.Thread(target=update_logs, daemon=True)
        updater_thread.start()
        
    def _append_log(self, log_entry: str, level: str):
        """Append a log entry to the text widget."""
        # Enable text widget for editing
        self.log_text.configure(state="normal")
        
        # Add log entry with appropriate tag
        self.log_text.insert("end", log_entry + "\n", level)
        
        # Auto-scroll to bottom
        self.log_text.see("end")
        
        # Disable text widget again
        self.log_text.configure(state="disabled")
        
        # Limit log size (keep last 1000 lines)
        content = self.log_text.get("1.0", "end-1c")
        lines = content.split('\n')
        if len(lines) > 1000:
            # Remove oldest lines
            self.log_text.configure(state="normal")
            self.log_text.delete("1.0", f"{len(lines)-1000}.0")
            self.log_text.configure(state="disabled")
            
    def clear_logs(self):
        """Clear all log entries."""
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        
    def save_logs_to_file(self, filepath: str):
        """Save current logs to a file."""
        content = self.log_text.get("1.0", "end-1c")
        with open(filepath, 'w') as f:
            f.write(content)
```

## C. Main UI Integration

Update `src/client_activity_monitor/view/app_ui.py` to include these panels:

```python
class AppUI(ctk.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("User Activity Review")
        self.geometry("1200x800")
        
        # Create main container with grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)
        
        # Left column: Configuration and Run Analysis
        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)
        
        self.config_panel = ConfigurationPanel(left_frame, self.controller.on_config_save)
        self.config_panel.pack(fill="x", padx=10, pady=10)
        
        self.run_analysis_panel = RunAnalysisPanel(left_frame, {
            'on_run_report': self.controller.on_run_report,
            'on_generate_email': self.controller.on_generate_email,
            'on_copy_excel_path': self.controller.on_copy_excel_path,
            'on_copy_onenote': self.controller.on_copy_onenote,
            'on_optional_save': self.controller.on_optional_save
        })
        self.run_analysis_panel.pack(fill="x", padx=10, pady=10)
        
        # Right column top: Database Status
        self.database_status_panel = DatabaseStatusPanel(self)
        self.database_status_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Right column bottom: Logs
        self.log_panel = LogPanel(self)
        self.log_panel.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
```

## D. Controller Integration

Update the controller to use these panels:

```python
class MainController:
    def __init__(self):
        # ... other init ...
        
        # Initialize UI
        self.app_ui = AppUI(self)
        
        # Initialize database status panel with configurations
        databases = self.config_manager.get_all_databases()
        self.app_ui.database_status_panel.initialize_databases(databases)
        
    def update_database_status_ui(
        self,
        database_name: str,
        query_name: str,
        status: str,
        row_count: Optional[int] = None
    ):
        """Progress callback for database executor."""
        # Update database status panel
        self.app_ui.database_status_panel.update_database_status(
            database_name, query_name, status, row_count
        )
        
        # Log the status update
        if query_name == "all":
            if status == "connecting":
                self.log_info(f"Connecting to {database_name}...")
            elif status == "completed":
                self.log_success(f"Completed all queries for {database_name}")
            elif status == "failed":
                self.log_error(f"Failed to process {database_name}")
        else:
            if status == "completed" and row_count is not None:
                self.log_info(f"{database_name} - {query_name}: {row_count} rows")
            elif status == "failed":
                self.log_error(f"{database_name} - {query_name}: Failed")
                
    def log_info(self, message: str):
        """Log info message."""
        self.app_ui.log_panel.log(message, "INFO")
        logger.info(message)
        
    def log_success(self, message: str):
        """Log success message."""
        self.app_ui.log_panel.log(message, "SUCCESS")
        logger.info(message)
        
    def log_warning(self, message: str):
        """Log warning message."""
        self.app_ui.log_panel.log(message, "WARNING")
        logger.warning(message)
        
    def log_error(self, message: str):
        """Log error message."""
        self.app_ui.log_panel.log(message, "ERROR")
        logger.error(message)
```

## E. Key Features

### Database Status Panel:
1. **Dynamic initialization** based on configured databases
2. **Hierarchical display**: Database → Queries
3. **Color-coded status**: Gray (idle), Orange (connecting), Blue (running), Green (completed), Red (failed)
4. **Row counts** displayed for completed queries
5. **Overall status** summary at top

### Log Panel:
1. **Timestamped entries** with HH:MM:SS format
2. **Color-coded levels**: INFO (black), SUCCESS (green), WARNING (orange), ERROR (red), DEBUG (gray)
3. **Auto-scrolling** to show latest entries
4. **Thread-safe** log updates using queue
5. **Log rotation** (keeps last 1000 lines)
6. **Scrollable** text area for history

## F. Visual Layout

Based on the wireframe:
```
┌─────────────────────┬──────────────────────────┐
│ Configuration       │ Database Status          │
│ ─────────────       │ ───────────────          │
│ [Config fields]     │ Overall Status: Running  │
│                     │                          │
│ Run Analysis        │ client_activity_analysis │
│ ────────────        │   Status: Connected      │
│ [Analysis fields]   │   • Email: Complete (45) │
│ [Action buttons]    │   • Phone: Running...    │
│                     │   • Token: Pending       │
│                     │                          │
│                     │ account_activity_analysis│
│                     │   Status: Connecting...  │
│                     │   • Password: Pending    │
├─────────────────────┼──────────────────────────┤
│                     │ Logs:                    │
│                     │ [14:30:15] Starting...   │
│                     │ [14:30:16] Connected...  │
│                     │ [14:30:18] Query done... │
│                     │ ...                      │
└─────────────────────┴──────────────────────────┘
```

## Next Step
After implementing UI panels and status feedback, proceed to Step 10: Validation, Error Handling, and Testing.