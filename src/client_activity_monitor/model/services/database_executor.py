from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Event
from typing import Dict, Callable, Any, Optional, List
import pandas as pd
from datetime import datetime
from loguru import logger
from ..config_manager import ConfigManager
from ..repositories.query_repository import QueryRepository
from ...common.exceptions import DatabaseConnectionError

class DatabaseExecutor:
    """Manages concurrent query execution across multiple databases."""
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize with configuration manager.
        
        Args:
            config_manager: ConfigManager instance
        """
        self.config_manager = config_manager
        
    def test_connections(self, databases: List[Any]) -> Dict[str, bool]:
        """
        Test connections to all databases before starting the main analysis.
        
        Args:
            databases: List of database configurations
            
        Returns:
            Dictionary mapping database names to connection success status
        """
        connection_status = {}
        
        for db_config in databases:
            db_name = db_config.name
            logger.info(f"Testing connection to {db_name}...")
            
            conn_params = self.config_manager.get_connection_params(db_name)
            if not conn_params:
                connection_status[db_name] = False
                continue
                
            repo = QueryRepository(conn_params, db_name)
            try:
                success = repo.connect()
                connection_status[db_name] = success
                if success:
                    logger.info(f"Successfully connected to {db_name}")
                else:
                    logger.error(f"Failed to connect to {db_name}")
            finally:
                repo.close()
                
        return connection_status
    
    def execute_all_databases(
        self,
        start_date: datetime,
        progress_callback: Callable[[str, str, str, Optional[int]], None],
        cancel_event: Event
    ) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Execute queries on all configured databases concurrently.
        
        Args:
            start_date: Start date for all queries (30 days ago)
            progress_callback: Callback(database_name, query_name, status, row_count)
                status: "connecting", "running", "completed", "failed", "cancelled"
            cancel_event: Threading event for cancellation
            
        Returns:
            Nested dictionary:
            {
                "client_activity_analysis": {
                    "Get all email changes": DataFrame,
                    "Get phone changes by client ID": DataFrame,
                    "Get token changes": DataFrame
                },
                "account_activity_analysis": {
                    "Get all password changes": DataFrame
                }
            }
        """
        databases = self.config_manager.get_all_databases()
        results = {}
        
        # First, test all connections before starting the main analysis
        logger.info("Testing database connections...")
        connection_status = self.test_connections(databases)
        
        # Check if any connection failed
        failed_databases = [db for db, success in connection_status.items() if not success]
        if failed_databases:
            error_msg = f"Failed to connect to the following databases: {', '.join(failed_databases)}"
            logger.error(error_msg)
            # Mark all databases as failed in the UI
            for db_config in databases:
                progress_callback(db_config.name, "all", "failed", None)
            raise DatabaseConnectionError(error_msg)
        
        logger.info("All database connections successful. Starting analysis...")
        
        # Use ThreadPoolExecutor for concurrent database execution
        with ThreadPoolExecutor(max_workers=len(databases)) as executor:
            # Submit tasks for each database
            future_to_db = {}
            
            for db_config in databases:
                if cancel_event.is_set():
                    logger.info("Execution cancelled before starting all databases")
                    break
                    
                future = executor.submit(
                    self._execute_single_database,
                    db_config,
                    start_date,
                    progress_callback,
                    cancel_event
                )
                future_to_db[future] = db_config.name
                
            # Collect results as they complete
            for future in as_completed(future_to_db):
                db_name = future_to_db[future]
                
                if cancel_event.is_set():
                    logger.info(f"Skipping results for {db_name} due to cancellation")
                    continue
                    
                try:
                    db_results = future.result()
                    results[db_name] = db_results
                    logger.info(f"Completed all queries for {db_name}")
                except Exception as e:
                    logger.error(f"Database {db_name} execution failed: {e}")
                    progress_callback(db_name, "all", "failed", None)
                    # Cancel all remaining operations
                    cancel_event.set()
                    # Cancel all pending futures
                    for pending_future in future_to_db:
                        if not pending_future.done():
                            pending_future.cancel()
                    # Re-raise the exception to stop all processing
                    raise DatabaseConnectionError(f"Critical error in database {db_name}: {str(e)}")
                    
        return results
        
    def _execute_single_database(
        self,
        db_config: Any,  # DatabaseConfig from config_manager
        start_date: datetime,
        progress_callback: Callable,
        cancel_event: Event
    ) -> Dict[str, pd.DataFrame]:
        """
        Execute all queries for a single database.
        
        Returns:
            Dictionary mapping query names to DataFrames
        """
        db_name = db_config.name
        results = {}
        
        # Update progress: connecting
        progress_callback(db_name, "all", "connecting", None)
        
        # Get connection parameters
        conn_params = self.config_manager.get_connection_params(db_name)
        if not conn_params:
            logger.error(f"Failed to get connection parameters for {db_name}")
            progress_callback(db_name, "all", "failed", None)
            return results
            
        # Create repository instance
        repo = QueryRepository(conn_params, db_name)
        
        try:
            # Connect to database
            if not repo.connect():
                progress_callback(db_name, "all", "failed", None)
                raise DatabaseConnectionError(f"Failed to connect to database: {db_name}")
                
            # Execute each query defined for this database
            for query_def in db_config.sql_queries:
                if cancel_event.is_set():
                    progress_callback(db_name, query_def.name, "cancelled", None)
                    logger.info(f"Cancelled query {query_def.name} on {db_name}")
                    break
                    
                # Update progress: running query
                progress_callback(db_name, query_def.name, "running", None)
                
                # Execute query
                df = repo.execute_query(
                    query_name=query_def.name,
                    sql_file_path=query_def.query_location,
                    start_date=start_date
                )
                
                # Store result
                results[query_def.name] = df
                
                # Update progress: completed
                row_count = len(df) if not df.empty else 0
                progress_callback(db_name, query_def.name, "completed", row_count)
                
        except Exception as e:
            logger.error(f"Error executing queries on {db_name}: {e}")
            progress_callback(db_name, "all", "failed", None)
        finally:
            # Always close connection
            repo.close()
            
        return results