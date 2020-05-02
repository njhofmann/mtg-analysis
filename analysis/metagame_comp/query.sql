WITH FilteredResults AS (
    SELECT ee.archetype archetype, ee.entry_id id
    FROM events.event_entry ee
        JOIN events.event_info ei ON ei.tourny_id = ee.tourny_id
    WHERE ei.date BETWEEN (DATE '{date}' - INTEGER '{length}') AND DATE '{date}'
      AND ei.format = '{format}'
    ),
     ArchetypeCounts AS (
         SELECT fr.archetype, COUNT(fr.id) amount
         FROM FilteredResults fr
         GROUP BY fr.archetype
    ),
     TotalCount AS (
         SELECT COUNT(*) total
         FROM FilteredResults
    )
SELECT ac.archetype archetype, (CAST(ac.amount AS FLOAT) / CAST(tc.total AS FLOAT)) * 100 percent
FROM ArchetypeCounts ac CROSS JOIN TotalCount tc
ORDER BY percent DESC