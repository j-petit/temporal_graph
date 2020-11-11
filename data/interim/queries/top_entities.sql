SELECT entities.name, test.occCount, test.my_date, test.daily_rank FROM
(
SELECT entity_1, occCount, my_date,
row_number() over (partition by my_date order by occCount desc) as daily_rank  
FROM entity_counts
)
AS test
JOIN entities ON entities.mid = test.entity_1 AND test.daily_rank < 10
ORDER BY test.my_date ASC, test.occCount DESC
