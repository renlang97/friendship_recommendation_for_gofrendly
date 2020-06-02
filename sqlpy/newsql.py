#%%----------------------------
""" Import libs """
import pandas as pd
import pymysql
from sql import sqlquery

#%%----------------------------
""" SQL data extraction """
def newsqldataext():
    queries = {
                # Mutually connected friends(hard positive)
                # count: a.120,409(119,750) b.128,138(122,768) c. 
                'mf' : "SELECT a.user_id, a.friend_id FROM friends a\
                INNER JOIN friends b ON (a.user_id = b.friend_id) AND (a.friend_id = b.user_id) WHERE (a.user_id > a.friend_id)"
            }
    print('--> SQL query begins...')
    
    # gofrendly, gofrendly-api
    with sqlquery('test') as newconn:
        mf = newconn.query(queries['mf']) 
        mf.to_hdf("../data/common/test/sqldata.h5", key='mf')
        print('--> mf\' query finished ')
    return mf

mf = newsqldataext()
