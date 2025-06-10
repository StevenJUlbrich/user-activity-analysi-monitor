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
            
    def test_empty_results_handling(self):
        """Test handling of empty query results."""
        database_results = {
            "client_activity_analysis": {
                "Get all email changes": pd.DataFrame(),
                "Get phone changes by client ID": pd.DataFrame(),
                "Get token changes": pd.DataFrame()
            },
            "account_activity_analysis": {
                "Get all password changes": pd.DataFrame()
            }
        }
        
        service = MergeFilterService()
        result = service.process_results(
            database_results, 
            datetime(2024, 1, 15, 14, 0)
        )
        
        # Should return empty DataFrame
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        
    def test_partial_results_handling(self):
        """Test handling when some users have incomplete change sets."""
        last_event_time = datetime(2024, 1, 15, 14, 0)
        
        database_results = {
            "client_activity_analysis": {
                "Get all email changes": pd.DataFrame({
                    'user_id': ['user1', 'user2', 'user3'],
                    'change_timestamp': [
                        last_event_time - timedelta(hours=2),
                        last_event_time - timedelta(hours=3),
                        last_event_time - timedelta(hours=4)
                    ]
                }),
                "Get phone changes by client ID": pd.DataFrame({
                    'user_id': ['user1', 'user3'],  # user2 missing
                    'change_timestamp': [
                        last_event_time - timedelta(hours=1),
                        last_event_time - timedelta(hours=2)
                    ]
                }),
                "Get token changes": pd.DataFrame({
                    'user_id': ['user1', 'user2'],  # user3 missing
                    'change_timestamp': [
                        last_event_time - timedelta(hours=3),
                        last_event_time - timedelta(hours=4)
                    ]
                })
            },
            "account_activity_analysis": {
                "Get all password changes": pd.DataFrame({
                    'user_id': ['user1', 'user2', 'user3'],
                    'change_timestamp': [
                        last_event_time - timedelta(hours=4),
                        last_event_time - timedelta(hours=5),
                        last_event_time - timedelta(hours=6)
                    ]
                })
            }
        }
        
        service = MergeFilterService()
        result = service.process_results(database_results, last_event_time)
        
        # Only user1 should qualify (has all 4 changes)
        assert len(result) == 1
        assert result.iloc[0]['user_id'] == 'user1'