# Oracle Kerberos Connection Documentation

## Table of Contents

1. [Overview](#overview)
2. [Installation Requirements](#installation-requirements)
3. [Configuration](#configuration)
4. [Usage Guide](#usage-guide)
5. [API Reference](#api-reference)
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Overview

The `ez_connect_oracle.py` module provides a robust, thread-safe Oracle database connection manager with Kerberos authentication support. It's designed for enterprise environments where security and reliability are paramount.

### Key Features

- **Kerberos Authentication**: Secure, password-less authentication
- **Connection Pooling**: Efficient resource management for multi-threaded applications
- **Thread-Safe**: Safe for concurrent usage
- **Configuration File Support**: Easy management via YAML/JSON
- **Comprehensive Logging**: Detailed debugging and monitoring
- **Transaction Management**: Full support for commits and rollbacks
- **Automatic Reconnection**: Handles connection failures gracefully

## Installation Requirements

### System Requirements

- Python 3.8 or higher
- Oracle Instant Client 19c or higher
- Kerberos client utilities installed
- Valid Kerberos ticket

### Python Dependencies

```bash
pip install oracledb pyyaml
```

### Oracle Instant Client Setup

1. Download Oracle Instant Client from Oracle's website
2. Extract to a directory (e.g., `/opt/oracle/instantclient`)
3. Ensure the directory contains the required libraries

## Configuration

### Configuration File Structure

The module supports two configuration files for separation of concerns:

#### 1. User Configuration (`configs/user_config.yaml`)

This file contains user-specific and environment settings:

```yaml
oracle_client:
  instant_client_dir: "/opt/oracle/instantclient"
  krb5_conf: "/etc/krb5.conf"
  krb5_cache: "/tmp/krb5cc_user"
  trace_level: 16  # Optional: 0-16, higher = more verbose
  trace_directory: "/tmp/oracle_trace"  # Optional

app_settings:
  report_output_dir: "reports"
  log_dir: "logs"
  log_level: "INFO"
  email_recipients: ["security@example.com", "soc@example.com"]

user_settings:
  sid: "A12345"  # User's SID for audit trail only
```

#### 2. Database Configuration (`configs/databases.yaml`)

This file defines target databases and their queries:

```yaml
databases:
  - name: client_activity_analysis
    host: oracle.client.example.com
    port: 6036  # Custom Oracle port
    service_name: CLIENT_AUDIT
    default_schema: "audit_logs"
    sql_queries:
      - name: "Get all email changes"
        query_location: "queries/get_all_email_changes.sql"
      - name: "Get phone changes by client ID"
        query_location: "queries/get_phone_changes_by_client_id.sql"
        parameters:  # Optional parameters
          client_id: 12345
      - name: "Get token changes"
        query_location: "queries/get_token_changes.sql"
        
  - name: account_activity_analysis
    host: oracle.account.example.com
    port: 6036
    service_name: ACCOUNT_AUDIT
    default_schema: "audit_logs"
    sql_queries:
      - name: "Get all password changes"
        query_location: "queries/get_all_password_changes.sql"
```

### Configuration Parameters Explained

#### Oracle Client Settings

- **instant_client_dir**: Path to Oracle Instant Client installation
- **krb5_conf**: Path to Kerberos configuration file
- **krb5_cache**: Path to Kerberos credential cache
- **trace_level**: (Optional) Oracle trace verbosity (0-16)
- **trace_directory**: (Optional) Where to store trace files

#### Database Settings

- **name**: Unique identifier for the database
- **host**: Database hostname or IP
- **port**: Oracle listener port (default: 1521)
- **service_name**: Oracle service name
- **default_schema**: Schema to set upon connection
- **sql_queries**: List of queries to execute

## Usage Guide

### Basic Usage

#### 1. Direct Connection

```python
from ez_connect_oracle import OracleKerberosConnection

# Create connection instance
conn = OracleKerberosConnection(
    host="oracle.example.com",
    port=6036,
    service_name="AUDIT_DB",
    instant_client_dir="/opt/oracle/instantclient",
    krb5_conf="/etc/krb5.conf",
    krb5_cache="/tmp/krb5cc_user",
    default_schema="audit_logs"
)

# Connect and execute query
try:
    conn.connect()
    results = conn.execute_query("SELECT * FROM audit_log WHERE rownum <= 10")
    for row in results:
        print(row)
finally:
    conn.close()
```

#### 2. Using Context Manager

```python
from ez_connect_oracle import OracleKerberosConnection

connection_params = {
    "host": "oracle.example.com",
    "port": 6036,
    "service_name": "AUDIT_DB",
    "instant_client_dir": "/opt/oracle/instantclient",
    "krb5_conf": "/etc/krb5.conf",
    "krb5_cache": "/tmp/krb5cc_user",
    "default_schema": "audit_logs"
}

with OracleKerberosConnection(**connection_params) as conn:
    results = conn.execute_query("SELECT sysdate FROM dual")
    print(f"Current database time: {results[0]['SYSDATE']}")
```

#### 3. Loading from Configuration Files

```python
import yaml
from pathlib import Path
from ez_connect_oracle import OracleKerberosConnection

# Load configurations
with open('configs/user_config.yaml', 'r') as f:
    user_config = yaml.safe_load(f)

with open('configs/databases.yaml', 'r') as f:
    db_config = yaml.safe_load(f)

# Process each database
for db in db_config['databases']:
    conn = OracleKerberosConnection(
        host=db['host'],
        port=db['port'],
        service_name=db['service_name'],
        instant_client_dir=user_config['oracle_client']['instant_client_dir'],
        krb5_conf=user_config['oracle_client']['krb5_conf'],
        krb5_cache=user_config['oracle_client']['krb5_cache'],
        default_schema=db.get('default_schema'),
        trace_level=user_config['oracle_client'].get('trace_level'),
        trace_directory=user_config['oracle_client'].get('trace_directory')
    )
    
    with conn:
        print(f"Connected to {db['name']}")
        
        # Execute each query
        for query_def in db['sql_queries']:
            # Load SQL from file
            sql_path = Path(query_def['query_location'])
            sql = sql_path.read_text()
            
            # Execute query
            results = conn.execute_query(sql, query_def.get('parameters'))
            print(f"{query_def['name']}: {len(results)} rows returned")
```

### Advanced Usage

#### 1. Connection Pooling

```python
from ez_connect_oracle import OracleKerberosConnection
import concurrent.futures

# Create connection manager
conn_manager = OracleKerberosConnection(
    host="oracle.example.com",
    port=6036,
    service_name="AUDIT_DB",
    instant_client_dir="/opt/oracle/instantclient",
    krb5_conf="/etc/krb5.conf",
    krb5_cache="/tmp/krb5cc_user"
)

# Create connection pool
pool = conn_manager.create_connection_pool(
    min_size=2,
    max_size=10,
    increment=1,
    timeout=60
)

def process_query(query):
    """Process a single query using pooled connection"""
    conn = conn_manager.get_connection_from_pool()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
    finally:
        conn_manager.release_connection_to_pool(conn)

# Execute queries concurrently
queries = [
    "SELECT count(*) FROM audit_log WHERE action = 'LOGIN'",
    "SELECT count(*) FROM audit_log WHERE action = 'LOGOUT'",
    "SELECT count(*) FROM audit_log WHERE action = 'CHANGE_PASSWORD'"
]

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(process_query, queries))
    
# Close pool when done
conn_manager.close()
```

#### 2. Transaction Management

```python
with OracleKerberosConnection(**connection_params) as conn:
    try:
        # Start transaction
        conn.begin_transaction()
        
        # Multiple operations
        conn.execute_query(
            "INSERT INTO audit_summary (date, total_events) VALUES (:1, :2)",
            {'1': datetime.now(), '2': 1000}
        )
        
        conn.execute_query(
            "UPDATE audit_stats SET last_run = SYSDATE WHERE job_name = :1",
            {'1': 'daily_summary'}
        )
        
        # Commit if all successful
        conn.commit()
        print("Transaction committed successfully")
        
    except Exception as e:
        # Rollback on error
        conn.rollback()
        print(f"Transaction rolled back due to: {e}")
        raise
```

#### 3. Batch Operations

```python
with OracleKerberosConnection(**connection_params) as conn:
    # Prepare batch data
    audit_records = [
        {'user_id': 'USER001', 'action': 'LOGIN', 'timestamp': datetime.now()},
        {'user_id': 'USER002', 'action': 'LOGOUT', 'timestamp': datetime.now()},
        {'user_id': 'USER003', 'action': 'CHANGE_PASSWORD', 'timestamp': datetime.now()}
    ]
    
    # Execute batch insert
    rows_affected = conn.execute_many(
        "INSERT INTO audit_log (user_id, action, timestamp) VALUES (:user_id, :action, :timestamp)",
        audit_records
    )
    
    conn.commit()
    print(f"Inserted {rows_affected} audit records")
```

## API Reference

### Class: OracleKerberosConnection

#### Constructor

```python
OracleKerberosConnection(
    host: str,
    port: int,
    service_name: str,
    instant_client_dir: Union[str, Path],
    krb5_conf: Union[str, Path],
    krb5_cache: Union[str, Path],
    default_schema: Optional[str] = None,
    trace_level: Optional[int] = None,
    trace_directory: Optional[Union[str, Path]] = None,
    log_level: int = logging.INFO
)
```

#### Methods

##### Connection Management

- **connect()**: Establish database connection
- **close()**: Close database connection
- **ensure_connection()**: Check and reconnect if necessary
- **create_connection_pool()**: Create a connection pool
- **get_connection_from_pool()**: Get connection from pool
- **release_connection_to_pool()**: Return connection to pool

##### Query Execution

- **execute_query(sql, params)**: Execute SELECT query
- **execute_many(sql, params)**: Execute batch operations
- **set_current_schema(schema)**: Change current schema
- **get_current_schema()**: Get current schema name

##### Transaction Management

- **begin_transaction()**: Start transaction
- **commit()**: Commit transaction
- **rollback()**: Rollback transaction

##### Factory Methods

- **from_config_file(config_file)**: Create instance from JSON config

## Examples

### Example 1: Security Audit Report

```python
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from ez_connect_oracle import OracleKerberosConnection

def generate_security_audit_report(days_back=7):
    """Generate security audit report for the last N days"""
    
    # Load configurations
    with open('configs/user_config.yaml', 'r') as f:
        user_config = yaml.safe_load(f)
    
    with open('configs/databases.yaml', 'r') as f:
        db_config = yaml.safe_load(f)
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    report_data = {}
    
    # Process each database
    for db in db_config['databases']:
        db_name = db['name']
        report_data[db_name] = {}
        
        # Create connection
        conn = OracleKerberosConnection(
            host=db['host'],
            port=db['port'],
            service_name=db['service_name'],
            instant_client_dir=user_config['oracle_client']['instant_client_dir'],
            krb5_conf=user_config['oracle_client']['krb5_conf'],
            krb5_cache=user_config['oracle_client']['krb5_cache'],
            default_schema=db.get('default_schema')
        )
        
        try:
            conn.connect()
            
            # Execute each query
            for query_def in db['sql_queries']:
                query_name = query_def['name']
                sql_file = Path(query_def['query_location'])
                
                # Read SQL template
                sql_template = sql_file.read_text()
                
                # Add date parameters if needed
                params = query_def.get('parameters', {})
                params.update({
                    'start_date': start_date,
                    'end_date': end_date
                })
                
                # Execute query
                results = conn.execute_query(sql_template, params)
                report_data[db_name][query_name] = {
                    'row_count': len(results),
                    'data': results
                }
                
                print(f"[{db_name}] {query_name}: {len(results)} records found")
                
        except Exception as e:
            print(f"Error processing {db_name}: {str(e)}")
            report_data[db_name]['error'] = str(e)
        finally:
            conn.close()
    
    # Save report
    output_dir = Path(user_config['app_settings']['report_output_dir'])
    output_dir.mkdir(exist_ok=True)
    
    report_file = output_dir / f"security_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    import json
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2, default=str)
    
    print(f"Report saved to: {report_file}")
    return report_data

# Run the report
if __name__ == "__main__":
    report = generate_security_audit_report(days_back=30)
```

### Example 2: Real-time Monitoring

```python
import time
import threading
from collections import deque
from datetime import datetime

class OracleActivityMonitor:
    """Real-time monitoring of database activity"""
    
    def __init__(self, connection_params, check_interval=60):
        self.connection_params = connection_params
        self.check_interval = check_interval
        self.activity_log = deque(maxlen=1000)
        self.running = False
        self.monitor_thread = None
        
    def start(self):
        """Start monitoring"""
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()
        print("Monitoring started")
        
    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("Monitoring stopped")
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        conn = OracleKerberosConnection(**self.connection_params)
        
        while self.running:
            try:
                # Ensure connection is active
                conn.ensure_connection()
                
                # Check for suspicious activities
                suspicious_query = """
                SELECT user_id, action, timestamp, details
                FROM audit_log
                WHERE timestamp > SYSDATE - INTERVAL '1' MINUTE
                  AND action IN ('FAILED_LOGIN', 'PRIVILEGE_ESCALATION', 'DATA_EXPORT')
                ORDER BY timestamp DESC
                """
                
                results = conn.execute_query(suspicious_query)
                
                if results:
                    for record in results:
                        self.activity_log.append({
                            'timestamp': datetime.now(),
                            'alert': 'SUSPICIOUS_ACTIVITY',
                            'details': record
                        })
                        print(f"ALERT: {record['action']} by {record['user_id']}")
                
                # Sleep before next check
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(self.check_interval)
        
        conn.close()
    
    def get_recent_alerts(self, minutes=10):
        """Get alerts from the last N minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [
            alert for alert in self.activity_log
            if alert['timestamp'] > cutoff_time
        ]

# Usage
monitor = OracleActivityMonitor(
    connection_params={
        'host': 'oracle.example.com',
        'port': 6036,
        'service_name': 'AUDIT_DB',
        'instant_client_dir': '/opt/oracle/instantclient',
        'krb5_conf': '/etc/krb5.conf',
        'krb5_cache': '/tmp/krb5cc_user'
    },
    check_interval=30  # Check every 30 seconds
)

monitor.start()
# Let it run for a while
time.sleep(300)
monitor.stop()
```

## Troubleshooting

### Common Issues

#### 1. Kerberos Authentication Failures

**Error**: `ORA-12638: Credential retrieval failed`

**Solutions**:

- Verify Kerberos ticket is valid: `klist`
- Renew ticket if expired: `kinit`
- Check krb5.conf path is correct
- Ensure krb5_cache file exists and is readable

#### 2. Oracle Client Initialization

**Error**: `DPI-1047: Cannot locate a 64-bit Oracle Client library`

**Solutions**:

- Verify instant_client_dir path is correct
- Check LD_LIBRARY_PATH includes instant client directory
- Ensure all required Oracle client files are present

#### 3. Connection Timeouts

**Error**: `ORA-12170: TNS:Connect timeout occurred`

**Solutions**:

- Verify network connectivity to database host
- Check if custom port (6036) is open
- Increase connection timeout in sqlnet.ora
- Check firewall rules

#### 4. Schema Access Issues

**Error**: `ORA-00942: table or view does not exist`

**Solutions**:

- Verify default_schema is set correctly
- Check user has privileges on the schema
- Use fully qualified table names (schema.table)

### Debug Mode

Enable detailed tracing for troubleshooting:

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create connection with trace enabled
conn = OracleKerberosConnection(
    host="oracle.example.com",
    port=6036,
    service_name="AUDIT_DB",
    instant_client_dir="/opt/oracle/instantclient",
    krb5_conf="/etc/krb5.conf",
    krb5_cache="/tmp/krb5cc_user",
    trace_level=16,  # Maximum trace level
    trace_directory="/tmp/oracle_trace",
    log_level=logging.DEBUG
)
```

## Best Practices

### 1. Configuration Management

- **Separate Concerns**: Keep user settings separate from database definitions
- **Use Environment Variables**: For sensitive data like credentials
- **Version Control**: Track configuration changes, but exclude sensitive data
- **Validate Configurations**: Always validate before using

```python
def validate_config(config):
    """Validate configuration before use"""
    required_fields = ['host', 'port', 'service_name']
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(config['port'], int) or config['port'] <= 0:
        raise ValueError("Port must be a positive integer")
```

### 2. Connection Management

- **Use Connection Pools**: For multi-threaded applications
- **Implement Retry Logic**: Handle transient failures
- **Monitor Connection Health**: Regular health checks
- **Clean Up Resources**: Always close connections

```python
class ManagedConnection:
    """Managed connection with retry and health checks"""
    
    def __init__(self, connection_params, max_retries=3):
        self.connection_params = connection_params
        self.max_retries = max_retries
        self.conn = None
        
    def get_connection(self):
        """Get connection with retry logic"""
        for attempt in range(self.max_retries):
            try:
                if not self.conn or not self.is_healthy():
                    self.conn = OracleKerberosConnection(**self.connection_params)
                    self.conn.connect()
                return self.conn
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def is_healthy(self):
        """Check if connection is healthy"""
        if not self.conn:
            return False
        try:
            self.conn.execute_query("SELECT 1 FROM DUAL")
            return True
        except:
            return False
```

### 3. Query Optimization

- **Use Bind Variables**: Prevent SQL injection and improve performance
- **Limit Result Sets**: Use ROWNUM or FETCH FIRST
- **Index Awareness**: Ensure queries use appropriate indexes
- **Monitor Performance**: Track query execution times

```python
def execute_query_with_metrics(conn, query_name, sql, params=None):
    """Execute query and collect metrics"""
    start_time = time.time()
    
    try:
        results = conn.execute_query(sql, params)
        execution_time = time.time() - start_time
        
        # Log metrics
        logging.info(f"Query: {query_name}")
        logging.info(f"Execution time: {execution_time:.2f}s")
        logging.info(f"Rows returned: {len(results)}")
        
        # Alert if slow
        if execution_time > 30:
            logging.warning(f"Slow query detected: {query_name} took {execution_time:.2f}s")
        
        return results
        
    except Exception as e:
        execution_time = time.time() - start_time
        logging.error(f"Query failed: {query_name} after {execution_time:.2f}s: {str(e)}")
        raise
```

### 4. Security Considerations

- **Never Store Passwords**: Use Kerberos or Oracle Wallets
- **Audit Connections**: Log all connection attempts
- **Principle of Least Privilege**: Use minimal required permissions
- **Encrypt Sensitive Data**: Use Oracle Native Network Encryption

```python
def create_secure_connection(user_config, db_config):
    """Create connection with security best practices"""
    
    # Validate Kerberos ticket
    import subprocess
    try:
        result = subprocess.run(['klist'], capture_output=True, text=True)
        if 'No credentials cache found' in result.stderr:
            raise Exception("No valid Kerberos ticket found. Run 'kinit' first.")
    except Exception as e:
        logging.error(f"Kerberos validation failed: {e}")
        raise
    
    # Create connection with minimal logging of sensitive data
    conn = OracleKerberosConnection(
        host=db_config['host'],
        port=db_config['port'],
        service_name=db_config['service_name'],
        instant_client_dir=user_config['oracle_client']['instant_client_dir'],
        krb5_conf=user_config['oracle_client']['krb5_conf'],
        krb5_cache=user_config['oracle_client']['krb5_cache'],
        default_schema=db_config.get('default_schema')
    )
    
    # Log connection attempt (without sensitive details)
    logging.info(f"Attempting connection to {db_config['name']} as Kerberos principal")
    
    return conn
```

### 5. Error Handling

- **Specific Exception Handling**: Catch specific Oracle errors
- **Graceful Degradation**: Continue processing other databases if one fails
- **Comprehensive Logging**: Log errors with context
- **User-Friendly Messages**: Translate technical errors

```python
def handle_oracle_errors(func):
    """Decorator for handling Oracle-specific errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except oracledb.DatabaseError as e:
            error_obj, = e.args
            if error_obj.code == 1017:
                raise Exception("Invalid username/password")
            elif error_obj.code == 12541:
                raise Exception("Database listener is not running")
            elif error_obj.code == 942:
                raise Exception("Table or view does not exist - check schema permissions")
            else:
                raise Exception(f"Database error: {error_obj.message}")
        except Exception as e:
            logging.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise
    return wrapper
```

## Conclusion

The `ez_connect_oracle.py` module provides a robust foundation for Oracle database connectivity with Kerberos authentication. By following this documentation and best practices, you can build secure, reliable, and maintainable database applications.

For additional support or contributions, please refer to the project repository.
