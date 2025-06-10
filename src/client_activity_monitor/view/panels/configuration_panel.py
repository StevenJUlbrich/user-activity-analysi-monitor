"""
Configuration Panel UI Component

This module provides the configuration panel for user input of Oracle client
settings, Kerberos paths, and user SID.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Callable, Dict, Optional
from pathlib import Path
from ...common.validators import Validators


class ConfigurationPanel(ctk.CTkFrame):
    """
    Configuration panel for Oracle/Kerberos settings and user SID.
    
    Provides UI controls for entering:
    - Oracle Client Path
    - KRB5 Config Path
    - KRB5 Config Cache Path
    - User SID
    """
    
    def __init__(self, parent, save_callback: Callable):
        """
        Initialize the configuration panel.
        
        Args:
            parent: Parent widget
            save_callback: Function to call when Save Config is clicked
            Signature: save_callback(config_dict) -> (success, error_msg)
        """
        super().__init__(parent)
        self.save_callback = save_callback
        self._create_widgets()
        self._is_editing = True  # Start in edit mode
        
    def _create_widgets(self):
        """Create all UI widgets matching the wireframe."""
        # Title
        title = ctk.CTkLabel(self, text="Configuration", font=("Arial", 16, "bold"))
        title.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Oracle Client Path
        ctk.CTkLabel(self, text="Oracle Client Path:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.oracle_path_entry = ctk.CTkEntry(
            self, placeholder_text="Oracle Client", width=300
        )
        self.oracle_path_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.oracle_browse_btn = ctk.CTkButton(
            self, text="Browse", width=80,
            command=lambda: self._browse_folder(self.oracle_path_entry)
        )
        self.oracle_browse_btn.grid(row=1, column=2, padx=5, pady=5)
        
        # KRB5 Config Path
        ctk.CTkLabel(self, text="KRB5 Config Path:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.krb5_config_entry = ctk.CTkEntry(
            self, placeholder_text="KRB5 Config", width=300
        )
        self.krb5_config_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.krb5_config_browse_btn = ctk.CTkButton(
            self, text="Browse", width=80,
            command=lambda: self._browse_file(self.krb5_config_entry)
        )
        self.krb5_config_browse_btn.grid(row=2, column=2, padx=5, pady=5)
        
        # KRB5 Cache Path
        ctk.CTkLabel(self, text="KRB5 Config Cache Path:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        self.krb5_cache_entry = ctk.CTkEntry(
            self, placeholder_text="KRB5 User Cache", width=300
        )
        self.krb5_cache_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.krb5_cache_browse_btn = ctk.CTkButton(
            self, text="Browse", width=80,
            command=lambda: self._browse_file(self.krb5_cache_entry)
        )
        self.krb5_cache_browse_btn.grid(row=3, column=2, padx=5, pady=5)
        
        # User SID
        ctk.CTkLabel(self, text="User SID:").grid(
            row=4, column=0, sticky="w", padx=5, pady=5
        )
        self.sid_entry = ctk.CTkEntry(
            self, placeholder_text="SID", width=300
        )
        self.sid_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        
        # Save Config Button
        self.save_button = ctk.CTkButton(
            self, text="Save Config", command=self._on_save, width=200
        )
        self.save_button.grid(row=5, column=0, columnspan=3, pady=20)
        
        # Configure grid weights
        self.grid_columnconfigure(1, weight=1)
        
    def _browse_folder(self, entry_widget):
        """Browse for folder and update entry widget."""
        folder = filedialog.askdirectory(
            title="Select Oracle Client Directory",
            initialdir=entry_widget.get() or "/"
        )
        if folder:
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, folder)
            
    def _browse_file(self, entry_widget):
        """Browse for file and update entry widget."""
        # Determine file type based on which entry is being updated
        if entry_widget == self.krb5_config_entry:
            title = "Select KRB5 Config File"
            filetypes = [("Config files", "*.conf"), ("All files", "*.*")]
        else:
            title = "Select KRB5 Cache File"
            filetypes = [("All files", "*.*")]
            
        file = filedialog.askopenfilename(
            title=title,
            filetypes=filetypes,
            initialdir=str(Path(entry_widget.get()).parent) if entry_widget.get() else "/"
        )
        if file:
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, file)
            
    def _on_save(self):
        """Handle Save Config button click with validation."""
        if self._is_editing:
            # Get values
            oracle_path = self.oracle_path_entry.get().strip()
            krb5_config = self.krb5_config_entry.get().strip()
            krb5_cache = self.krb5_cache_entry.get().strip()
            sid = self.sid_entry.get().strip()
            
            # Validate each field
            validators = [
                (Validators.validate_oracle_client_path(oracle_path), "Oracle Client Path"),
                (Validators.validate_krb5_config(krb5_config), "KRB5 Config"),
                (Validators.validate_krb5_cache(krb5_cache), "KRB5 Cache"),
                (Validators.validate_sid(sid), "User SID")
            ]
            
            # Check all validations
            for (is_valid, error_msg), field_name in validators:
                if not is_valid:
                    self._show_error(f"{field_name}: {error_msg}")
                    return
                    
            # All valid, proceed with save
            config_data = {
                'oracle_client_path': oracle_path,
                'krb5_config_path': krb5_config,
                'krb5_cache_path': krb5_cache,
                'user_sid': sid
            }
            
            try:
                success, error_msg = self.save_callback(config_data)
                if success:
                    self._show_success("Configuration saved successfully")
                    # Switch to view mode
                    self._set_fields_enabled(False)
                    self._is_editing = False
                else:
                    self._show_error(f"Failed to save: {error_msg}")
            except Exception as e:
                self._show_error(f"Unexpected error: {str(e)}")
        else:
            # Switch to edit mode
            self._set_fields_enabled(True)
            self._is_editing = True
            
    def populate_fields(self, config_data: Dict[str, str]):
        """
        Populate fields with existing configuration.
        
        Args:
            config_data: Dictionary with configuration values
        """
        if 'oracle_client_path' in config_data:
            self.oracle_path_entry.delete(0, 'end')
            self.oracle_path_entry.insert(0, config_data['oracle_client_path'])
        if 'krb5_config_path' in config_data:
            self.krb5_config_entry.delete(0, 'end')
            self.krb5_config_entry.insert(0, config_data['krb5_config_path'])
        if 'krb5_cache_path' in config_data:
            self.krb5_cache_entry.delete(0, 'end')
            self.krb5_cache_entry.insert(0, config_data['krb5_cache_path'])
        if 'user_sid' in config_data:
            self.sid_entry.delete(0, 'end')
            self.sid_entry.insert(0, config_data['user_sid'])
            
        # Start in view mode if we have existing config
        if all(config_data.values()):
            self._set_fields_enabled(False)
            self._is_editing = False
            
    def _set_fields_enabled(self, enabled: bool):
        """Enable or disable all input fields."""
        state = "normal" if enabled else "disabled"
        self.oracle_path_entry.configure(state=state)
        self.krb5_config_entry.configure(state=state)
        self.krb5_cache_entry.configure(state=state)
        self.sid_entry.configure(state=state)
        self.oracle_browse_btn.configure(state=state)
        self.krb5_config_browse_btn.configure(state=state)
        self.krb5_cache_browse_btn.configure(state=state)
        self.save_button.configure(text="Save Config" if enabled else "Edit Config")
        
    def _show_error(self, message: str):
        """Show error message dialog."""
        messagebox.showerror("Configuration Error", message)
        
    def _show_success(self, message: str):
        """Show success message dialog."""
        messagebox.showinfo("Success", message)
        
    def get_current_config(self) -> Dict[str, str]:
        """
        Get current configuration values from UI.
        
        Returns:
            Dictionary with current configuration values
        """
        return {
            'oracle_client_path': self.oracle_path_entry.get().strip(),
            'krb5_config_path': self.krb5_config_entry.get().strip(),
            'krb5_cache_path': self.krb5_cache_entry.get().strip(),
            'user_sid': self.sid_entry.get().strip()
        }