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
        'configs/app_settings.yaml',
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
        with open('configs/app_settings.yaml', 'r') as f:
            user_config = yaml.safe_load(f)
        instant_client_dir = user_config['oracle_client']['instant_client_dir']
    except Exception as e:
        print(f"Cannot read app_settings.yaml: {e}")
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