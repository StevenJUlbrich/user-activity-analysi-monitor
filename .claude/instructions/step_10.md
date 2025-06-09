# Step 10: Validation, Error Handling, and Testing

## Objective
Implement comprehensive validation, error handling, and testing strategies to ensure the application is robust and user-friendly.

## A. Input Validation

### 1. Configuration Panel Validation

Create `src/client_activity_monitor/common/validators.py`:

```python
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
```

### 2. Configuration Panel with Validation

Update configuration panel to use validators:

```python
class ConfigurationPanel(ctk.CTkFrame):
    def _on_save(self):
        """Handle Save Config button click with validation."""
        # Get values
        oracle_path = self.oracle_path_entry.get().strip()
        krb5_config = self.krb5_config_entry.get().strip()
        krb5_cache = self.krb5_cache_entry.get().strip()
        sid = self.sid_entry.get().strip()
        
        # Validate each field
        validators = [
            (Validators.validate_oracle_client_path(oracle_path), "Oracle Client Path"),
            (Validators.validate_krb5_config(krb5_config), "KRB5 Config"),
            (Validators.validate_krb5_cache(krb5_cache), "KRB5 Cache"),
            (Validators.validate_sid(sid), "User SID")
        ]
        
        # Check all validations
        for (is_valid, error_msg), field_name in validators:
            if not is_valid:
                self._show_error(f"{field_name}: {error_msg}")
                return
                
        # All valid, proceed with save
        config_data = {
            'oracle_client_path': oracle_path,
            'krb5_config_path': krb5_config,
            'krb5_cache_path': krb5_cache,
            'user_sid': sid
        }
        
        try:
            success, error_msg = self.save_callback(config_data)
            if success:
                self._show_success("Configuration saved successfully")
            else:
                self._show_error(f"Failed to save: {error_msg}")
        except Exception as e:
            self._show_error(f"Unexpected error: {str(e)}")
```

## B. Error Handling Strategy

### 1. Custom Exception Classes

Create `src/client_activity_monitor/common/exceptions.py`:

```python
class ClientActivityMonitorError(Exception):
    """Base exception for application errors."""
    pass

class ConfigurationError(ClientActivityMonitorError):
    """Configuration-related errors."""
    pass

class DatabaseConnectionError(ClientActivityMonitorError):
    """Database connection errors."""
    pass

class QueryExecutionError(ClientActivityMonitorError):
    """Query execution errors."""
    pass

class ReportGenerationError(ClientActivityMonitorError):
    """Report generation errors."""
    pass

class ExternalIntegrationError(ClientActivityMonitorError):
    """Email/OneNote integration errors."""
    pass
```

### 2. Error Handler Decorator

Create `src/client_activity_monitor/common/error_handler.py`:

```python
from functools import wraps
from loguru import logger
import traceback

def handle_errors(error_callback=None, log_errors=True):
    """
    Decorator for consistent error handling.
    
    Args:
        error_callback: Function to call on error (e.g., show UI message)
        log_errors: Whether to log errors
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                    logger.debug(traceback.format_exc())
                    
                if error_callback:
                    error_callback(str(e))
                    
                # Re-raise if it's a critical error
                if isinstance(e, (SystemExit, KeyboardInterrupt)):
                    raise
                    
                return None
        return wrapper
    return decorator
```

### 3. Controller Error Handling

```python
class MainController:
    @handle_errors(log_errors=True)
    def on_run_report(self, last_event_time_str: str):
        """Handle Run Report with comprehensive error handling."""
        try:
            # Validate inputs
            is_valid, error_msg = Validators.validate_datetime(last_event_time_str)
            if not is_valid:
                self.show_error("Invalid Input", error_msg)
                return
                
            # Check configuration
            if not self.config_manager.config_exists():
                raise ConfigurationError("No configuration found. Please configure settings first.")
                
            # Validate databases configured
            databases = self.config_manager.get_all_databases()
            if not databases:
                raise ConfigurationError("No databases configured")
                
            # Start analysis
            self._start_analysis(last_event_time_str)
            
        except ConfigurationError as e:
            self.log_error(f"Configuration Error: {e}")
            self.show_error("Configuration Error", str(e))
        except Exception as e:
            self.log_error(f"Unexpected error: {e}")
            self.show_error("Error", "An unexpected error occurred. Check logs for details.")
```

## C. Testing Strategy

### 1. Unit Tests Structure

Create test directory structure:
```
tests/
├── unit/
│   ├── test_validators.py
│   ├── test_config_manager.py
│   ├── test_query_repository.py
│   ├── test_merge_filter_service.py
│   └── test_report_generator.py
├── integration/
│   ├── test_database_executor.py
│   └── test_end_to_end.py
└── fixtures/
    ├── sample_config.yaml
    └── sample_data.py
```

### 2. Unit Test Examples

Create `tests/unit/test_validators.py`:

```python
import pytest
from client_activity_monitor.common.validators import Validators

class TestValidators:
    """Test validation functions."""
    
    def test_validate_sid_valid(self):
        """Test valid SID formats."""
        valid_sids = ["A12345", "USER01", "TEST123"]
        for sid in valid_sids:
            is_valid, error = Validators.validate_sid(sid)
            assert is_valid is True
            assert error is None
            
    def test_validate_sid_invalid(self):
        """Test invalid SID formats."""
        invalid_sids = [
            "",  # Empty
            "A1",  # Too short
            "A12345678901",  # Too long
            "A-1234",  # Invalid character
            "123 45",  # Space
        ]
        for sid in invalid_sids:
            is_valid, error = Validators.validate_sid(sid)
            assert is_valid is False
            assert error is not None
            
    def test_validate_datetime_valid(self):
        """Test valid datetime formats."""
        valid_dates = [
            "2024-01-15 14:30",
            "2023-12-31 23:59",
            "2024-02-29 00:00",  # Leap year
        ]
        for date_str in valid_dates:
            is_valid, error = Validators.validate_datetime(date_str)
            assert is_valid is True
            assert error is None
            
    def test_validate_datetime_invalid(self):
        """Test invalid datetime formats."""
        invalid_dates = [
            "",  # Empty
            "2024/01/15 14:30",  # Wrong separator
            "15-01-2024 14:30",  # Wrong order
            "2024-13-01 14:30",  # Invalid month
            "2024-01-15",  # Missing time
        ]
        for date_str in invalid_dates:
            is_valid, error = Validators.validate_datetime(date_str)
            assert is_valid is False
            assert error is not None
```

### 3. Mock Testing for Database Operations

Create `tests/unit/test_query_repository.py`:

```python
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime
from client_activity_monitor.model.repositories.query_repository import QueryRepository

class TestQueryRepository:
    """Test QueryRepository with mocked database connection."""
    
    @patch('client_activity_monitor.model.repositories.query_repository.OracleKerberosConnection')
    def test_successful_connection(self, mock_oracle_class):
        """Test successful database connection."""
        # Setup mock
        mock_connection = Mock()
        mock_oracle_class.return_value = mock_connection
        
        # Test
        repo = QueryRepository({'host': 'test'}, 'TEST_DB')
        result = repo.connect()
        
        # Verify
        assert result is True
        mock_connection.connect.assert_called_once()
        
    @patch('client_activity_monitor.model.repositories.query_repository.OracleKerberosConnection')
    def test_query_execution(self, mock_oracle_class):
        """Test query execution returns DataFrame."""
        # Setup mock
        mock_connection = Mock()
        mock_connection.execute_query.return_value = [
            {'user_id': 'user1', 'change_timestamp': '2024-01-15 10:00:00'},
            {'user_id': 'user2', 'change_timestamp': '2024-01-15 11:00:00'}
        ]
        mock_oracle_class.return_value = mock_connection
        
        # Test
        repo = QueryRepository({'host': 'test'}, 'TEST_DB')
        repo.connection = mock_connection
        
        with patch('builtins.open', MagicMock()):
            with patch('pathlib.Path.exists', return_value=True):
                df = repo.execute_query(
                    'Test Query',
                    'test.sql',
                    datetime(2024, 1, 1)
                )
        
        # Verify
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert 'user_id' in df.columns
```

### 4. Integration Test Example

Create `tests/integration/test_end_to_end.py`:

```python
import pytest
from datetime import datetime, timedelta
import pandas as pd
from client_activity_monitor.model.services.merge_filter_service import MergeFilterService

class TestEndToEnd:
    """Integration tests for complete workflow."""
    
    def test_merge_filter_workflow(self):
        """Test merging and filtering with sample data."""
        # Create sample data
        last_event_time = datetime(2024, 1, 15, 14, 0)
        window_start = last_event_time - timedelta(hours=24)
        
        # Sample results from multiple databases
        database_results = {
            "client_activity_analysis": {
                "Get all email changes": pd.DataFrame({
                    'user_id': ['user1', 'user2', 'user3'],
                    'change_timestamp': [
                        last_event_time - timedelta(hours=2),
                        last_event_time - timedelta(hours=3),
                        last_event_time - timedelta(hours=25)  # Outside window
                    ]
                }),
                "Get phone changes by client ID": pd.DataFrame({
                    'user_id': ['user1', 'user2'],
                    'change_timestamp': [
                        last_event_time - timedelta(hours=1),
                        last_event_time - timedelta(hours=2)
                    ]
                }),
                "Get token changes": pd.DataFrame({
                    'user_id': ['user1', 'user2'],
                    'change_timestamp': [
                        last_event_time - timedelta(hours=3),
                        last_event_time - timedelta(hours=4)
                    ]
                })
            },
            "account_activity_analysis": {
                "Get all password changes": pd.DataFrame({
                    'user_id': ['user1', 'user2', 'user4'],
                    'change_timestamp': [
                        last_event_time - timedelta(hours=4),
                        last_event_time - timedelta(hours=5),
                        last_event_time - timedelta(hours=1)  # user4 missing other changes
                    ]
                })
            }
        }
        
        # Test merge/filter
        service = MergeFilterService()
        result = service.process_results(database_results, last_event_time)
        
        # Verify results
        assert len(result) == 2  # Only user1 and user2 qualify
        assert set(result['user_id']) == {'user1', 'user2'}
        
        # Verify columns exist
        expected_columns = [
            'user_id',
            'password_change_time',
            'email_change_time',
            'phone_change_time',
            'token_change_time'
        ]
        for col in expected_columns:
            assert col in result.columns
```

## D. Error Recovery Strategies

### 1. Database Connection Recovery

```python
class QueryRepository:
    def execute_query_with_retry(self, query_name: str, sql_file: str, 
                                 start_date: datetime, max_retries: int = 3):
        """Execute query with automatic retry on connection failure."""
        for attempt in range(max_retries):
            try:
                if not self.connection:
                    self.connect()
                    
                return self.execute_query(query_name, sql_file, start_date)
                
            except DatabaseConnectionError as e:
                logger.warning(f"Connection failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    self.connection = None  # Force reconnection
                else:
                    raise
```

### 2. Partial Result Handling

```python
class DatabaseExecutor:
    def execute_all_databases(self, start_date, progress_callback, cancel_event):
        """Execute with graceful handling of partial failures."""
        results = {}
        failed_databases = []
        
        # ... execution logic ...
        
        # After execution, check if we have minimum required data
        if not results:
            raise QueryExecutionError("All database queries failed")
            
        if failed_databases:
            logger.warning(f"Partial failure: {len(failed_databases)} databases failed")
            # Continue with available results
            
        return results
```

## E. User-Friendly Error Messages

Create a mapping of technical errors to user-friendly messages:

```python
ERROR_MESSAGES = {
    "ORA-01017": "Invalid username/password. Please check your credentials.",
    "ORA-12154": "Cannot find database. Please check your database configuration.",
    "ORA-12170": "Connection timeout. Please check network connectivity.",
    "Kerberos": "Kerberos authentication failed. Please run 'kinit' and try again.",
    "Permission denied": "Access denied. Please check file permissions.",
    "No such file": "Configuration file not found. Please check the path.",
}

def get_user_friendly_error(technical_error: str) -> str:
    """Convert technical error to user-friendly message."""
    for key, message in ERROR_MESSAGES.items():
        if key in technical_error:
            return message
    return "An unexpected error occurred. Please check the logs for details."
```

## F. Testing Checklist

### Unit Tests:
- [ ] All validators tested with valid/invalid inputs
- [ ] ConfigManager save/load operations
- [ ] Query execution with mocked database
- [ ] Merge/filter logic with various data scenarios
- [ ] Report generation with empty/full data

### Integration Tests:
- [ ] Full workflow with mocked databases
- [ ] Error scenarios (connection failure, invalid data)
- [ ] Cancellation at various stages
- [ ] Configuration changes between runs

### Manual Testing:
- [ ] All UI validation messages appear correctly
- [ ] Error dialogs show appropriate messages
- [ ] Log panel shows all operations
- [ ] Database status updates correctly
- [ ] Report actions enable/disable properly
- [ ] Clipboard operations work
- [ ] Email client opens with correct data

## Next Step
After implementing validation, error handling, and testing, proceed to Step 11: Documentation & Polish.