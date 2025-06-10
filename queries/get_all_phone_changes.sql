SELECT 
    user_id,
    old_phone,
    new_phone,
    phone_type,
    change_date,
    changed_by
FROM event_logs.phone_changes
WHERE change_date >= :start_date
ORDER BY change_date DESC