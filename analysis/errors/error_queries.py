import analysis.utility as u

"""Collection of queries showing errors / malformed data in the database"""

if __name__ == '__main__':
    for i in u.generic_search(u.load_query('untracked_sets.sql')):
        print(i)
