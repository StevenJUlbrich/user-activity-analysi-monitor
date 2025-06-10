#!/usr/bin/env python3
"""Test Oracle database connection"""

import yaml
import logging
from pathlib import Path
from client_activity_monitor.model.repositories.ez_connect_oracle import OracleKerberosConnection

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
        # Create connection with proper parameter structure
        connection_params = {
            'host': db_config['host'],
            'port': db_config['port'],
            'service_name': db_config['service_name'],
            'default_schema': db_config.get('default_schema'),
            'oracle_client': oracle_config
        }
        
        conn = OracleKerberosConnection(connection_params)
        
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
    with open('configs/app_settings.yaml', 'r') as f:
        app_settings = yaml.safe_load(f)
    
    with open('configs/databases.yaml', 'r') as f:
        db_config = yaml.safe_load(f)
    
    oracle_config = app_settings['oracle_client']
    
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