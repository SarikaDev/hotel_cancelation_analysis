-- Cancellation Breakdown by Guest Type
-- Helps understand who cancels the most:

SELECT 
    guest_type,
    COUNT(CASE WHEN is_canceled = 'yes' THEN 1 END) AS canceled_bookings,
    COUNT(*) AS total_bookings,
    ROUND(
        100.0 * COUNT(CASE WHEN is_canceled = 'yes' THEN 1 END) / COUNT(*), 
        2
    ) AS cancellation_rate_percent
FROM 
    hotel_bookings
GROUP BY 
    guest_type
ORDER BY 
    cancellation_rate_percent DESC;
