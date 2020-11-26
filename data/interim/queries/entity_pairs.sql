SELECT * FROM data 
JOIN entities ON data.entity_1 = entities.mid
WHERE data.entity_1 = '/m/0f8l9c'
UNION ALL 
SELECT * FROM data 
JOIN entities ON data.entity_2 = entities.mid
WHERE data.entity_2 = '/m/0f8l9c'
