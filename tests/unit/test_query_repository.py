import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime
from client_activity_monitor.model.repositories.query_repository import QueryRepository

class TestQueryRepository:
    """Test QueryRepository with mocked database connection."""
    
    @patch('client_activity_monitor.model.repositories.ez_connect_oracle.EZConnectOracle')
    def test_successful_connection(self, mock_oracle_class):
        """Test successful database connection."""
        # Setup mock
        mock_connection = Mock()
        mock_oracle_class.return_value = mock_connection
        
        # Test
        repo = QueryRepository(
            db_config={
                'host': 'test_host',
                'port': 1521,
                'service_name': 'TEST_SERVICE'
            },
            db_name='TEST_DB'
        )
        result = repo.connect()
        
        # Verify
        assert result is True
        mock_connection.connect.assert_called_once()
        
    @patch('client_activity_monitor.model.repositories.ez_connect_oracle.EZConnectOracle')
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
        repo = QueryRepository(
            db_config={
                'host': 'test_host',
                'port': 1521,
                'service_name': 'TEST_SERVICE'
            },
            db_name='TEST_DB'
        )
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
        
    @patch('client_activity_monitor.model.repositories.ez_connect_oracle.EZConnectOracle')
    def test_connection_failure(self, mock_oracle_class):
        """Test handling of connection failure."""
        # Setup mock to raise exception
        mock_connection = Mock()
        mock_connection.connect.side_effect = Exception("Connection failed")
        mock_oracle_class.return_value = mock_connection
        
        # Test
        repo = QueryRepository(
            db_config={
                'host': 'test_host',
                'port': 1521,
                'service_name': 'TEST_SERVICE'
            },
            db_name='TEST_DB'
        )
        
        # Should return False on connection failure
        result = repo.connect()
        assert result is False
        
    def test_invalid_sql_file(self):
        """Test handling of missing SQL file."""
        repo = QueryRepository(
            db_config={
                'host': 'test_host',
                'port': 1521,
                'service_name': 'TEST_SERVICE'
            },
            db_name='TEST_DB'
        )
        
        # Mock connection
        repo.connection = Mock()
        
        # Test with non-existent file
        with patch('pathlib.Path.exists', return_value=False):
            with pytest.raises(FileNotFoundError):
                repo.execute_query(
                    'Test Query',
                    'non_existent.sql',
                    datetime(2024, 1, 1)
                )