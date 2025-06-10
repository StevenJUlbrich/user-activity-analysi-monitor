import datetime
import json
import logging
import os
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import oracledb
from pydantic import BaseModel, Field, field_validator, model_validator


class OracleClientConfig(BaseModel):
    """Oracle Client Configuration for Kerberos authentication"""

    instant_client_dir: Path
    krb5_conf: Path
    krb5_cache: Path
    trace_level: Optional[int] = None
    trace_directory: Optional[Path] = None

    @field_validator("instant_client_dir", "krb5_conf", "krb5_cache", mode="before")
    @classmethod
    def convert_to_path(cls, v):
        """Convert string paths to Path objects"""
        if isinstance(v, str):
            return Path(v)
        return v

    @field_validator("instant_client_dir")
    @classmethod
    def instant_client_dir_must_exist(cls, v):
        """Validate that instant client directory exists"""
        if not v.exists():
            raise ValueError(f"Oracle Instant Client directory not found: {v}")
        return v

    @field_validator("krb5_conf")
    @classmethod
    def krb5_conf_must_exist(cls, v):
        """Validate that krb5.conf file exists"""
        if not v.exists():
            raise ValueError(f"Kerberos configuration file not found: {v}")
        return v


class DatabaseConnectionConfig(BaseModel):
    """Configuration for connecting to an Oracle database"""

    host: str
    port: int
    service_name: str
    default_schema: Optional[str] = None
    oracle_client: OracleClientConfig

    @field_validator("host")
    @classmethod
    def host_not_empty(cls, v):
        """Validate that host is not empty"""
        if not v or not isinstance(v, str):
            raise ValueError("Host must be a non-empty string")
        return v

    @field_validator("port")
    @classmethod
    def port_must_be_valid(cls, v):
        """Validate that port is in valid range"""
        if not isinstance(v, int) or v <= 0 or v > 65535:
            raise ValueError(
                f"Port must be a positive integer between 1 and 65535, got {v}"
            )
        return v

    @field_validator("service_name")
    @classmethod
    def service_name_not_empty(cls, v):
        """Validate that service name is not empty"""
        if not v or not isinstance(v, str):
            raise ValueError("Service name must be a non-empty string")
        return v


class ConnectionPoolConfig(BaseModel):
    """Configuration for Oracle connection pool"""

    min_size: int = 1
    max_size: int = 5
    increment: int = 1
    timeout: int = 60

    @field_validator("min_size", "max_size", "increment")
    @classmethod
    def must_be_positive(cls, v, info):
        """Validate that pool sizes are positive"""
        if v <= 0:
            raise ValueError(f"{info.field_name} must be positive")
        return v

    @model_validator(mode="after")
    def check_sizes(self):
        """Validate that min_size <= max_size"""
        if self.min_size > self.max_size:
            raise ValueError(
                f"min_size ({self.min_size}) cannot be greater than max_size ({self.max_size})"
            )
        return self


class CredentialsConfig(BaseModel):
    """Configuration for username/password credentials"""

    username: Optional[str] = None
    password: Optional[str] = None
    wallet_location: Optional[Path] = None

    @field_validator("wallet_location", mode="before")
    @classmethod
    def convert_to_path(cls, v):
        """Convert string path to Path object"""
        if isinstance(v, str) and v:
            return Path(v)
        return v

    @field_validator("wallet_location")
    @classmethod
    def wallet_location_must_exist(cls, v):
        """Validate that wallet location exists if provided"""
        if v is not None and not v.exists():
            raise ValueError(f"Oracle wallet directory not found: {v}")
        return v


class OracleKerberosConnection:
    """
    A comprehensive class to handle Oracle Database connections using Kerberos authentication.
    Optimized for concurrency, clarity, and reliability with enhanced configuration options.
    Uses Pydantic v2 for configuration validation.
    """

    _init_lock = threading.Lock()
    _client_initialized = False

    def __init__(
        self,
        config: Union[Dict[str, Any], DatabaseConnectionConfig],
        log_level: int = logging.INFO,
    ):
        """
        Initialize the Oracle Kerberos Connection with validated configuration.

        Args:
            config: Either a DatabaseConnectionConfig instance or a dictionary
            that can be parsed into one
            log_level: Logging level (default: INFO)

        Raises:
            ValidationError: If configuration is invalid
            ValueError: If required parameters are invalid
            FileNotFoundError: If required files or directories don't exist
        """
        # Ensure we have a Pydantic model
        if not isinstance(config, DatabaseConnectionConfig):
            config = DatabaseConnectionConfig.model_validate(config)

        # Extract configuration values
        self.host = config.host
        self.port = config.port
        self.service_name = config.service_name
        self.default_schema = config.default_schema

        # Extract client configuration values
        self.instant_client_dir = config.oracle_client.instant_client_dir
        self.krb5_conf = config.oracle_client.krb5_conf
        self.krb5_cache = config.oracle_client.krb5_cache
        self.trace_level = config.oracle_client.trace_level
        self.trace_directory = config.oracle_client.trace_directory

        # Store the validated config
        self.config = config

        # Initialize connection state
        self.connection = None
        self.pool = None

        # Initialize logger with thread ID for concurrent environments
        self.logger = logging.getLogger(
            f"oracle_conn_{self.host}_{threading.get_ident()}"
        )
        self._configure_logging(log_level)

    def _configure_logging(self, log_level: int):
        """
        Configure logging handlers and formatting explicitly.

        Args:
            log_level: Logging level to use
        """
        if not self.logger.handlers:
            # Create console handler
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            # Create file handler
            file_handler = logging.FileHandler("oracle_connection.log")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            # Set log level
            self.logger.setLevel(log_level)
            self.logger.info("Logger configured successfully")

    def setup_environment(self):
        """
        Safely sets environment variables and initializes Oracle client.
        Uses thread-safe initialization to ensure client is only initialized once.
        """
        self.logger.info(
            "Setting environment variables and initializing Oracle client."
        )
        with OracleKerberosConnection._init_lock:
            if not OracleKerberosConnection._client_initialized:
                self._configure_environment()
                OracleKerberosConnection._client_initialized = True

    def _configure_environment(self):
        """
        Configure Oracle Instant Client environment with proper path handling
        and platform-independent settings.
        """
        # Set Oracle environment variables
        os.environ["ORACLE_HOME"] = str(self.instant_client_dir)
        # Use platform-independent path separator
        os.environ["PATH"] = (
            f"{self.instant_client_dir}{os.pathsep}{os.environ.get('PATH', '')}"
        )
        os.environ["KRB5_CONFIG"] = str(self.krb5_conf)
        os.environ["KRB5CCNAME"] = f"FILE:{self.krb5_cache}"

        # Set up network/admin directory
        network_admin = self.instant_client_dir / "network" / "admin"
        network_admin.mkdir(parents=True, exist_ok=True)
        os.environ["TNS_ADMIN"] = str(network_admin)
        self.logger.info(f"TNS_ADMIN set to: {network_admin}")

        # Create trace directory if configured
        trace_config = ""
        if self.trace_level is not None and self.trace_directory:
            self.trace_directory.mkdir(parents=True, exist_ok=True)
            trace_config = (
                f"TRACE_LEVEL_CLIENT = {self.trace_level}\n"
                f"TRACE_DIRECTORY_CLIENT = {self.trace_directory}\n"
                "TRACE_FILE_CLIENT = oracle_client_trace\n"
                "TRACE_UNIQUE_CLIENT = TRUE\n"
            )

        # Create sqlnet.ora with Kerberos authentication settings
        sqlnet_path = network_admin / "sqlnet.ora"
        sqlnet_content = (
            "SQLNET.AUTHENTICATION_SERVICES = (BEQ, KERBEROS5)\n"
            f"SQLNET.KERBEROS5_CONF = {self.krb5_conf}\n"
            "SQLNET.KERBEROS5_CONF_MIT = TRUE\n"
            f"SQLNET.KERBEROS5_CC_NAME = FILE:{self.krb5_cache}\n"
            f"{trace_config}"
        )
        sqlnet_path.write_text(sqlnet_content)
        self.logger.info(f"Created sqlnet.ora at {sqlnet_path}")

        # Initialize Oracle client
        try:
            oracledb.init_oracle_client(lib_dir=str(self.instant_client_dir))
            self.logger.info("Oracle client initialized successfully.")
        except oracledb.exceptions.ProgrammingError as e:
            if "already initialized" not in str(e).lower():
                self.logger.exception("Oracle client initialization error.")
                raise
            self.logger.info("Oracle client was already initialized.")

    def get_ez_connect_string(self) -> str:
        """
        Returns EZ connect formatted connection string.

        Returns:
            str: The Oracle EZ Connect string
        """
        return (
            f"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={self.host})(PORT={self.port}))"
            f"(CONNECT_DATA=(SERVICE_NAME={self.service_name})))"
        )

    def connect(self):
        """
        Connect to the Oracle database using Kerberos authentication.

        Returns:
            The database connection object

        Raises:
            oracledb.DatabaseError: If database connection fails
            Exception: For other unexpected errors
        """
        self.setup_environment()
        try:
            dsn = self.get_ez_connect_string()
            self.connection = oracledb.connect(dsn=dsn, mode=oracledb.AUTH_MODE_DEFAULT)
            self.logger.info(
                f"Connected to Oracle database version: {self.connection.version}"
            )

            if self.default_schema:
                self.set_current_schema(self.default_schema)

            return self.connection
        except oracledb.DatabaseError as e:
            self.logger.exception(f"Database connection error: {str(e)}")
            raise
        except Exception as e:
            self.logger.exception(f"Unexpected error during connection: {str(e)}")
            raise

    def connect_with_credentials(
        self, credentials: Union[Dict[str, Any], CredentialsConfig]
    ):
        """
        Connect with username/password or wallet credentials as an alternative to Kerberos.

        Args:
            credentials: CredentialsConfig model or dictionary with credential information

        Returns:
            The database connection object

        Raises:
            ValueError: If neither credentials nor Kerberos is properly configured
            oracledb.DatabaseError: If database connection fails
        """
        self.setup_environment()

        # Convert to Pydantic model if needed
        if not isinstance(credentials, CredentialsConfig):
            credentials = CredentialsConfig.model_validate(credentials)

        # Use credentials from environment if not provided
        username = credentials.username or os.environ.get("ORACLE_USERNAME")
        password = credentials.password or os.environ.get("ORACLE_PASSWORD")
        wallet_location = credentials.wallet_location

        try:
            dsn = self.get_ez_connect_string()

            # Use wallet if provided
            if wallet_location:
                os.environ["TNS_ADMIN"] = str(wallet_location)
                self.connection = oracledb.connect(dsn=dsn)
                self.logger.info("Connected using Oracle wallet authentication")
            # Use username/password if provided
            elif username and password:
                self.connection = oracledb.connect(
                    user=username, password=password, dsn=dsn
                )
                self.logger.info("Connected using username/password authentication")
            # Fall back to default AUTH_MODE_DEFAULT (Kerberos)
            else:
                self.connection = oracledb.connect(
                    dsn=dsn, mode=oracledb.AUTH_MODE_DEFAULT
                )
                self.logger.info("Connected using Kerberos authentication")

            self.logger.info(
                f"Connected to Oracle database version: {self.connection.version}"
            )

            if self.default_schema:
                self.set_current_schema(self.default_schema)

            return self.connection
        except Exception as e:
            self.logger.exception(f"Connection failed: {str(e)}")
            raise

    def create_connection_pool(
        self, pool_config: Union[Dict[str, Any], ConnectionPoolConfig] = None
    ):
        """
        Create and return a connection pool for multi-connection applications.

        Args:
            pool_config: ConnectionPoolConfig instance or dictionary with pool parameters

        Returns:
            The connection pool object

        Raises:
            oracledb.DatabaseError: If pool creation fails
        """
        self.setup_environment()

        # Use default config if none provided
        if pool_config is None:
            pool_config = ConnectionPoolConfig()
        # Convert to Pydantic model if needed
        elif not isinstance(pool_config, ConnectionPoolConfig):
            pool_config = ConnectionPoolConfig.model_validate(pool_config)

        try:
            pool = oracledb.create_pool(
                dsn=self.get_ez_connect_string(),
                min=pool_config.min_size,
                max=pool_config.max_size,
                increment=pool_config.increment,
                timeout=pool_config.timeout,
                mode=oracledb.AUTH_MODE_DEFAULT,
                threaded=True,
            )
            self.pool = pool
            self.logger.info(
                f"Connection pool created with min={pool_config.min_size}, "
                f"max={pool_config.max_size}, increment={pool_config.increment}"
            )
            return pool
        except Exception as e:
            self.logger.exception(f"Failed to create connection pool: {str(e)}")
            raise

    def get_connection_from_pool(self):
        """
        Get a connection from the pool.

        Returns:
            A connection from the pool

        Raises:
            ValueError: If no pool has been created
            oracledb.DatabaseError: If acquiring a connection fails
        """
        if not self.pool:
            raise ValueError(
                "Connection pool has not been created. Call create_connection_pool first."
            )

        try:
            conn = self.pool.acquire()
            self.logger.info("Acquired connection from pool")
            return conn
        except Exception as e:
            self.logger.exception(f"Failed to acquire connection from pool: {str(e)}")
            raise

    def release_connection_to_pool(self, conn):
        """
        Release a connection back to the pool.

        Args:
            conn: The connection to release

        Raises:
            ValueError: If no pool has been created
        """
        if not self.pool:
            raise ValueError("Connection pool has not been created.")

        try:
            self.pool.release(conn)
            self.logger.info("Released connection back to pool")
        except Exception as e:
            self.logger.exception(f"Failed to release connection to pool: {str(e)}")
            raise

    def set_current_schema(self, schema_name: str):
        """
        Sets the current schema for the connection.

        Args:
            schema_name: The schema name to set

        Raises:
            ValueError: If no active connection
            oracledb.DatabaseError: If setting the schema fails
        """
        if not self.connection:
            raise ValueError("No active connection. Connect first.")

        with self.connection.cursor() as cursor:
            cursor.execute(f"ALTER SESSION SET CURRENT_SCHEMA = {schema_name}")
            self.logger.info(f"Schema set to: {schema_name}")

    def get_current_schema(self) -> Optional[str]:
        """
        Gets the current schema.

        Returns:
            str: The current schema name or None if not available

        Raises:
            ValueError: If no active connection
            oracledb.DatabaseError: If retrieving the schema fails
        """
        if not self.connection:
            raise ValueError("No active connection. Connect first.")

        with self.connection.cursor() as cursor:
            cursor.execute("SELECT SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA') FROM DUAL")
            result = cursor.fetchone()
            schema = result[0] if result else None
            self.logger.info(f"Current schema: {schema}")
            return schema

    def execute_query(
        self, sql: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a query and return results as a list of dictionaries.

        Args:
            sql: SQL query to execute
            params: Parameters for the query (optional)

        Returns:
            List of dictionaries with query results

        Raises:
            ValueError: If no active connection
            oracledb.DatabaseError: If query execution fails
        """
        if not self.connection:
            raise ValueError("No active connection. Connect first.")

        with self.connection.cursor() as cursor:
            cursor.execute(sql, params or {})
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            return []

    def execute_many(self, sql: str, params: List[Dict[str, Any]]) -> int:
        """
        Execute a batch operation with multiple parameter sets.

        Args:
            sql: SQL statement to execute
            params: List of parameter dictionaries

        Returns:
            int: Number of rows affected

        Raises:
            ValueError: If no active connection
            oracledb.DatabaseError: If execution fails
        """
        if not self.connection:
            raise ValueError("No active connection. Connect first.")

        with self.connection.cursor() as cursor:
            cursor.executemany(sql, params)
            return cursor.rowcount

    def begin_transaction(self):
        """
        Begin a transaction explicitly (for documentation purposes - Oracle
        automatically begins transactions when needed).

        Raises:
            ValueError: If no active connection
        """
        if not self.connection:
            raise ValueError("No active connection. Connect first.")

        self.logger.info("Transaction started")

    def commit(self):
        """
        Commit the current transaction.

        Raises:
            ValueError: If no active connection
            oracledb.DatabaseError: If commit fails
        """
        if not self.connection:
            raise ValueError("No active connection. Connect first.")

        try:
            self.connection.commit()
            self.logger.info("Transaction committed")
        except Exception as e:
            self.logger.exception(f"Commit failed: {str(e)}")
            raise

    def rollback(self):
        """
        Rollback the current transaction.

        Raises:
            ValueError: If no active connection
            oracledb.DatabaseError: If rollback fails
        """
        if not self.connection:
            raise ValueError("No active connection. Connect first.")

        try:
            self.connection.rollback()
            self.logger.info("Transaction rolled back")
        except Exception as e:
            self.logger.exception(f"Rollback failed: {str(e)}")
            raise

    def ensure_connection(self):
        """
        Ensure the connection is active and reconnect if necessary.

        Returns:
            The active connection

        Raises:
            Exception: If reconnection fails
        """
        try:
            if not self.connection:
                self.logger.info("No active connection, connecting...")
                return self.connect()

            # Test the connection with a simple query
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM DUAL")
                cursor.fetchone()
                return self.connection
        except Exception as e:
            self.logger.warning(f"Connection test failed: {str(e)}, reconnecting...")
            try:
                if self.connection:
                    self.close()
                return self.connect()
            except Exception as reconnect_error:
                self.logger.exception(f"Reconnection failed: {str(reconnect_error)}")
                raise

    def close(self):
        """
        Close the database connection explicitly.
        """
        if self.connection:
            try:
                self.connection.close()
                self.logger.info("Database connection closed.")
            except Exception as e:
                self.logger.exception(f"Error closing connection: {str(e)}")
            finally:
                self.connection = None

        if self.pool:
            try:
                self.pool.close()
                self.logger.info("Connection pool closed.")
            except Exception as e:
                self.logger.exception(f"Error closing connection pool: {str(e)}")
            finally:
                self.pool = None

    def __enter__(self):
        """
        Context manager enter method.

        Returns:
            self: The connection instance
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit method.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        self.close()

    @classmethod
    def from_config_file(
        cls, config_file: Union[str, Path], log_level: int = logging.INFO
    ):
        """
        Create a connection instance from a JSON or YAML configuration file.

        Args:
            config_file: Path to the configuration file
            log_level: Logging level to use

        Returns:
            OracleKerberosConnection: A new connection instance

        Raises:
            FileNotFoundError: If the config file doesn't exist
            json.JSONDecodeError: If the config file isn't valid JSON
            ValueError: If the config file has an unsupported format
        """
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        # Load config based on file extension
        if config_path.suffix.lower() in [".json"]:
            with open(config_path, "r") as f:
                try:
                    config_dict = json.load(f)
                except json.JSONDecodeError as e:
                    raise json.JSONDecodeError(
                        f"Invalid JSON in configuration file: {str(e)}", e.doc, e.pos
                    )
        elif config_path.suffix.lower() in [".yaml", ".yml"]:
            try:
                import yaml

                with open(config_path, "r") as f:
                    config_dict = yaml.safe_load(f)
            except ImportError:
                raise ImportError(
                    "PyYAML is required for YAML config files. Install with 'pip install pyyaml'"
                )
            except Exception as e:
                raise ValueError(f"Error loading YAML configuration: {str(e)}")
        else:
            raise ValueError(f"Unsupported config file format: {config_path.suffix}")

        # Create connection with validated config
        return cls(config=config_dict, log_level=log_level)

    @classmethod
    def from_environment(cls, log_level: int = logging.INFO):
        """
        Create a connection instance from environment variables.

        Environment variables used:
        - ORACLE_HOST: Database hostname
        - ORACLE_PORT: Database port
        - ORACLE_SERVICE_NAME: Oracle service name
        - ORACLE_DEFAULT_SCHEMA: Default schema (optional)
        - ORACLE_INSTANT_CLIENT_DIR: Path to Oracle Instant Client
        - ORACLE_KRB5_CONF: Path to Kerberos config
        - ORACLE_KRB5_CACHE: Path to Kerberos ticket cache
        - ORACLE_TRACE_LEVEL: Oracle trace level (optional)
        - ORACLE_TRACE_DIRECTORY: Oracle trace directory (optional)

        Returns:
            OracleKerberosConnection: A new connection instance

        Raises:
            ValueError: If required environment variables are missing
        """
        # Check required environment variables
        required_vars = [
            "ORACLE_HOST",
            "ORACLE_PORT",
            "ORACLE_SERVICE_NAME",
            "ORACLE_INSTANT_CLIENT_DIR",
            "ORACLE_KRB5_CONF",
            "ORACLE_KRB5_CACHE",
        ]

        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        # Build config from environment
        config = {
            "host": os.environ["ORACLE_HOST"],
            "port": int(os.environ["ORACLE_PORT"]),
            "service_name": os.environ["ORACLE_SERVICE_NAME"],
            "default_schema": os.environ.get("ORACLE_DEFAULT_SCHEMA"),
            "oracle_client": {
                "instant_client_dir": os.environ["ORACLE_INSTANT_CLIENT_DIR"],
                "krb5_conf": os.environ["ORACLE_KRB5_CONF"],
                "krb5_cache": os.environ["ORACLE_KRB5_CACHE"],
            },
        }

        # Add optional trace configuration
        if "ORACLE_TRACE_LEVEL" in os.environ:
            config["oracle_client"]["trace_level"] = int(
                os.environ["ORACLE_TRACE_LEVEL"]
            )

        if "ORACLE_TRACE_DIRECTORY" in os.environ:
            config["oracle_client"]["trace_directory"] = os.environ[
                "ORACLE_TRACE_DIRECTORY"
            ]

        return cls(config=config, log_level=log_level)


# Module-level convenience functions
def get_connection_from_config(
    config_file: Union[str, Path], log_level: int = logging.INFO
) -> OracleKerberosConnection:
    """
    Convenience function to create and connect using a configuration file.

    Args:
        config_file: Path to the configuration file
        log_level: Logging level to use

    Returns:
        Connected OracleKerberosConnection instance
    """
    conn = OracleKerberosConnection.from_config_file(config_file, log_level)
    conn.connect()
    return conn


def execute_with_config(
    config_file: Union[str, Path], sql: str, params: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function to execute a query using a configuration file.

    Args:
        config_file: Path to the configuration file
        sql: SQL query to execute
        params: Parameters for the query (optional)

    Returns:
        List of dictionaries with query results
    """
    with get_connection_from_config(config_file) as conn:
        return conn.execute_query(sql, params)


if __name__ == "__main__":
    # Example configuration
    config = {
        "host": "proddbgo.example.com",
        "port": 1521,
        "service_name": "ORCL",
        "default_schema": "MYSCHEMA",
        "oracle_client": {
            "instant_client_dir": "/path/to/instantclient",
            "krb5_conf": "/path/to/krb5.conf",
            "krb5_cache": "/path/to/krb5cc",
            "trace_level": 16,
            "trace_directory": "/path/to/trace",
        },
    }

    # Save example config to show the format
    with open("oracle_config_example.json", "w") as f:
        json.dump(config, f, indent=2)

    print("Saved example configuration to oracle_config_example.json")
    print("To use this script, update the paths in the configuration and run:")
    print("python ez_connect_oracle.py")

    # Uncomment and modify to test:
    """
    try:
        # Example 1: Basic connection with context manager
        with OracleKerberosConnection(config=config) as db_conn:
            schema = db_conn.get_current_schema()
            print(f"Connected schema: {schema}")

            # Basic query
            results = db_conn.execute_query("SELECT SYSDATE FROM DUAL")
            print(f"Current date: {results[0]['SYSDATE']}")

            # Query with parameters
            params = {"start_date": datetime.datetime(2023, 1, 1)}
            results = db_conn.execute_query(
                "SELECT * FROM orders WHERE order_date >= :start_date", params
            )
            print(f"Found {len(results)} orders")

        # Example 2: Connection pooling
        db_conn = OracleKerberosConnection(config=config)
        
        # Create a connection pool
        pool_config = ConnectionPoolConfig(min_size=2, max_size=10)
        pool = db_conn.create_connection_pool(pool_config)

        # Get connections from the pool
        conn1 = db_conn.get_connection_from_pool()
        conn2 = db_conn.get_connection_from_pool()

        # Use connections
        with conn1.cursor() as cursor:
            cursor.execute("SELECT 1 FROM DUAL")

        # Release connections back to the pool
        db_conn.release_connection_to_pool(conn1)
        db_conn.release_connection_to_pool(conn2)

        # Close the pool when done
        db_conn.close()

        # Example 3: Using configuration file
        results = execute_with_config(
            "oracle_config_example.json",
            "SELECT 'Hello, Oracle!' as greeting FROM DUAL",
        )
        print(results[0]["GREETING"])
        
        # Example 4: Using environment variables
        os.environ['ORACLE_HOST'] = 'proddbgo.example.com'
        os.environ['ORACLE_PORT'] = '1521'
        os.environ['ORACLE_SERVICE_NAME'] = 'ORCL'
        os.environ['ORACLE_DEFAULT_SCHEMA'] = 'MYSCHEMA'
        os.environ['ORACLE_INSTANT_CLIENT_DIR'] = '/path/to/instantclient'
        os.environ['ORACLE_KRB5_CONF'] = '/path/to/krb5.conf'
        os.environ['ORACLE_KRB5_CACHE'] = '/path/to/krb5cc'
        
        conn = OracleKerberosConnection.from_environment()
        conn.connect()
        print(f"Connected to {conn.host} using environment variables")
        conn.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")
    """
