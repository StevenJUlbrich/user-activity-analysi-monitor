SELECT 
    user_id,
    token_type,
    action,
    action_date,
    performed_by,
    ip_address
FROM event_logs.token_changes
WHERE action_date >= :start_date
  AND action IN ('CREATED', 'REVOKED', 'EXPIRED')
ORDER BY action_date DESC