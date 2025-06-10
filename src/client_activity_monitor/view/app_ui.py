import customtkinter as ctk
from .panels.configuration_panel import ConfigurationPanel
from .panels.run_analysis_panel import RunAnalysisPanel
from .panels.database_status_panel import DatabaseStatusPanel
from .panels.log_panel import LogPanel

class AppUI(ctk.CTk):
    """
    Main application UI window that contains all panels.
    """
    
    def __init__(self, controller):
        """
        Initialize the main application window.
        
        Args:
            controller: Reference to the MainController
        """
        super().__init__()
        self.controller = controller
        self.title("User Activity Review")
        self.geometry("1200x800")

        # Set default theme
        ctk.set_appearance_mode("light")  # Options: "light", "dark", "system"

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
        
        # Store reference in controller
        self.controller.run_analysis_panel = self.run_analysis_panel
        
        # Right column top: Database Status
        self.database_status_panel = DatabaseStatusPanel(self)
        self.database_status_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Right column bottom: Logs
        self.log_panel = LogPanel(self)
        self.log_panel.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        
    def show_message(self, title: str, message: str):
        """Show an info message dialog."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x200")
        
        # Center the dialog
        dialog.transient(self)
        dialog.grab_set()
        
        # Message
        msg_label = ctk.CTkLabel(dialog, text=message, wraplength=350)
        msg_label.pack(pady=20, padx=20)
        
        # OK button
        ok_button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy)
        ok_button.pack(pady=10)
        
        # Center on parent window
        self.wait_visibility(dialog)
        x = self.winfo_x() + (self.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
    def show_error(self, title: str, message: str):
        """Show an error message dialog."""
        self.show_message(f"Error: {title}", message)
        
    def show_warning(self, title: str, message: str):
        """Show a warning message dialog."""
        self.show_message(f"Warning: {title}", message)