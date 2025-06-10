"""
Main Controller for Client Activity Monitor

This module serves as the central controller for the application,
coordinating between the Model and View components.
"""

import threading
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from pathlib import Path
from loguru import logger
from ..model.config_manager import ConfigManager


class MainController:
    """
    Central controller for the Client Activity Monitor application.
    
    Orchestrates all application operations and manages the flow
    between UI components and business logic.
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
        
        This will be implemented in future steps to start the UI.
        """
        logger.info("Starting Client Activity Monitor...")
        # TODO: Initialize and start UI (Step 9)
        print("Application controller initialized. UI implementation coming in Step 9.")
        
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
            
        except Exception as e:
            logger.error(f"Failed to start analysis: {e}")
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
            # TODO: Execute queries (Step 4)
            # results = self.database_executor.execute_all_databases(
            #     start_date=start_date,
            #     progress_callback=self.update_database_status,
            #     cancel_event=self.cancel_event
            # )
            
            # TODO: Merge and filter results (Step 5)
            # filtered_data = self.merge_filter_service.process_results(
            #     results, 
            #     last_event_time
            # )
            
            # TODO: Generate report (Step 6)
            # if not filtered_data.empty:
            #     self.last_report_path = self.report_generator.create_excel_report(
            #         filtered_data,
            #         self.config_manager.get_user_sid(),
            #         last_event_time
            #     )
            #     self.last_report_data = filtered_data
            #     
            #     # Enable report actions
            #     if self.run_analysis_panel:
            #         self.run_analysis_panel.enable_report_actions(True)
            #     
            #     # Update last event time to now
            #     new_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            #     if self.run_analysis_panel:
            #         self.run_analysis_panel.update_last_event_time(new_time)
            #     
            #     logger.info(f"Report generated: {self.last_report_path}")
            # else:
            #     logger.info("No users met all criteria")
            
            # Temporary: Simulate analysis completion
            import time
            time.sleep(3)  # Simulate processing
            logger.info("Analysis simulation complete")
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
        finally:
            if self.run_analysis_panel:
                self.run_analysis_panel.set_running_state(False)
            
    def on_generate_email(self):
        """Handle Generate Email Report button."""
        if self.last_report_path:
            # TODO: Implementation in Step 7
            logger.info("Generate Email Report clicked")
        else:
            logger.warning("No report available for email")
            
    def on_copy_excel_path(self):
        """Handle Copy Excel Path to Clipboard button."""
        if self.last_report_path:
            # TODO: Implementation in Step 6
            logger.info("Copy Excel Path clicked")
        else:
            logger.warning("No report path to copy")
            
    def on_copy_onenote(self):
        """Handle OneNote Entry to Clipboard button."""
        if self.last_report_data is not None:
            # TODO: Implementation in Step 8
            logger.info("OneNote Entry clicked")
        else:
            logger.warning("No report data for OneNote")
            
    def on_optional_save(self):
        """Handle Optional Save Report button (CSV export)."""
        if self.last_report_data is not None:
            # TODO: Save as CSV
            # csv_path = self.report_generator.create_csv_report(self.last_report_data)
            logger.info("Optional Save Report clicked")
        else:
            logger.warning("No report data to save")
            
    def update_database_status(self, database_name: str, query_name: str, 
                              status: str, row_count: Optional[int] = None):
        """
        Progress callback for database executor.
        
        Args:
            database_name: Name of the database
            query_name: Name of the query or "all" for database-level status
            status: Status string
            row_count: Optional row count for completed queries
        """
        # TODO: Update database status panel (Step 9)
        logger.info(f"Database {database_name} - {query_name}: {status}")
        if row_count is not None:
            logger.info(f"  Rows returned: {row_count}")