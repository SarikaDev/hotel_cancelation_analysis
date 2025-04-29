-- Note is_canceled 0 = no and 1 = yes 
-- Top 5 Countries with Highest Cancellation Counts
SELECT 
    country,
    COUNT(*) AS cancel_count
FROM 
    hotel_bookings
WHERE 
    is_canceled = 'yes'
GROUP BY 
    country
ORDER BY 
    cancel_count DESC
LIMIT 5;
