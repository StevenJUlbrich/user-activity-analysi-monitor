from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime
from loguru import logger
from .ez_connect_oracle import OracleKerberosConnection
from ...common.exceptions import DatabaseConnectionError

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
            error_msg = str(e)
            # Check for common connection errors
            if "ORA-01017" in error_msg:
                logger.error(f"Authentication failed for {self.database_name}: Invalid credentials or Kerberos ticket expired")
            elif "ORA-12170" in error_msg or "timeout" in error_msg.lower():
                logger.error(f"Connection timeout for {self.database_name}: Unable to reach database server")
            elif "ORA-12154" in error_msg:
                logger.error(f"TNS error for {self.database_name}: Service name not found")
            else:
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