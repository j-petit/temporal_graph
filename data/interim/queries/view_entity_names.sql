SELECT 
	data.unix_time,
	e1.name as entity_1_name,
	e2.name as entity_2_name
FROM data 
JOIN entities as e1 ON data.entity_1 = e1.mid
JOIN entities as e2 ON data.entity_2 = e2.mid
