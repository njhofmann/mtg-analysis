
"""Collection of queries for drawing together useful collections of data for analysis"""

# get metagame composition for a format within a given timeframe
metagame_comp = ('')

with archetypecounts as (select ee.archetype archetype, count(ee.entry_id) amount from events.event_entry ee join events.event_info ei on ei.tourny_id = ee.tourny_id where ei.date between '2017-06-04' and '2017-06-18' and format = 'modern' group by archetype), totalcount as (select count(*) total from events.event_entry ee join events.event_info ei on ei.tourny_id = ee.tourny_id where ei.date between '2017-06-04' and '2017-06-18' and format = 'modern') select ac.archetype, (cast(ac.amount as decimal(7,2)) / cast(tc.total as decimal(7,2)))  from archetypecounts ac cross join totalcount tc;