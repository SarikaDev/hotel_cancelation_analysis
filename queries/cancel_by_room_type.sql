-- Cancellation by Reserved Room Type
-- This helps spot if specific room types get canceled more:
SELECT 
    reserved_room_type,
    COUNT(CASE WHEN TRIM(LOWER(is_canceled)) = 'yes' THEN 1 END) AS canceled_bookings,
    COUNT(*) AS total_bookings,
    ROUND(
        100.0 * COUNT(CASE WHEN TRIM(LOWER(is_canceled)) = 'yes' THEN 1 END) / COUNT(*), 
        2
    ) AS cancellation_rate_percent
FROM 
    hotel_bookings
GROUP BY 
    reserved_room_type
ORDER BY 
    cancellation_rate_percent DESC;

