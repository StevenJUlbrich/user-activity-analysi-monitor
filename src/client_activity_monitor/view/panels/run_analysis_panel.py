"""
Run Analysis Panel UI Component

This module provides the Run Analysis panel with KINIT checkbox,
Run Report button, and report action buttons.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from typing import Callable, Dict


class RunAnalysisPanel(ctk.CTkFrame):
    """
    Run Analysis panel for executing database queries and managing reports.
    
    Provides controls for:
    - Last Time Event Reported datetime entry
    - KINIT confirmation checkbox
    - Run Report button
    - Report action buttons (Email, Excel Path, OneNote, Save)
    """
    
    def __init__(self, parent, callbacks: Dict[str, Callable]):
        """
        Initialize the Run Analysis panel.
        
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
        ctk.CTkLabel(self, text="Last Time Event Reported:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.datetime_entry = ctk.CTkEntry(
            self, placeholder_text="YYYY-MM-DD HH:MM", width=200
        )
        self.datetime_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # KINIT Checkbox
        self.kinit_var = ctk.BooleanVar()
        self.kinit_checkbox = ctk.CTkCheckBox(
            self, 
            text="KINIT Executed?",
            variable=self.kinit_var,
            command=self._on_kinit_toggle,
            checkbox_width=24,
            checkbox_height=24
        )
        self.kinit_checkbox.grid(row=2, column=0, columnspan=2, pady=15)
        
        # Run Report Button
        self.run_report_button = ctk.CTkButton(
            self, 
            text="Run Report",
            command=self._on_run_report,
            state="disabled",
            width=200,
            height=35
        )
        self.run_report_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Separator
        separator = ctk.CTkFrame(self, height=2, fg_color=("gray70", "gray30"))
        separator.grid(row=4, column=0, columnspan=2, sticky="ew", pady=15, padx=20)
        
        # Report Action Buttons
        self.email_button = ctk.CTkButton(
            self,
            text="Generate Email Report",
            command=lambda: self.callbacks.get('on_generate_email', lambda: None)(),
            state="disabled",
            width=250
        )
        self.email_button.grid(row=5, column=0, columnspan=2, pady=5)
        
        self.copy_excel_button = ctk.CTkButton(
            self,
            text="Copy Excel Path to Clipboard",
            command=lambda: self.callbacks.get('on_copy_excel_path', lambda: None)(),
            state="disabled",
            width=250
        )
        self.copy_excel_button.grid(row=6, column=0, columnspan=2, pady=5)
        
        self.onenote_button = ctk.CTkButton(
            self,
            text="OneNote Entry to Clipboard",
            command=lambda: self.callbacks.get('on_copy_onenote', lambda: None)(),
            state="disabled",
            width=250
        )
        self.onenote_button.grid(row=7, column=0, columnspan=2, pady=5)
        
        self.optional_save_button = ctk.CTkButton(
            self,
            text="Optional Save Report",
            command=lambda: self.callbacks.get('on_optional_save', lambda: None)(),
            state="disabled",
            width=250
        )
        self.optional_save_button.grid(row=8, column=0, columnspan=2, pady=5)
        
        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
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
        if 'on_run_report' in self.callbacks:
            self.callbacks['on_run_report'](last_event_time)
        
    def set_running_state(self, is_running: bool):
        """
        Update UI state when report is running or finished.
        
        Args:
            is_running: True if analysis is running, False if complete
        """
        if is_running:
            self.run_report_button.configure(state="disabled", text="Running...")
            self.kinit_checkbox.configure(state="disabled")
            self.datetime_entry.configure(state="disabled")
        else:
            self.run_report_button.configure(
                state="normal" if self.kinit_var.get() else "disabled",
                text="Run Report"
            )
            self.kinit_checkbox.configure(state="normal")
            self.datetime_entry.configure(state="normal")
            
    def enable_report_actions(self, enable: bool):
        """
        Enable or disable all report action buttons.
        
        Args:
            enable: True to enable buttons, False to disable
        """
        state = "normal" if enable else "disabled"
        self.email_button.configure(state=state)
        self.copy_excel_button.configure(state=state)
        self.onenote_button.configure(state=state)
        self.optional_save_button.configure(state=state)
        
    def get_last_event_time(self) -> str:
        """
        Get the last event time from the entry field.
        
        Returns:
            Last event time as string in format "YYYY-MM-DD HH:MM"
        """
        return self.datetime_entry.get().strip()
        
    def update_last_event_time(self, timestamp: str):
        """
        Update the last event time field (for successful runs).
        
        Args:
            timestamp: New timestamp in format "YYYY-MM-DD HH:MM"
        """
        self.datetime_entry.delete(0, 'end')
        self.datetime_entry.insert(0, timestamp)
        
    def _show_error(self, message: str):
        """Show error message dialog."""
        messagebox.showerror("Run Analysis Error", message)
        
    def _show_info(self, message: str):
        """Show info message dialog."""
        messagebox.showinfo("Run Analysis", message)