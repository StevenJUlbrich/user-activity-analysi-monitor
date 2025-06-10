"""
Configuration Manager for Client Activity Monitor

This module handles loading, validating, and managing configuration files
for the application using Pydantic models for type safety and validation.
"""

import yaml
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from loguru import logger


# Models for app_settings.yaml
class OracleClientConfig(BaseModel):
    """Oracle client configuration - editable via UI."""
    instant_client_dir: str = Field(..., description="Oracle Client Path")
    krb5_conf: str = Field(..., description="KRB5 Config Path")
    krb5_cache: str = Field(..., description="KRB5 Config Cache Path")
    trace_level: int = 0
    trace_directory: Optional[str] = None
    
    @field_validator('instant_client_dir', 'krb5_conf')
    @classmethod
    def validate_paths_exist(cls, v):
        """Validate that required paths exist."""
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


class ConfigManager:
    """
    Manages application configuration files.
    
    Handles loading, validation, and updates of configuration settings
    from app_settings.yaml and databases.yaml.
    """
    
    def __init__(self, 
                 app_settings_path: str = "configs/app_settings.yaml",
                 databases_path: str = "configs/databases.yaml"):
        """
        Initialize with configuration file paths.
        
        Args:
            app_settings_path: Path to app_settings.yaml
            databases_path: Path to databases.yaml
        """
        self.app_settings_path = Path(app_settings_path)
        self.databases_path = Path(databases_path)
        self.app_settings_config: Optional[AppSettingsConfig] = None
        self.databases_config: Optional[DatabasesConfig] = None
        
    def load_configs(self) -> bool:
        """
        Load both configuration files.
        
        Returns:
            True if both configs loaded successfully, False otherwise
        """
        try:
            # Load app settings
            if self.app_settings_path.exists():
                with open(self.app_settings_path, 'r') as f:
                    app_settings_data = yaml.safe_load(f)
                self.app_settings_config = AppSettingsConfig(**app_settings_data)
                logger.info("App settings loaded successfully")
            else:
                logger.error(f"App settings file not found: {self.app_settings_path}")
                return False
                
            # Load databases config
            if self.databases_path.exists():
                with open(self.databases_path, 'r') as f:
                    databases_data = yaml.safe_load(f)
                self.databases_config = DatabasesConfig(**databases_data)
                logger.info("Databases config loaded successfully")
            else:
                logger.error(f"Databases config file not found: {self.databases_path}")
                return False
                
            return True
            
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error loading configs: {e}")
            return False
            
    def get_oracle_client_config(self) -> Optional[OracleClientConfig]:
        """
        Return current Oracle client configuration.
        
        Returns:
            OracleClientConfig object or None if not loaded
        """
        if self.app_settings_config:
            return self.app_settings_config.oracle_client
        return None
        
    def get_user_sid(self) -> Optional[str]:
        """
        Return the user's SID.
        
        Returns:
            User SID or None if not loaded
        """
        if self.app_settings_config:
            return self.app_settings_config.user_settings.sid
        return None
        
    def get_app_settings(self) -> Optional[Dict[str, Any]]:
        """
        Return application settings as dictionary.
        
        Returns:
            App settings dict or None if not loaded
        """
        if self.app_settings_config:
            return self.app_settings_config.app_settings.model_dump()
        return None
        
    def update_config_from_ui(self,
                             oracle_client_path: str,
                             krb5_config_path: str,
                             krb5_cache_path: str,
                             user_sid: str) -> bool:
        """
        Update configuration with values from UI and save.
        
        Args:
            oracle_client_path: Path to Oracle Instant Client
            krb5_config_path: Path to krb5.conf
            krb5_cache_path: Path to Kerberos cache
            user_sid: User's SID
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Update Oracle client config
            if self.app_settings_config:
                self.app_settings_config.oracle_client.instant_client_dir = oracle_client_path
                self.app_settings_config.oracle_client.krb5_conf = krb5_config_path
                self.app_settings_config.oracle_client.krb5_cache = krb5_cache_path
                self.app_settings_config.user_settings.sid = user_sid
                
                # Validate the updated config
                self.app_settings_config.oracle_client.model_validate(
                    self.app_settings_config.oracle_client.model_dump()
                )
                
                # Save to file
                return self._save_app_settings()
            else:
                logger.error("App settings not loaded")
                return False
                
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            return False
            
    def _save_app_settings(self) -> bool:
        """
        Save app settings to YAML file.
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            if self.app_settings_config:
                # Convert to dict for YAML serialization
                config_dict = self.app_settings_config.model_dump()
                
                # Write to file
                with open(self.app_settings_path, 'w') as f:
                    yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
                    
                logger.info("App settings saved successfully")
                return True
            else:
                logger.error("No app settings to save")
                return False
                
        except Exception as e:
            logger.error(f"Error saving app settings: {e}")
            return False
            
    def validate_and_save(self) -> tuple[bool, Optional[str]]:
        """
        Validate current configuration and save if valid.
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            if self.app_settings_config:
                # Validate the entire config
                self.app_settings_config.model_validate(
                    self.app_settings_config.model_dump()
                )
                
                # Save if valid
                if self._save_app_settings():
                    return True, None
                else:
                    return False, "Failed to save configuration"
            else:
                return False, "Configuration not loaded"
                
        except Exception as e:
            return False, str(e)
            
    def get_all_databases(self) -> List[DatabaseConfig]:
        """
        Return all database configurations.
        
        Returns:
            List of DatabaseConfig objects
        """
        if self.databases_config:
            return self.databases_config.databases
        return []
        
    def get_connection_params(self, database_name: str) -> Optional[Dict[str, Any]]:
        """
        Get connection parameters for ez_connect_oracle.py.
        
        Args:
            database_name: Name of the database
            
        Returns:
            Dictionary with connection parameters or None if not found
        """
        if not self.databases_config or not self.app_settings_config:
            logger.error("Configs not loaded")
            return None
            
        # Find the database
        for db in self.databases_config.databases:
            if db.name == database_name:
                # Build connection params
                oracle_client_dict = self.app_settings_config.oracle_client.model_dump()
                
                return {
                    'host': db.host,
                    'port': db.port,
                    'service_name': db.service_name,
                    'default_schema': db.default_schema,
                    'oracle_client': oracle_client_dict
                }
                
        logger.error(f"Database not found: {database_name}")
        return None
        
    def config_exists(self) -> bool:
        """
        Check if configuration files exist.
        
        Returns:
            True if both config files exist
        """
        return self.app_settings_path.exists() and self.databases_path.exists()