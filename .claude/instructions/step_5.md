# **Step 5: Data Merging & Filtering Logic**

## **Objective**

* Take the four query results (each a pandas DataFrame) for a given time window.
* **Merge and filter** to find users who meet **all four criteria within the last 24 hours**.
* Prepare the filtered results for reporting/export.

---

## **A. Merge & Filter Service Module**

**Directory:**
`src/client_activity_monitor/model/services/merge_filter_service.py`

**Core Algorithm:**

1. Each query result is a DataFrame (`password_df`, `email_df`, `phone_df`, `token_df`).
2. All DataFrames have at least a `user_id` and a `change_time` column.
3. Only users appearing in **all four DataFrames** (i.e., made all four changes) are candidates.
4. **For each user**, filter to only those whose **latest change for each criterion occurred within the last 24 hours** from now (or from a reference time).
5. Return a DataFrame with users who qualify, including the relevant details.

---

**Example Implementation Outline:**

```python
import pandas as pd
from datetime import datetime, timedelta

class MergeFilterService:
    """
    Service to merge and filter query results to find reportable users.
    """

    def __init__(self, password_df, email_df, phone_df, token_df):
        self.password_df = password_df
        self.email_df = email_df
        self.phone_df = phone_df
        self.token_df = token_df

    def filter_users_with_all_changes(self, reference_time=None):
        """
        Returns DataFrame of users with all four changes within last 24 hours.

        Args:
            reference_time: The datetime from which to count back 24 hours.
                            If None, uses datetime.now().

        Returns:
            DataFrame of qualifying users with their change details.
        """
        if reference_time is None:
            reference_time = datetime.now()
        window_start = reference_time - timedelta(hours=24)

        # Ensure change_time columns are datetime
        for df in [self.password_df, self.email_df, self.phone_df, self.token_df]:
            if not df.empty and not pd.api.types.is_datetime64_any_dtype(df["change_time"]):
                df["change_time"] = pd.to_datetime(df["change_time"])

        # Filter for changes in last 24 hours
        pw_recent = self.password_df[self.password_df["change_time"] >= window_start]
        email_recent = self.email_df[self.email_df["change_time"] >= window_start]
        phone_recent = self.phone_df[self.phone_df["change_time"] >= window_start]
        token_recent = self.token_df[self.token_df["change_time"] >= window_start]

        # Find intersection of user_ids present in all DataFrames
        sets = [set(df["user_id"]) for df in [pw_recent, email_recent, phone_recent, token_recent] if not df.empty]
        if len(sets) < 4:
            return pd.DataFrame()  # Not enough data to report anyone

        qualifying_user_ids = set.intersection(*sets)
        if not qualifying_user_ids:
            return pd.DataFrame()

        # Optionally merge details for reporting
        merged = pw_recent[pw_recent["user_id"].isin(qualifying_user_ids)] \
            .merge(email_recent, on="user_id", suffixes=("_password", "_email")) \
            .merge(phone_recent, on="user_id", suffixes=("", "_phone")) \
            .merge(token_recent, on="user_id", suffixes=("", "_token"))

        return merged
```

---

## **B. Controller Integration**

* After all four queries complete, the controller:

  * Instantiates `MergeFilterService` with the four DataFrames.
  * Calls `filter_users_with_all_changes(reference_time)` (reference time = now or user input).
  * Passes the resulting DataFrame to the reporting/export logic.

---

## **C. UI Feedback**

* If no users qualify, show a clear message: “No users met all criteria in the last 24 hours.”
* If results exist, enable reporting/export actions.

---

## **D. Error Handling**

* Handle missing/empty DataFrames (no changes for some criteria).
* Handle bad/missing columns with user-friendly error logs.

---

## **E. Testing**

* **Unit tests:**

  * Create small DataFrames with mock user data; assert correct intersection/merging.
* **Manual test:**

  * Simulate input with overlapping and non-overlapping users and dates.

---

## **F. Example AI Prompt for This Brick**

> Generate a Python class that takes four pandas DataFrames (password, email, phone, token changes), each with `user_id` and `change_time` columns. Write a method to filter for users who appear in all four DataFrames and whose changes occurred within the last 24 hours. Merge the details for reporting.

---

## **Summary Table: Step 5**

| Sub-Step           | Action/Behavior                                                   |
| ------------------ | ----------------------------------------------------------------- |
| MergeFilterService | Merges/filters four DataFrames to find users meeting all criteria |
| Controller         | Calls merge/filter logic after query step, passes results onward  |
| UI                 | Informs user of result (success or “no users found”)              |
| Error Handling     | Catches/report missing data, bad columns, no results              |
| Testing            | Unit/manual test intersection and reporting logic                 |

---
