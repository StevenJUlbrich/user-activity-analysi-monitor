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