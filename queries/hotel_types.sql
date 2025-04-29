SELECT
    guest_type,

    -- Resort Hotel stats
    COUNT(CASE WHEN hotel = 'Resort Hotel' AND is_canceled = 'yes' THEN 1 END) AS resort_canceled,


    ROUND(
        100.0 * COUNT(CASE WHEN hotel = 'Resort Hotel' AND is_canceled = 'yes' THEN 1 END) /
        NULLIF(COUNT(CASE WHEN hotel = 'Resort Hotel' THEN 1 END), 0), 2
    ) AS resort_cancel_rate,
	    COUNT(CASE WHEN hotel = 'Resort Hotel' THEN 1 END) AS resort_total,
		  COUNT(CASE WHEN hotel = 'Resort Hotel' AND is_canceled = 'no' THEN 1 END) AS resort_approved,
	  ROUND(
        100.0 * COUNT(CASE WHEN hotel = 'Resort Hotel' AND is_canceled = 'no' THEN 1 END) /
        NULLIF(COUNT(CASE WHEN hotel = 'Resort Hotel' THEN 1 END), 0), 2
    ) AS resort_approve_rate

FROM hotel_bookings
GROUP BY guest_type
ORDER BY guest_type;
