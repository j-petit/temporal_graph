SELECT IIF(data.entity_1 == "/m/05dq_", data.entity_2, data.entity_1) AS entity 
FROM data
WHERE data.unix_time <= 1537365600 
AND (data.entity_1 == "/m/05dq_" OR data.entity_2 == "/m/05dq_")
ORDER BY unix_time DESC
LIMIT 30
