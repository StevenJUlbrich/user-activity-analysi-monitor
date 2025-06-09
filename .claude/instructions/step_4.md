# Step 4: Database Query Execution

## Objective
Implement concurrent query execution across multiple Oracle databases using the existing `ez_connect_oracle.py` module. Each database runs its own specific set of queries as defined in `databases.yaml`.

## A. Query Repository Implementation

Create `src/client_activity_monitor/model/repositories/query_repository.py`:

### Purpose
Handles connection and query execution for a SINGLE database. Multiple instances will be created for concurrent execution.

### Implementation

```python
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime
from loguru import logger
from .ez_connect_oracle import OracleKerberosConnection

class QueryRepository:
    """Handles query execution for a single Oracle database."""
    
    def __init__(self, connection_params: Dict[str, Any], database_name: str):
        """
        Initialize repository for a specific database.
        
        Args:
            connection_params: Parameters for OracleKerberosConnection
            database_name: Name of the database for logging
        """
        self.connection_params = connection_params
        self.database_name = database_name
        self.connection: Optional[OracleKerberosConnection] = None
        
    def connect(self) -> bool:
        """
        Establish database connection using Kerberos authentication.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.connection = OracleKerberosConnection(self.connection_params)
            self.connection.connect()
            logger.info(f"Connected to database: {self.database_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to {self.database_name}: {e}")
            return False
            
    def execute_query(self, query_name: str, sql_file_path: str, start_date: datetime) -> pd.DataFrame:
        """
        Execute a single query from SQL file.
        
        Args:
            query_name: Name of the query for logging
            sql_file_path: Path to SQL file
            start_date: Start date parameter for the query
            
        Returns:
            DataFrame with query results (empty if query fails)
        """
        if not self.connection:
            logger.error(f"No connection available for {self.database_name}")
            return pd.DataFrame()
            
        try:
            # Read SQL from file
            sql_path = Path(sql_file_path)
            if not sql_path.exists():
                logger.error(f"SQL file not found: {sql_file_path}")
                return pd.DataFrame()
                
            with open(sql_path, 'r') as f:
                sql = f.read()
                
            # Execute query with parameter
            params = {'start_date': start_date}
            logger.info(f"Executing {query_name} on {self.database_name}")
            
            results = self.connection.execute_query(sql, params)
            df = pd.DataFrame(results)
            
            logger.info(f"Query {query_name} returned {len(df)} rows from {self.database_name}")
            return df
            
        except Exception as e:
            logger.error(f"Query {query_name} failed on {self.database_name}: {e}")
            return pd.DataFrame()
            
    def close(self):
        """Close database connection."""
        if self.connection:
            try:
                self.connection.close()
                logger.info(f"Closed connection to {self.database_name}")
            except Exception as e:
                logger.error(f"Error closing connection to {self.database_name}: {e}")
            finally:
                self.connection = None
```

## B. Database Executor Service

Create `src/client_activity_monitor/model/services/database_executor.py`:

### Purpose
Manages concurrent execution across ALL configured databases, running each database's specific queries.

### Implementation

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Event
from typing import Dict, Callable, Any, Optional
import pandas as pd
from datetime import datetime
from loguru import logger
from ..config_manager import ConfigManager
from ..repositories.query_repository import QueryRepository

class DatabaseExecutor:
    """Manages concurrent query execution across multiple databases."""
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize with configuration manager.
        
        Args:
            config_manager: ConfigManager instance
        """
        self.config_manager = config_manager
        
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
                    results[db_name] = {}
                    
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
                return results
                
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
```

## C. Progress Callback Implementation

The UI should handle progress updates like this:

```python
def update_database_status(database_name: str, query_name: str, status: str, row_count: Optional[int] = None):
    """
    Update the Database Status panel with query progress.
    
    Args:
        database_name: e.g., "client_activity_analysis"
        query_name: e.g., "Get all email changes" or "all" for database-level status
        status: "connecting", "running", "completed", "failed", "cancelled"
        row_count: Number of rows returned (only for "completed" status)
    """
    # This would update the Database Status panel in the UI
    # Implementation depends on your UI framework
    
    if query_name == "all":
        # Database-level status
        logger.info(f"Database {database_name}: {status}")
    else:
        # Query-level status
        if status == "completed":
            logger.info(f"{database_name} - {query_name}: {status} ({row_count} rows)")
        else:
            logger.info(f"{database_name} - {query_name}: {status}")
```

## D. Controller Integration Example

```python
class MainController:
    def _run_analysis_thread(self, start_date: datetime, last_event_time: datetime):
        """Run the analysis in a separate thread."""
        try:
            # Execute queries on all databases
            self.database_executor = DatabaseExecutor(self.config_manager)
            
            results = self.database_executor.execute_all_databases(
                start_date=start_date,
                progress_callback=self.update_database_status_ui,
                cancel_event=self.cancel_event
            )
            
            # Log summary
            for db_name, queries in results.items():
                logger.info(f"Database {db_name} returned {len(queries)} query results")
                for query_name, df in queries.items():
                    logger.info(f"  - {query_name}: {len(df)} rows")
                    
            # Continue to merge/filter (Step 5)...
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
```

## E. Key Implementation Notes

1. **Concurrent Execution**: Each database runs in its own thread via ThreadPoolExecutor
2. **Database-Specific Queries**: Each database runs only its configured queries
3. **Progress Updates**: Real-time updates for both database and query level
4. **Cancellation Support**: Check cancel_event between queries
5. **Error Isolation**: One database failure doesn't stop others
6. **Resource Cleanup**: Always close connections in finally blocks

## F. Expected Results Structure

After execution, results will look like:
```python
{
    "client_activity_analysis": {
        "Get all email changes": DataFrame(...),
        "Get phone changes by client ID": DataFrame(...),
        "Get token changes": DataFrame(...)
    },
    "account_activity_analysis": {
        "Get all password changes": DataFrame(...)
    }
}
```

## G. Error Handling

1. **Connection Failures**: Log and continue with other databases
2. **Query Failures**: Return empty DataFrame, log error
3. **Missing SQL Files**: Return empty DataFrame, log error
4. **Cancellation**: Stop remaining queries, return partial results
5. **Thread Exceptions**: Catch and log, don't crash the application

## Next Step
After implementing database query execution, proceed to Step 5: Data Merging & Filtering Logic to combine results from all databases and identify users meeting all criteria.