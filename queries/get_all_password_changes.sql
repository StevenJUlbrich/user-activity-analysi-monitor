SELECT 
    user_id,
    change_date,
    change_type,
    change_source,
    ip_address,
    user_agent
FROM audit_logs.password_changes
WHERE change_date >= :start_date
ORDER BY change_date DESC