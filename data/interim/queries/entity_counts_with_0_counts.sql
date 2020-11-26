SELECT IFNULL(ec1.occCount, 0) as occCount FROM dates
LEFT OUTER JOIN 
	(SELECT * FROM entity_counts WHERE entity_counts.entity_1 = '/m/0gcngm')
AS ec1 ON dates.my_date == ec1.my_date
WHERE (dates.my_date > '2018-03-01' AND dates.my_date <= '2018-05-01')