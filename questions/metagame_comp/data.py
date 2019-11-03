import questions.utility as qu
from psycopg2 import sql

"""Collection of queries for drawing together useful collections of data for analysis"""


# get metagame composition for a format within a given timeframe
def get_metagame_comp(end, length, format):
    query = ("WITH FilteredResults AS ("
             "SELECT ee.archetype archetype, ee.entry_id id "
             "FROM events.event_entry ee JOIN events.event_info ei ON ei.tourny_id = ee.tourny_id "
             f"WHERE ei.date BETWEEN DATE '{end}' - INTEGER '{length}' AND '{end}' AND format = '{format}'), "
             "archetypecounts AS ("
             "SELECT archetype, COUNT(id) amount "
             "FROM FilteredResults GROUP BY archetype), "
             "totalcount AS ("
             "SELECT COUNT(*) total "
             "FROM FilteredResults) "
             "SELECT ac.archetype, (CAST(ac.amount AS FLOAT) * 100 / CAST(tc.total AS FLOAT)) "
             "FROM archetypecounts ac CROSS JOIN totalcount tc")
    print(query)
    return qu.generic_search(query)


if __name__ == '__main__':
    print(get_metagame_comp('2019-05-01', 14, 'modern'))
