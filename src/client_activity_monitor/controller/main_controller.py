"""
Client Activity Monitor - Main Controller

This module serves as the central orchestrator for the Client Activity Monitor
application. It coordinates between the UI (View) and business logic (Model)
following the MVC pattern.

Key Responsibilities:
- Initialize and manage all application components
- Handle UI events and delegate to appropriate services  
- Manage threading for non-blocking operations
- Coordinate error handling and user feedback

Author: SOC Development Team
Created: 2024
Modified: 2024
"""

import threading
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from pathlib import Path
from loguru import logger
from ..model.config_manager import ConfigManager
from ..model.services.database_executor import DatabaseExecutor
from ..model.services.merge_filter_service import MergeFilterService
from ..model.services.report_generator import ReportGenerator
from ..common.clipboard_utils import copy_file_path
from ..model.integrations.email_service import EmailService
from ..model.integrations.onenote_service import OneNoteService
from ..view.app_ui import AppUI
from ..common.validators import Validators
from ..common.exceptions import ConfigurationError, DatabaseConnectionError
from ..common.error_handler import handle_errors, get_user_friendly_error


class MainController:
    """
    Central controller for the Client Activity Monitor application.
    
    This class orchestrates all application operations, managing the flow
    between user interface events and business logic execution. It ensures
    UI responsiveness through proper threading and provides comprehensive
    error handling.
    
    Attributes:
        config_manager: Handles application configuration
        app_ui: Main application window
        report_generator: Creates Excel/CSV reports
        last_report_path: Path to most recent report
        last_report_data: DataFrame of most recent results
        
    Example:
        >>> controller = MainController()
        >>> controller.run()  # Starts the application
    """
    
    def __init__(self):
        """Initialize the main controller."""
        # Initialize config manager
        self.config_manager = ConfigManager()
        
        # Load configurations
        if not self.config_manager.load_configs():
            logger.warning("Failed to load configurations on startup")
            
        # Initialize other components (to be added in future steps)
        self.app_ui = None
        self.database_executor = None
        self.report_generator = None
        self.merge_filter_service = None
        
        # Report tracking
        self.last_report_path: Optional[Path] = None
        self.last_report_data = None
        
        # Analysis state
        self.analysis_thread: Optional[threading.Thread] = None
        self.cancel_event = threading.Event()
        
        # UI components (to be set when UI is created)
        self.run_analysis_panel = None
        
    def run(self):
        """
        Run the application.
        """
        logger.info("Starting Client Activity Monitor...")
        
        # Initialize UI
        self.app_ui = AppUI(self)
        
        # Initialize database status panel with configurations
        databases = self.config_manager.get_all_databases()
        self.app_ui.database_status_panel.initialize_databases(databases)
        
        # Populate configuration panel with current values
        current_config = self.get_current_config()
        self.app_ui.config_panel.populate_fields(current_config)
        
        # Initial log message
        self.log_info("Client Activity Monitor started")
        self.log_info(f"Loaded {len(databases)} database configurations")
        
        # Start the UI main loop
        self.app_ui.mainloop()
        
    def on_config_save(self, config_data: Dict[str, str]) -> Tuple[bool, Optional[str]]:
        """
        Handle configuration save from UI.
        
        Args:
            config_data: Dictionary with configuration values from UI
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            success = self.config_manager.update_config_from_ui(
                oracle_client_path=config_data['oracle_client_path'],
                krb5_config_path=config_data['krb5_config_path'],
                krb5_cache_path=config_data['krb5_cache_path'],
                user_sid=config_data['user_sid']
            )
            
            if success:
                logger.info(f"Configuration saved by user {config_data['user_sid']}")
                return True, None
            else:
                return False, "Failed to save configuration"
                
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False, str(e)
            
    def get_current_config(self) -> Dict[str, str]:
        """
        Get current configuration for populating UI.
        
        Returns:
            Dictionary with current configuration values
        """
        config_dict = {}
        
        oracle_config = self.config_manager.get_oracle_client_config()
        if oracle_config:
            config_dict['oracle_client_path'] = oracle_config.instant_client_dir
            config_dict['krb5_config_path'] = oracle_config.krb5_conf
            config_dict['krb5_cache_path'] = oracle_config.krb5_cache
            
        user_sid = self.config_manager.get_user_sid()
        if user_sid:
            config_dict['user_sid'] = user_sid
            
        return config_dict
        
    def _validate_oracle_configuration(self) -> Tuple[bool, Optional[str]]:
        """
        Validate Oracle client configuration before attempting connections.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        oracle_config = self.config_manager.get_oracle_client_config()
        if not oracle_config:
            return False, "Oracle client configuration not found. Please configure Oracle paths."
            
        # Check if paths exist
        from pathlib import Path
        instant_client_path = Path(oracle_config.instant_client_dir)
        if not instant_client_path.exists():
            return False, f"Oracle Instant Client directory not found: {oracle_config.instant_client_dir}"
            
        krb5_conf_path = Path(oracle_config.krb5_conf)
        if not krb5_conf_path.exists():
            return False, f"Kerberos configuration file not found: {oracle_config.krb5_conf}"
            
        # Check if user has a valid Kerberos ticket
        import subprocess
        try:
            result = subprocess.run(['klist'], capture_output=True, text=True)
            if result.returncode != 0 or "No credentials cache found" in result.stderr:
                return False, "No valid Kerberos ticket found. Please run 'kinit' to obtain a ticket."
        except FileNotFoundError:
            logger.warning("klist command not found - unable to verify Kerberos ticket")
            
        return True, None
    
    @handle_errors(log_errors=True)
    def on_run_report(self, last_event_time_str: str):
        """
        Handle Run Report button click with comprehensive error handling.
        
        Args:
            last_event_time_str: Last event time as string "YYYY-MM-DD HH:MM"
        """
        try:
            # Validate inputs
            is_valid, error_msg = Validators.validate_datetime(last_event_time_str)
            if not is_valid:
                self.show_error("Invalid Input", error_msg)
                return
                
            # Validate Oracle configuration
            is_valid, error_msg = self._validate_oracle_configuration()
            if not is_valid:
                self.show_error("Configuration Error", error_msg)
                return
                
            # Check configuration
            if not self.config_manager.get_all_databases():
                raise ConfigurationError("No databases configured. Please check your configuration.")
                
            # Parse the last event time
            last_event_time = datetime.strptime(last_event_time_str, "%Y-%m-%d %H:%M")
            
            # Calculate start_date (30 days ago)
            start_date = datetime.now() - timedelta(days=30)
            
            # Log the analysis start
            user_sid = self.config_manager.get_user_sid()
            logger.info(f"Analysis started by {user_sid} at {datetime.now()}")
            logger.info(f"Last event time: {last_event_time}")
            logger.info(f"Query start date: {start_date}")
            
            # Clear cancel event
            self.cancel_event.clear()
            
            # Start analysis in separate thread
            self.analysis_thread = threading.Thread(
                target=self._run_analysis_thread,
                args=(start_date, last_event_time),
                daemon=True
            )
            self.analysis_thread.start()
            
        except ConfigurationError as e:
            self.log_error(f"Configuration Error: {e}")
            self.show_error("Configuration Error", str(e))
            if self.run_analysis_panel:
                self.run_analysis_panel.set_running_state(False)
        except Exception as e:
            self.log_error(f"Unexpected error: {e}")
            self.show_error("Error", "An unexpected error occurred. Check logs for details.")
            if self.run_analysis_panel:
                self.run_analysis_panel.set_running_state(False)
            
    def _run_analysis_thread(self, start_date: datetime, last_event_time: datetime):
        """
        Run the analysis in a separate thread.
        
        Args:
            start_date: Start date for queries (30 days ago)
            last_event_time: Last event time for filtering
        """
        try:
            # Execute queries on all databases
            self.database_executor = DatabaseExecutor(self.config_manager)
            
            try:
                results = self.database_executor.execute_all_databases(
                    start_date=start_date,
                    progress_callback=self.update_database_status_ui,
                    cancel_event=self.cancel_event
                )
            except DatabaseConnectionError as e:
                # Database connection failed - stop all processing
                logger.error(f"Database connection error: {e}")
                self.show_error(
                    "Database Connection Failed",
                    f"{str(e)}\n\nAnalysis has been stopped. Please check your database " +
                    "configurations and ensure all databases are accessible."
                )
                return
            
            # Log summary
            for db_name, queries in results.items():
                logger.info(f"Database {db_name} returned {len(queries)} query results")
                for query_name, df in queries.items():
                    logger.info(f"  - {query_name}: {len(df)} rows")
            
            # Merge and filter results
            merge_filter_service = MergeFilterService()
            filtered_data = merge_filter_service.process_results(
                database_results=results,
                last_event_time=last_event_time
            )
            
            if not filtered_data.empty:
                self.report_data = filtered_data
                logger.info(f"Found {len(filtered_data)} users meeting all criteria")
                
                # Generate report
                user_sid = self.config_manager.get_user_settings().get('sid', 'Unknown')
                report_output_dir = self.config_manager.get_app_settings().get('report_output_dir', 'reports')
                
                self.report_generator = ReportGenerator(report_output_dir)
                self.last_report_path = self.report_generator.create_excel_report(
                    data=filtered_data,
                    user_sid=user_sid,
                    last_event_time=last_event_time,
                    additional_info={
                        'Database Count': len(self.config_manager.get_all_databases()),
                        'Analysis Start Time': start_date.strftime('%Y-%m-%d %H:%M:%S')
                    }
                )
                self.last_report_data = filtered_data
                
                # Enable report actions
                if self.run_analysis_panel:
                    self.run_analysis_panel.enable_report_actions(True)
                
                # Update last event time to now
                new_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                if self.run_analysis_panel:
                    self.run_analysis_panel.update_last_event_time(new_time)
                
                logger.info(f"Report generated: {self.last_report_path}")
                
                # Show success message
                self.show_message(
                    "Report Generated",
                    f"Found {len(filtered_data)} users meeting criteria.\n"
                    f"Report saved to: {self.last_report_path.name}"
                )
            else:
                logger.info("No users met all criteria within the 24-hour window")
                self.report_data = None
                self.last_report_data = None
                self.show_message(
                    "No Results",
                    "No users found meeting all criteria within 24-hour window."
                )
            
        except DatabaseConnectionError as e:
            # This should already be handled above, but just in case
            logger.error(f"Database connection error in thread: {e}")
            self.show_error("Database Connection Failed", str(e))
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            # Check if it's a wrapped database connection error
            if "database" in str(e).lower() and "connect" in str(e).lower():
                self.show_error(
                    "Database Connection Failed",
                    f"{str(e)}\n\nPlease verify your database credentials and network connectivity."
                )
            else:
                self.show_error("Analysis Failed", str(e))
        finally:
            if self.run_analysis_panel:
                self.run_analysis_panel.set_running_state(False)
            
    def on_generate_email(self):
        """Handle Generate Email Report button."""
        if self.last_report_data is not None and not self.last_report_data.empty and self.last_report_path:
            try:
                # Get email recipients from config
                email_recipients = self.config_manager.get_app_settings().get('email_recipients', [])
                
                if not email_recipients:
                    logger.warning("No email recipients configured")
                    self.show_warning(
                        "No Recipients",
                        "No email recipients configured.\n"
                        "Please add recipients in the configuration."
                    )
                    return
                    
                # Get other required data
                user_sid = self.config_manager.get_user_settings().get('sid', 'Unknown')
                
                # Get last event time from UI or use current time
                if self.run_analysis_panel:
                    last_event_time_str = self.run_analysis_panel.get_last_event_time()
                    last_event_time = datetime.strptime(last_event_time_str, "%Y-%m-%d %H:%M")
                else:
                    last_event_time = datetime.now()
                
                # First copy the report path to clipboard
                copy_file_path(self.last_report_path)
                
                # Create email draft
                email_service = EmailService()
                success = email_service.create_email_draft(
                    recipients=email_recipients,
                    report_data=self.last_report_data,
                    report_path=self.last_report_path,
                    user_sid=user_sid,
                    last_event_time=last_event_time
                )
                
                if success:
                    logger.info("Email draft created successfully")
                    self.show_message(
                        "Email Draft Created",
                        "Email draft opened in your default email client.\n\n"
                        "IMPORTANT: Please manually attach the report file.\n"
                        "The file path has been copied to your clipboard."
                    )
                else:
                    logger.error("Failed to create email draft")
                    self.show_error(
                        "Email Failed",
                        "Failed to create email draft.\n"
                        "Please check your default email client settings."
                    )
                    
            except Exception as e:
                logger.error(f"Email generation failed: {e}")
                self.show_error("Email Error", str(e))
        else:
            logger.warning("No report available for email")
            self.show_warning("No Report", "No report available to email")
            
    def on_copy_excel_path(self):
        """Handle Copy Excel Path to Clipboard button."""
        if self.last_report_path and self.last_report_path.exists():
            success = copy_file_path(self.last_report_path)
            if success:
                logger.info(f"Report path copied to clipboard: {self.last_report_path}")
                self.show_message(
                    "Path Copied",
                    f"Report path copied to clipboard:\n{self.last_report_path}"
                )
            else:
                logger.error("Failed to copy path to clipboard")
                self.show_error("Copy Failed", "Failed to copy path to clipboard")
        else:
            logger.warning("No report path to copy")
            self.show_warning("No Report", "No report available to copy")
            
    def on_copy_onenote(self):
        """Handle OneNote Entry to Clipboard button."""
        if self.last_report_data is not None and self.last_report_path:
            try:
                # Get required data
                user_sid = self.config_manager.get_user_settings().get('sid', 'Unknown')
                report_run_time = datetime.now()
                
                # Get last event time from UI or use current time
                if self.run_analysis_panel:
                    last_event_time_str = self.run_analysis_panel.get_last_event_time()
                    last_event_time = datetime.strptime(last_event_time_str, "%Y-%m-%d %H:%M")
                else:
                    last_event_time = datetime.now()
                    
                user_count = len(self.last_report_data)
                
                # Create OneNote service
                onenote_service = OneNoteService()
                
                # Copy summary to clipboard
                success = onenote_service.copy_summary_to_clipboard(
                    user_sid=user_sid,
                    report_run_time=report_run_time,
                    last_event_time=last_event_time,
                    user_count=user_count
                )
                
                if success:
                    logger.info(
                        f"OneNote summary copied - SID: {user_sid}, "
                        f"Run Time: {report_run_time.strftime('%Y-%m-%d %H:%M:%S')}, "
                        f"Last Event: {last_event_time.strftime('%Y-%m-%d %H:%M:%S')}, "
                        f"Users: {user_count}"
                    )
                    self.show_message(
                        "OneNote Summary Copied",
                        "Summary copied to clipboard:\n\n"
                        f"SID: {user_sid}\n"
                        f"Run Time: {report_run_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"Last Event: {last_event_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"Users Found: {user_count}\n\n"
                        "Paste into OneNote with Ctrl+V"
                    )
                else:
                    logger.error("Failed to copy OneNote summary to clipboard")
                    self.show_error(
                        "Copy Failed",
                        "Failed to copy summary to clipboard"
                    )
                    
            except Exception as e:
                logger.error(f"OneNote summary failed: {e}")
                self.show_error("OneNote Error", str(e))
        else:
            logger.warning("No report data for OneNote")
            self.show_warning("No Report", "No report available for OneNote summary")
            
    def on_optional_save(self):
        """Handle Optional Save Report button (CSV export)."""
        if self.last_report_data is not None and not self.last_report_data.empty:
            try:
                # Get current settings
                user_sid = self.config_manager.get_user_settings().get('sid', 'Unknown')
                
                # Get last event time from UI or use current time
                if self.run_analysis_panel:
                    last_event_time_str = self.run_analysis_panel.get_last_event_time()
                    last_event_time = datetime.strptime(last_event_time_str, "%Y-%m-%d %H:%M")
                else:
                    last_event_time = datetime.now()
                
                # Create CSV report
                csv_path = self.report_generator.create_csv_report(
                    data=self.last_report_data,
                    user_sid=user_sid,
                    last_event_time=last_event_time
                )
                
                logger.info(f"CSV report saved to: {csv_path}")
                self.show_message(
                    "CSV Saved",
                    f"CSV report saved to:\n{csv_path.name}"
                )
            except Exception as e:
                logger.error(f"CSV export failed: {e}")
                self.show_error("Export Failed", str(e))
        else:
            logger.warning("No report data to save")
            self.show_warning("No Data", "No report data available to save")
            
    def update_database_status_ui(self, database_name: str, query_name: str, 
                                  status: str, row_count: Optional[int] = None):
        """
        Progress callback for database executor with UI updates.
        
        Args:
            database_name: Name of the database
            query_name: Name of the query or "all" for database-level status
            status: Status string ("connecting", "running", "completed", "failed", "cancelled")
            row_count: Optional row count for completed queries
        """
        # Update database status panel
        if self.app_ui and hasattr(self.app_ui, 'database_status_panel'):
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
        if self.app_ui and hasattr(self.app_ui, 'log_panel'):
            self.app_ui.log_panel.log(message, "INFO")
        logger.info(message)
        
    def log_success(self, message: str):
        """Log success message."""
        if self.app_ui and hasattr(self.app_ui, 'log_panel'):
            self.app_ui.log_panel.log(message, "SUCCESS")
        logger.info(message)
        
    def log_warning(self, message: str):
        """Log warning message."""
        if self.app_ui and hasattr(self.app_ui, 'log_panel'):
            self.app_ui.log_panel.log(message, "WARNING")
        logger.warning(message)
        
    def log_error(self, message: str):
        """Log error message."""
        if self.app_ui and hasattr(self.app_ui, 'log_panel'):
            self.app_ui.log_panel.log(message, "ERROR")
        logger.error(message)
        
    def show_message(self, title: str, message: str):
        """Show message dialog to user."""
        if self.app_ui:
            self.app_ui.show_message(title, message)
            
    def show_error(self, title: str, message: str):
        """Show error dialog to user."""
        if self.app_ui:
            self.app_ui.show_error(title, message)
            
    def show_warning(self, title: str, message: str):
        """Show warning dialog to user."""
        if self.app_ui:
            self.app_ui.show_warning(title, message)