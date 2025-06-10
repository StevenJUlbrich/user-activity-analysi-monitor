# Step 0: Prerequisites and Oracle Connection Foundation

This step establishes the prerequisites and foundational components needed before implementing the Client Activity Monitor application.

## System Requirements

### 1. Environment Setup
- **Python**: 3.10 or higher (3.11+ recommended)
- **Operating System**: Linux/Unix (for Kerberos support)
- **Oracle Instant Client**: 19c or higher (23c recommended for full Kerberos support)
- **Kerberos**: Client utilities installed and configured

### 2. Python Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install oracledb pyyaml pydantic typing-extensions
```

### 3. Oracle Instant Client Installation
```bash
# Example for Linux (adjust for your system)
# Download from Oracle website
wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basic-linux.zip

# Extract to system location
sudo mkdir -p /opt/oracle
sudo unzip instantclient-basic-linux.zip -d /opt/oracle/

# Set environment variables (add to ~/.bashrc or ~/.bash_profile)
export LD_LIBRARY_PATH=/opt/oracle/instantclient_21_9:$LD_LIBRARY_PATH
export PATH=/opt/oracle/instantclient_21_9:$PATH
```

### 4. Kerberos Configuration
```bash
# Verify Kerberos is installed
which kinit klist

# Check for valid ticket
klist

# If no ticket, obtain one
kinit your_username@YOUR.DOMAIN.COM

# Verify ticket cache location
echo $KRB5CCNAME
```

## Project Structure Setup

Create the following directory structure:

```
client_activity_monitor/
├── .claude/
│   ├── context/
│   │   ├── ez_connect_oracle.py         # Oracle connection module
│   │   └── ez_connect_oracle_documentation/
│   └── instructions/
│       └── step_0.md                    # This file
├── configs/
│   ├── user_config.yaml               # User-specific settings
│   └── databases.yaml                  # Database definitions
├── queries/                            # SQL query files
│   ├── get_all_email_changes.sql
│   ├── get_phone_changes_by_client_id.sql
│   ├── get_token_changes.sql
│   └── get_all_password_changes.sql
├── logs/                               # Application logs
├── reports/                            # Generated reports
└── src/                                # Application source code
```

## Core Module Integration

### 1. Copy the Oracle Connection Module

Copy the `ez_connect_oracle.py` module from the context folder to your project:

```bash
# From project root
cp .claude/context/ez_connect_oracle.py src/
```

### 2. Create Initial Configuration Files

#### configs/user_config.yaml
```yaml
oracle_client:
  instant_client_dir: "/opt/oracle/instantclient_21_9"  # Update with your path
  krb5_conf: "/etc/krb5.conf"
  krb5_cache: "/tmp/krb5cc_${UID}"  # Will use your user's ticket cache
  trace_level: 0  # Set to 16 for debugging
  trace_directory: "/tmp/oracle_trace"

app_settings:
  report_output_dir: "reports"
  log_dir: "logs"
  log_level: "INFO"
  email_recipients: ["security@example.com", "soc@example.com"]

user_settings:
  sid: "A12345"  # Your SID for audit trail only
```

#### configs/databases.yaml
```yaml
databases:
  - name: client_activity_analysis
    host: oracle.client.example.com
    port: 6036  # Custom Oracle port
    service_name: CLIENT_AUDIT
    default_schema: "event_logs"
    sql_queries:
      - name: "Get all email changes"
        query_location: "queries/get_all_email_changes.sql"
      - name: "Get phone changes by client ID"
        query_location: "queries/get_phone_changes_by_client_id.sql"
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

### 3. Create Sample SQL Query Files

#### queries/get_all_email_changes.sql
```sql
SELECT 
    user_id,
    old_email,
    new_email,
    change_date,
    changed_by,
    change_reason
FROM event_logs.email_changes
WHERE change_date >= :end_date
ORDER BY change_date DESC
```

#### queries/get_phone_changes_by_client_id.sql
```sql
SELECT 
    user_id,
    old_phone,
    new_phone,
    phone_type,
    change_date,
    changed_by
FROM event_logs.phone_changes
WHERE change_date >= :end_date
ORDER BY change_date DESC
```

#### queries/get_token_changes.sql
```sql
SELECT 
    user_id,
    token_type,
    action,
    action_date,
    performed_by,
    ip_address
FROM event_logs.token_changes
WHERE action_date >= :end_date
  AND action IN ('CREATED', 'REVOKED', 'EXPIRED')
ORDER BY action_date DESC
```

#### queries/get_all_password_changes.sql
```sql
SELECT 
    user_id,
    change_date,
    change_type,
    change_source,
    ip_address,
    user_agent
FROM audit_logs.password_changes
WHERE change_date >= :end_date
ORDER BY change_date DESC
```

## Validation Script

Create a validation script to test the setup:

#### src/validate_setup.py
```python
#!/usr/bin/env python3
"""Validate the Oracle connection setup and prerequisites"""

import os
import sys
import subprocess
import yaml
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} - Need 3.10+")
        return False

def check_oracle_client(instant_client_dir):
    """Check Oracle Instant Client installation"""
    client_path = Path(instant_client_dir)
    if client_path.exists() and client_path.is_dir():
        print(f"✓ Oracle Instant Client found: {instant_client_dir}")
        return True
    else:
        print(f"✗ Oracle Instant Client not found: {instant_client_dir}")
        return False

def check_kerberos():
    """Check Kerberos setup"""
    try:
        result = subprocess.run(['klist'], capture_output=True, text=True)
        if result.returncode == 0 and 'Default principal:' in result.stdout:
            print("✓ Kerberos ticket found")
            return True
        else:
            print("✗ No valid Kerberos ticket - run 'kinit'")
            return False
    except FileNotFoundError:
        print("✗ Kerberos not installed")
        return False

def check_python_packages():
    """Check required Python packages"""
    required = ['oracledb', 'yaml', 'pydantic']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✓ {package} installed")
        except ImportError:
            print(f"✗ {package} not installed")
            missing.append(package)
    
    return len(missing) == 0

def check_configurations():
    """Check configuration files"""
    config_files = [
        'configs/user_config.yaml',
        'configs/databases.yaml'
    ]
    
    all_valid = True
    for config_file in config_files:
        if Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    yaml.safe_load(f)
                print(f"✓ {config_file} valid")
            except Exception as e:
                print(f"✗ {config_file} invalid: {e}")
                all_valid = False
        else:
            print(f"✗ {config_file} not found")
            all_valid = False
    
    return all_valid

def check_directories():
    """Check required directories exist"""
    dirs = ['queries', 'logs', 'reports', 'src']
    for dir_name in dirs:
        if Path(dir_name).exists():
            print(f"✓ {dir_name}/ directory exists")
        else:
            print(f"✗ {dir_name}/ directory missing")
            Path(dir_name).mkdir(exist_ok=True)
            print(f"  → Created {dir_name}/")

def main():
    """Run all validation checks"""
    print("Client Activity Monitor - Setup Validation")
    print("=" * 50)
    
    # Load user config
    try:
        with open('configs/user_config.yaml', 'r') as f:
            user_config = yaml.safe_load(f)
        instant_client_dir = user_config['oracle_client']['instant_client_dir']
    except Exception as e:
        print(f"Cannot read user_config.yaml: {e}")
        instant_client_dir = "/opt/oracle/instantclient"
    
    print("\n1. Checking Python version...")
    check_python_version()
    
    print("\n2. Checking Oracle Instant Client...")
    check_oracle_client(instant_client_dir)
    
    print("\n3. Checking Kerberos...")
    check_kerberos()
    
    print("\n4. Checking Python packages...")
    check_python_packages()
    
    print("\n5. Checking configuration files...")
    check_configurations()
    
    print("\n6. Checking directories...")
    check_directories()
    
    print("\n" + "=" * 50)
    print("Validation complete!")

if __name__ == "__main__":
    main()
```

## Connection Test Script

Create a simple test to verify Oracle connectivity:

#### src/test_connection.py
```python
#!/usr/bin/env python3
"""Test Oracle database connection"""

import yaml
import logging
from pathlib import Path
from ez_connect_oracle import OracleKerberosConnection

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_database_connection(db_config, oracle_config):
    """Test connection to a single database"""
    print(f"\nTesting connection to: {db_config['name']}")
    print("-" * 40)
    
    try:
        # Create connection
        conn = OracleKerberosConnection(
            host=db_config['host'],
            port=db_config['port'],
            service_name=db_config['service_name'],
            instant_client_dir=oracle_config['instant_client_dir'],
            krb5_conf=oracle_config['krb5_conf'],
            krb5_cache=oracle_config['krb5_cache'],
            default_schema=db_config.get('default_schema')
        )
        
        # Connect
        conn.connect()
        print("✓ Connection established")
        
        # Test query
        results = conn.execute_query("SELECT SYSDATE FROM DUAL")
        print(f"✓ Database time: {results[0]['SYSDATE']}")
        
        # Check schema
        if db_config.get('default_schema'):
            schema = conn.get_current_schema()
            print(f"✓ Current schema: {schema}")
        
        # Close connection
        conn.close()
        print("✓ Connection closed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
        return False

def main():
    """Test all configured database connections"""
    # Load configurations
    with open('configs/user_config.yaml', 'r') as f:
        user_config = yaml.safe_load(f)
    
    with open('configs/databases.yaml', 'r') as f:
        db_config = yaml.safe_load(f)
    
    oracle_config = user_config['oracle_client']
    
    print("Oracle Connection Test")
    print("=" * 50)
    
    # Test each database
    success_count = 0
    for db in db_config['databases']:
        if test_database_connection(db, oracle_config):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"Results: {success_count}/{len(db_config['databases'])} connections successful")

if __name__ == "__main__":
    main()
```

## Next Steps

After completing this setup:

1. Run the validation script: `python src/validate_setup.py`
2. Test database connections: `python src/test_connection.py`
3. Update configuration files with your actual database details
4. Ensure all SQL query files match your database schema
5. Proceed to Step 1 for application implementation

## Troubleshooting

### Common Issues

1. **Oracle Client Not Found**
   - Verify installation path in user_config.yaml
   - Check LD_LIBRARY_PATH environment variable
   - Ensure all Oracle client files are present

2. **Kerberos Authentication Failed**
   - Run `kinit` to obtain ticket
   - Verify krb5.conf path is correct
   - Check ticket cache permissions

3. **Connection Timeout**
   - Verify network connectivity to database
   - Check firewall rules for port 6036
   - Confirm database service name is correct

4. **Module Import Errors**
   - Ensure virtual environment is activated
   - Reinstall packages: `pip install -r requirements.txt`
   - Verify ez_connect_oracle.py is in src/

## Security Notes

- Never commit credentials to version control
- Use `.gitignore` to exclude sensitive files
- Ensure proper file permissions on configuration files
- Regular Kerberos ticket renewal for automated processes