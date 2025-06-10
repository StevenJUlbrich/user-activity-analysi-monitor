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