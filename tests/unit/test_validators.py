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
            
    def test_validate_email_list_valid(self):
        """Test valid email lists."""
        valid_lists = [
            ["test@example.com"],
            ["user1@domain.com", "user2@domain.org"],
            ["security@company.com", "soc-team@company.com"],
        ]
        for email_list in valid_lists:
            is_valid, error = Validators.validate_email_list(email_list)
            assert is_valid is True
            assert error is None
            
    def test_validate_email_list_invalid(self):
        """Test invalid email lists."""
        invalid_lists = [
            [],  # Empty list
            ["not-an-email"],  # Missing @
            ["user@"],  # Missing domain
            ["@domain.com"],  # Missing user
            ["user@domain"],  # Missing TLD
            ["user@domain.c"],  # TLD too short
        ]
        for email_list in invalid_lists:
            is_valid, error = Validators.validate_email_list(email_list)
            assert is_valid is False
            assert error is not None