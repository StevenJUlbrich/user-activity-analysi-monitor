from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional
import re

class Validators:
    """Common validation functions for the application."""
    
    @staticmethod
    def validate_oracle_client_path(path: str) -> Tuple[bool, Optional[str]]:
        """Validate Oracle Instant Client directory."""
        if not path:
            return False, "Oracle Client Path is required"
            
        path_obj = Path(path)
        if not path_obj.exists():
            return False, f"Path does not exist: {path}"
            
        if not path_obj.is_dir():
            return False, "Oracle Client Path must be a directory"
            
        # Check for expected Oracle client files
        expected_files = ['oci.dll', 'libclntsh.so', 'libclntsh.dylib']
        if not any((path_obj / f).exists() for f in expected_files):
            # Just warn, don't fail - different OS have different files
            pass
            
        return True, None
        
    @staticmethod
    def validate_krb5_config(path: str) -> Tuple[bool, Optional[str]]:
        """Validate Kerberos configuration file."""
        if not path:
            return False, "KRB5 Config Path is required"
            
        path_obj = Path(path)
        if not path_obj.exists():
            return False, f"File does not exist: {path}"
            
        if not path_obj.is_file():
            return False, "KRB5 Config must be a file"
            
        # Optionally check file content
        try:
            with open(path_obj, 'r') as f:
                content = f.read()
                if '[libdefaults]' not in content:
                    return False, "Invalid KRB5 config file (missing [libdefaults])"
        except Exception:
            return False, "Cannot read KRB5 config file"
            
        return True, None
        
    @staticmethod
    def validate_krb5_cache(path: str) -> Tuple[bool, Optional[str]]:
        """Validate Kerberos cache file path."""
        if not path:
            return False, "KRB5 Cache Path is required"
            
        # Cache file might not exist yet (created by kinit)
        # Just validate the directory exists
        path_obj = Path(path)
        parent_dir = path_obj.parent
        
        if not parent_dir.exists():
            return False, f"Directory does not exist: {parent_dir}"
            
        return True, None
        
    @staticmethod
    def validate_sid(sid: str) -> Tuple[bool, Optional[str]]:
        """Validate user SID format."""
        if not sid:
            return False, "User SID is required"
            
        # Example: SID should be alphanumeric, 5-10 characters
        if not re.match(r'^[A-Za-z0-9]{5,10}$', sid):
            return False, "SID must be 5-10 alphanumeric characters"
            
        return True, None
        
    @staticmethod
    def validate_datetime(datetime_str: str, format: str = "%Y-%m-%d %H:%M") -> Tuple[bool, Optional[str]]:
        """Validate datetime string format."""
        if not datetime_str:
            return False, "DateTime is required"
            
        try:
            datetime.strptime(datetime_str, format)
            return True, None
        except ValueError:
            return False, f"Invalid datetime format. Expected: {format}"
            
    @staticmethod
    def validate_email_list(emails: list) -> Tuple[bool, Optional[str]]:
        """Validate list of email addresses."""
        if not emails:
            return False, "At least one email recipient is required"
            
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        for email in emails:
            if not email_pattern.match(email.strip()):
                return False, f"Invalid email address: {email}"
                
        return True, None