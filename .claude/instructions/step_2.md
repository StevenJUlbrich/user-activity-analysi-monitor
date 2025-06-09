# Step 2: ConfigManager & Configuration UI Panel

## Objective
Create a ConfigManager to handle configuration files and a Configuration UI Panel that matches the wireframe design for user input of Oracle/Kerberos paths and SID.

## A. ConfigManager Implementation

Create `src/client_activity_monitor/model/config_manager.py`:

### Requirements
1. Load and manage two separate YAML configuration files:
   - `configs/app_settings.yaml` - User-editable settings
   - `configs/databases.yaml` - Database definitions (read-only)
2. Allow updating Oracle client paths and user SID through the UI
3. Validate configuration before saving
4. Use Pydantic models for data validation

### Pydantic Models

```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from pathlib import Path

# Models for app_settings.yaml
class OracleClientConfig(BaseModel):
    """Oracle client configuration - editable via UI."""
    instant_client_dir: str = Field(..., description="Oracle Client Path")
    krb5_conf: str = Field(..., description="KRB5 Config Path")
    krb5_cache: str = Field(..., description="KRB5 Config Cache Path")
    trace_level: int = 16
    trace_directory: Optional[str] = None
    
    @field_validator('instant_client_dir', 'krb5_conf')
    @classmethod
    def validate_paths_exist(cls, v):
        if not Path(v).exists():
            raise ValueError(f"Path does not exist: {v}")
        return v

class AppSettings(BaseModel):
    """Application settings."""
    report_output_dir: str = "reports"
    log_dir: str = "logs"
    log_level: str = "INFO"
    email_recipients: List[str] = Field(default_factory=list)

class UserSettings(BaseModel):
    """User settings - editable via UI."""
    sid: str = Field(..., description="User SID")

class AppSettingsConfig(BaseModel):
    """Complete app_settings.yaml structure."""
    oracle_client: OracleClientConfig
    app_settings: AppSettings
    user_settings: UserSettings

# Models for databases.yaml (read-only)
class SqlQuery(BaseModel):
    """SQL query definition."""
    name: str
    query_location: str

class DatabaseConfig(BaseModel):
    """Individual database configuration."""
    name: str
    host: str
    port: int = 1521
    service_name: str
    default_schema: str
    sql_queries: List[SqlQuery]

class DatabasesConfig(BaseModel):
    """Complete databases.yaml structure."""
    databases: List[DatabaseConfig]
```

### ConfigManager Methods

```python
class ConfigManager:
    def __init__(self, 
                 app_settings_path: str = "configs/app_settings.yaml",
                 databases_path: str = "configs/databases.yaml"):
        """Initialize with configuration file paths."""
        
    def load_configs(self) -> bool:
        """Load both configuration files. Returns True if successful."""
        
    def get_oracle_client_config(self) -> OracleClientConfig:
        """Return current Oracle client configuration."""
        
    def get_user_sid(self) -> str:
        """Return the user's SID."""
        
    def update_config_from_ui(self,
                             oracle_client_path: str,
                             krb5_config_path: str,
                             krb5_cache_path: str,
                             user_sid: str) -> bool:
        """
        Update configuration with values from UI and save.
        Returns True if saved successfully.
        """
        
    def validate_and_save(self) -> tuple[bool, Optional[str]]:
        """
        Validate current configuration and save if valid.
        Returns (success, error_message).
        """
        
    def get_all_databases(self) -> List[DatabaseConfig]:
        """Return all database configurations."""
        
    def get_connection_params(self, database_name: str) -> Dict[str, Any]:
        """Get connection parameters for ez_connect_oracle.py."""
```

## B. Configuration UI Panel

Create `src/client_activity_monitor/view/panels/configuration_panel.py`:

### Requirements (Based on Wireframe)
1. Entry fields for:
   - Oracle Client Path
   - KRB5 Config Path
   - KRB5 Config Cache Path
   - User SID
2. "Save Config" button
3. Pre-populate fields if configuration already exists
4. Show validation errors
5. Disable/enable Save button based on validation

### UI Implementation

```python
import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Dict

class ConfigurationPanel(ctk.CTkFrame):
    def __init__(self, parent, save_callback: Callable):
        """
        Args:
            parent: Parent widget
            save_callback: Function to call when Save Config is clicked
                         Signature: save_callback(config_dict) -> (success, error_msg)
        """
        super().__init__(parent)
        self.save_callback = save_callback
        self._create_widgets()
        
    def _create_widgets(self):
        """Create all UI widgets matching the wireframe."""
        # Title
        title = ctk.CTkLabel(self, text="Configuration", font=("Arial", 16, "bold"))
        title.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Oracle Client Path
        ctk.CTkLabel(self, text="Oracle Client Path").grid(row=1, column=0, sticky="w", padx=5)
        self.oracle_path_entry = ctk.CTkEntry(self, placeholder_text="Oracle Client")
        self.oracle_path_entry.grid(row=1, column=1, padx=5, sticky="ew")
        self.oracle_browse_btn = ctk.CTkButton(self, text="...", width=30,
                                              command=lambda: self._browse_folder(self.oracle_path_entry))
        self.oracle_browse_btn.grid(row=1, column=2, padx=5)
        
        # KRB5 Config Path
        ctk.CTkLabel(self, text="KRB5 Config Path").grid(row=2, column=0, sticky="w", padx=5)
        self.krb5_config_entry = ctk.CTkEntry(self, placeholder_text="KRB5 Config")
        self.krb5_config_entry.grid(row=2, column=1, padx=5, sticky="ew")
        self.krb5_config_browse_btn = ctk.CTkButton(self, text="...", width=30,
                                                    command=lambda: self._browse_file(self.krb5_config_entry))
        self.krb5_config_browse_btn.grid(row=2, column=2, padx=5)
        
        # KRB5 Cache Path
        ctk.CTkLabel(self, text="KRB5 Config Cache Path").grid(row=3, column=0, sticky="w", padx=5)
        self.krb5_cache_entry = ctk.CTkEntry(self, placeholder_text="KRB5 User Cache")
        self.krb5_cache_entry.grid(row=3, column=1, padx=5, sticky="ew")
        self.krb5_cache_browse_btn = ctk.CTkButton(self, text="...", width=30,
                                                   command=lambda: self._browse_file(self.krb5_cache_entry))
        self.krb5_cache_browse_btn.grid(row=3, column=2, padx=5)
        
        # User SID
        ctk.CTkLabel(self, text="User SID:").grid(row=4, column=0, sticky="w", padx=5)
        self.sid_entry = ctk.CTkEntry(self, placeholder_text="SID")
        self.sid_entry.grid(row=4, column=1, padx=5, sticky="ew")
        
        # Save Config Button
        self.save_button = ctk.CTkButton(self, text="Save Config", command=self._on_save)
        self.save_button.grid(row=5, column=0, columnspan=3, pady=20)
        
        # Configure grid weights
        self.grid_columnconfigure(1, weight=1)
        
    def _browse_folder(self, entry_widget):
        """Browse for folder and update entry widget."""
        folder = filedialog.askdirectory()
        if folder:
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, folder)
            
    def _browse_file(self, entry_widget):
        """Browse for file and update entry widget."""
        file = filedialog.askopenfilename()
        if file:
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, file)
            
    def _on_save(self):
        """Handle Save Config button click."""
        config_data = {
            'oracle_client_path': self.oracle_path_entry.get().strip(),
            'krb5_config_path': self.krb5_config_entry.get().strip(),
            'krb5_cache_path': self.krb5_cache_entry.get().strip(),
            'user_sid': self.sid_entry.get().strip()
        }
        
        # Basic validation
        if not all(config_data.values()):
            self._show_error("All fields are required")
            return
            
        # Call the save callback
        success, error_msg = self.save_callback(config_data)
        
        if success:
            self._show_success("Configuration saved successfully")
            # Optionally disable fields after successful save
            self._set_fields_enabled(False)
        else:
            self._show_error(f"Failed to save: {error_msg}")
            
    def populate_fields(self, config_data: Dict[str, str]):
        """Populate fields with existing configuration."""
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
        self.save_button.configure(text="Edit Config" if not enabled else "Save Config")
        
    def _show_error(self, message: str):
        """Show error message (implement based on your UI framework)."""
        # Could use CTkMessagebox or status label
        print(f"Error: {message}")
        
    def _show_success(self, message: str):
        """Show success message."""
        print(f"Success: {message}")
```

## C. Controller Integration

The controller should:
1. Initialize ConfigManager on startup
2. Load existing configuration and populate UI fields
3. Handle save requests from the Configuration Panel
4. Update ConfigManager with new values

Example controller method:
```python
def on_config_save(self, config_data: Dict[str, str]) -> tuple[bool, Optional[str]]:
    """Handle configuration save from UI."""
    try:
        success = self.config_manager.update_config_from_ui(
            oracle_client_path=config_data['oracle_client_path'],
            krb5_config_path=config_data['krb5_config_path'],
            krb5_cache_path=config_data['krb5_cache_path'],
            user_sid=config_data['user_sid']
        )
        if success:
            self.logger.info(f"Configuration saved by user {config_data['user_sid']}")
            return True, None
        else:
            return False, "Failed to save configuration"
    except Exception as e:
        return False, str(e)
```

## D. Key Implementation Notes

1. **UI matches wireframe**: Four entry fields with Save Config button
2. **Browse buttons**: Optional file/folder browsers for path fields
3. **Validation**: Ensure all paths exist before saving
4. **Pre-population**: Load existing config on startup
5. **State management**: Consider disabling fields after successful save
6. **databases.yaml**: Not editable through UI (admin-managed)

## Next Step
After implementing ConfigManager and Configuration Panel, proceed to Step 3: Run Analysis Panel with Last Time Event Reported field and KINIT checkbox.