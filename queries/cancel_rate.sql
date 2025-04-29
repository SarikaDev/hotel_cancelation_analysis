-- Cancellation Rate per Country
-- This gives you cancellation as a percentage of total bookings:



SELECT 
    country,
    COUNT(CASE WHEN is_canceled = 'yes' THEN 1 END) AS canceled_bookings,
    COUNT(*) AS total_bookings,
    ROUND(
        100.0 * COUNT(CASE WHEN is_canceled = 'yes' THEN 1 END) / COUNT(*), 
        2
    ) AS cancellation_rate_percent
FROM 
    hotel_bookings

GROUP BY 
    country
HAVING 
    COUNT(*) > 50  -- filter out countries with very few bookings if needed
ORDER BY 
    cancellation_rate_percent DESC
LIMIT 5;
