SELECT 
    user_id,
    old_email,
    new_email,
    change_date,
    changed_by,
    change_reason
FROM event_logs.email_changes
WHERE change_date >= :start_date
ORDER BY change_date DESC