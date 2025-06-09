# Step 5: Data Merging & Filtering Logic

## Objective
Take query results from multiple databases and identify users who have made ALL FOUR types of changes (password, email, phone, token) within the last 24 hours from the "Last Time Event Reported" timestamp.

## A. Merge Filter Service Implementation

Create `src/client_activity_monitor/model/services/merge_filter_service.py`:

### Purpose
Merge results from different databases and filter to find users meeting all criteria within the specified time window.

### Implementation

```python
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger

class MergeFilterService:
    """
    Service to merge and filter query results from multiple databases.
    Identifies users who made all 4 change types within 24 hours.
    """
    
    # Define the expected query names and their change types
    CHANGE_TYPE_MAPPING = {
        "Get all password changes": "password",
        "Get all email changes": "email",
        "Get phone changes by client ID": "phone",
        "Get token changes": "token"
    }
    
    def __init__(self):
        """Initialize the merge filter service."""
        self.required_change_types = {"password", "email", "phone", "token"}
        
    def process_results(
        self,
        database_results: Dict[str, Dict[str, pd.DataFrame]],
        last_event_time: datetime
    ) -> pd.DataFrame:
        """
        Process all database results to find users meeting criteria.
        
        Args:
            database_results: Nested dict from DatabaseExecutor
                {
                    "client_activity_analysis": {
                        "Get all email changes": DataFrame,
                        "Get phone changes by client ID": DataFrame,
                        "Get token changes": DataFrame
                    },
                    "account_activity_analysis": {
                        "Get all password changes": DataFrame
                    }
                }
            last_event_time: The "Last Time Event Reported" from UI
            
        Returns:
            DataFrame containing users who made all 4 changes within 24 hours
            Columns: user_id, password_change_time, email_change_time, 
                    phone_change_time, token_change_time, [other relevant fields]
        """
        # Step 1: Combine all results into a single structure by change type
        combined_changes = self._combine_results_by_change_type(database_results)
        
        # Step 2: Find users with all 4 change types
        users_with_all_changes = self._find_users_with_all_changes(combined_changes)
        
        # Step 3: Filter to only changes within 24 hours of last_event_time
        filtered_users = self._filter_by_time_window(
            users_with_all_changes,
            last_event_time
        )
        
        # Step 4: Create final report DataFrame
        report_df = self._create_report_dataframe(filtered_users)
        
        logger.info(f"Found {len(report_df)} users meeting all criteria")
        return report_df
        
    def _combine_results_by_change_type(
        self,
        database_results: Dict[str, Dict[str, pd.DataFrame]]
    ) -> Dict[str, pd.DataFrame]:
        """
        Combine results from all databases organized by change type.
        
        Returns:
            {
                "password": DataFrame with all password changes,
                "email": DataFrame with all email changes,
                "phone": DataFrame with all phone changes,
                "token": DataFrame with all token changes
            }
        """
        combined = {change_type: pd.DataFrame() for change_type in self.required_change_types}
        
        for db_name, queries in database_results.items():
            for query_name, df in queries.items():
                if df.empty:
                    continue
                    
                # Map query name to change type
                change_type = self.CHANGE_TYPE_MAPPING.get(query_name)
                if not change_type:
                    logger.warning(f"Unknown query name: {query_name}")
                    continue
                    
                # Add source database column for tracking
                df = df.copy()
                df['source_database'] = db_name
                
                # Standardize column names if needed
                df = self._standardize_columns(df, change_type)
                
                # Combine with existing data for this change type
                if combined[change_type].empty:
                    combined[change_type] = df
                else:
                    combined[change_type] = pd.concat(
                        [combined[change_type], df],
                        ignore_index=True
                    )
                    
                logger.info(f"Added {len(df)} {change_type} changes from {db_name}")
                
        return combined
        
    def _standardize_columns(self, df: pd.DataFrame, change_type: str) -> pd.DataFrame:
        """
        Standardize column names across different queries.
        Ensure each DataFrame has at minimum: user_id, change_timestamp
        """
        # Map possible column names to standard names
        column_mappings = {
            'user_id': ['user_id', 'userid', 'user', 'employee_id'],
            'change_timestamp': ['change_timestamp', 'change_time', 'timestamp', 
                               'modified_date', 'change_date', 'action_timestamp']
        }
        
        # Rename columns to standard names
        for standard_name, possible_names in column_mappings.items():
            for col in df.columns:
                if col.lower() in [name.lower() for name in possible_names]:
                    df = df.rename(columns={col: standard_name})
                    break
                    
        # Verify required columns exist
        required_columns = ['user_id', 'change_timestamp']
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            logger.error(f"Missing columns for {change_type}: {missing_columns}")
            logger.error(f"Available columns: {list(df.columns)}")
            
        # Ensure change_timestamp is datetime
        if 'change_timestamp' in df.columns:
            df['change_timestamp'] = pd.to_datetime(df['change_timestamp'])
            
        # Add change type column
        df['change_type'] = change_type
        
        return df
        
    def _find_users_with_all_changes(
        self,
        combined_changes: Dict[str, pd.DataFrame]
    ) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Find users who appear in all 4 change types.
        
        Returns:
            {
                "user123": {
                    "password": DataFrame of password changes for user123,
                    "email": DataFrame of email changes for user123,
                    "phone": DataFrame of phone changes for user123,
                    "token": DataFrame of token changes for user123
                }
            }
        """
        # Get unique users from each change type
        users_by_type = {}
        for change_type, df in combined_changes.items():
            if not df.empty and 'user_id' in df.columns:
                users_by_type[change_type] = set(df['user_id'].unique())
            else:
                users_by_type[change_type] = set()
                
        # Find intersection - users with all 4 change types
        if len(users_by_type) < 4:
            logger.warning(f"Only found {len(users_by_type)} change types with data")
            return {}
            
        users_with_all = set.intersection(*users_by_type.values())
        logger.info(f"Found {len(users_with_all)} users with all 4 change types")
        
        # Build result structure
        result = {}
        for user_id in users_with_all:
            result[user_id] = {}
            for change_type, df in combined_changes.items():
                if not df.empty:
                    user_changes = df[df['user_id'] == user_id].copy()
                    result[user_id][change_type] = user_changes
                    
        return result
        
    def _filter_by_time_window(
        self,
        users_with_all_changes: Dict[str, Dict[str, pd.DataFrame]],
        last_event_time: datetime
    ) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Filter to only users where ALL changes occurred within 24 hours 
        before the last_event_time.
        """
        window_start = last_event_time - timedelta(hours=24)
        filtered_users = {}
        
        for user_id, changes_by_type in users_with_all_changes.items():
            # Check if all change types have at least one change in the window
            all_in_window = True
            user_filtered_changes = {}
            
            for change_type, df in changes_by_type.items():
                # Filter to changes within the 24-hour window
                mask = (df['change_timestamp'] >= window_start) & \
                       (df['change_timestamp'] <= last_event_time)
                filtered_df = df[mask]
                
                if filtered_df.empty:
                    all_in_window = False
                    break
                    
                user_filtered_changes[change_type] = filtered_df
                
            if all_in_window:
                filtered_users[user_id] = user_filtered_changes
                
        logger.info(f"{len(filtered_users)} users had all changes within 24-hour window")
        return filtered_users
        
    def _create_report_dataframe(
        self,
        filtered_users: Dict[str, Dict[str, pd.DataFrame]]
    ) -> pd.DataFrame:
        """
        Create final report DataFrame with one row per qualifying user.
        """
        if not filtered_users:
            return pd.DataFrame()
            
        report_rows = []
        
        for user_id, changes_by_type in filtered_users.items():
            row = {'user_id': user_id}
            
            # Get the most recent change for each type
            for change_type in self.required_change_types:
                if change_type in changes_by_type and not changes_by_type[change_type].empty:
                    df = changes_by_type[change_type]
                    latest = df.loc[df['change_timestamp'].idxmax()]
                    
                    row[f'{change_type}_change_time'] = latest['change_timestamp']
                    row[f'{change_type}_source_db'] = latest.get('source_database', 'Unknown')
                    
                    # Include any additional relevant fields
                    for col in ['changed_by', 'old_value', 'new_value']:
                        if col in latest:
                            row[f'{change_type}_{col}'] = latest[col]
                            
            report_rows.append(row)
            
        report_df = pd.DataFrame(report_rows)
        
        # Sort by user_id
        report_df = report_df.sort_values('user_id')
        
        # Add summary columns
        if not report_df.empty:
            # Calculate earliest and latest change for each user
            change_time_cols = [col for col in report_df.columns if col.endswith('_change_time')]
            report_df['earliest_change'] = report_df[change_time_cols].min(axis=1)
            report_df['latest_change'] = report_df[change_time_cols].max(axis=1)
            report_df['change_window_hours'] = (
                (report_df['latest_change'] - report_df['earliest_change'])
                .dt.total_seconds() / 3600
            )
            
        return report_df
```

## B. Controller Integration

```python
# In MainController._run_analysis_thread method:

# After executing queries (Step 4)
results = self.database_executor.execute_all_databases(...)

# Process results through merge/filter
merge_filter_service = MergeFilterService()
filtered_data = merge_filter_service.process_results(
    database_results=results,
    last_event_time=last_event_time  # From UI input
)

if filtered_data.empty:
    logger.info("No users found matching all criteria within 24-hour window")
    # Show message to user
else:
    logger.info(f"Found {len(filtered_data)} users meeting all criteria")
    # Continue to report generation (Step 6)
```

## C. Key Business Logic

1. **Combine Results**: Merge results from all databases by change type
2. **Find Complete Sets**: Identify users with all 4 change types (password, email, phone, token)
3. **24-Hour Window**: Filter to users where ALL changes occurred within 24 hours before last_event_time
4. **Report Format**: One row per user with timestamps and details for each change type

## D. Expected Output

The final DataFrame will have columns like:
- `user_id`
- `password_change_time`, `password_source_db`, `password_changed_by`
- `email_change_time`, `email_source_db`, `email_old_value`, `email_new_value`
- `phone_change_time`, `phone_source_db`
- `token_change_time`, `token_source_db`
- `earliest_change`, `latest_change`, `change_window_hours`

## E. Edge Cases Handled

1. **Empty Results**: Any database or query returning no results
2. **Missing Columns**: Different queries might have different column names
3. **Multiple Changes**: User might have multiple changes of same type (uses most recent)
4. **Time Zones**: Assumes all timestamps are in same timezone
5. **No Qualifying Users**: Returns empty DataFrame

## F. Testing Considerations

1. Test with users having changes across different databases
2. Test with users having changes outside the 24-hour window
3. Test with users missing one or more change types
4. Test with empty query results
5. Test with different column naming conventions

## Next Step
After implementing merge/filter logic, proceed to Step 6: Report Generation & Export to create Excel and CSV reports.