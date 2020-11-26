SELECT * FROM entity_counts 
JOIN entities ON entity_counts.entity_1 = entities.mid
WHERE entity_counts.entity_1 = '/m/0f8l9c' AND (entity_counts.my_date > '2018-07-12' AND entity_counts.my_date < '2018-08-01')
ORDER BY my_date ASC
-- AND entity_counts.my_date < '2018-10-01'