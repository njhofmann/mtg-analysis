
"""Collection of queries for drawing together useful collections of data for analysis"""

# get metagame composition for a format within a given timeframe
metagame_comp = ("WITH FilteredResults AS ("
                 "SELECT ee.archetype archetype, ee.entry_id id "
                 "FROM events.event_entry ee JOIN events.event_info ei ON ei.tourny_id = ee.tourny_id "
                 "WHERE ei.date BETWEEN '2017-06-04' AND '2017-06-18' AND format = 'modern'), "
                 "archetypecounts AS ("
                 "SELECT archetype, COUNT(id) amount "
                 "FROM FilteredResults GROUP BY archetype), "
                 "totalcount AS ("
                 "SELECT COUNT(*) total "
                 "FROM Filtered Results) "
                 "SELECT ac.archetype, (CAST(ac.amount AS FLOAT) * 100 / CAST(tc.total AS FLOAT)) "
                 "FROM archetypecounts ac CROSS JOIN totalcount tc;")


if __name__ == '__main__':
    print(metagame_comp)