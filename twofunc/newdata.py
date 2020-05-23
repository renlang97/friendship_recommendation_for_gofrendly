#%%----------------------------
""" Import libs """
import pandas as pd
import pymysql
from func.sql import sqlquery

#%%----------------------------
""" SQL data extraction """
def newsqldataext():
    queries = {
                # 2. Mutually connected friends(hard positive)
                # count: a.120,409(119,750) b.128,138(122,768) c. 
                'mf' : "SELECT a.user_id, a.friend_id FROM friends a\
                INNER JOIN friends b ON (a.user_id = b.friend_id) AND (a.friend_id = b.user_id) WHERE (a.user_id > a.friend_id)",
            }
    # mf, af, bf, vnf, uf
    print('--> SQL query begins...')
    
    # gofrendly, gofrendly-api
    with sqlquery('gofrendly-api') as newconn:
        mf = newconn.query(queries['mf']) 
        mf.to_hdf("./data/02_val/sqldata.h5", key='mf')
        print('--> mf\' query finished ')

    return mf

mf = newsqldataext()

# %%