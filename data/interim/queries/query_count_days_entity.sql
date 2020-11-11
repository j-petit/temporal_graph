CREATE TABLE entity_counts AS
SELECT entity_1, my_date, COUNT(*) as occCount FROM
(
	SELECT entity_1, date(unix_time, "unixepoch") as my_date FROM data
	UNION ALL
	SELECT entity_2, date(unix_time, "unixepoch") as my_date FROM data
) 	
GROUP BY entity_1, my_date
ORDER BY my_date ASC, occCount DESC