"""
Date: 02 March 2020
Goal: 01 Data processing for one.py
Author: Harsha HN harshahn@kth.se
"""

#%%-------------
""" 01. Data Pre-processing """
class dproc:

    # Load all the training set data from stored files
    @staticmethod
    def loadsql():
        mf = pd.read_hdf("../data/common/eda/network.h5", key='mf')
        af = pd.read_hdf("../data/common/eda/network.h5", key='af')
        bf = pd.read_hdf("../data/common/eda/network.h5", key='bf')
        vnf = pd.read_hdf("../data/common/eda/network.h5", key='vnf')
        print('-> df files are loaded')

        return [users, mf, af, bf, vnf] 

    # Load all the data
    @staticmethod
    def loaddata():
        # Stockholm
        import pickle
        with open('../data/common/sublinks.pkl', 'rb') as f: # links.pickle
            [submfs, subafs, subbfs, subvnfs] = pickle.load(f)
    
        neg = (subbfs | subvnfs); pos = (submfs | subafs) - neg
        return [list(pos), list(neg)]

    # Load validation data
    @staticmethod
    def loadval(trainpos, trainids):
        valmf = pd.read_hdf("../data/common/val/sqldata.h5", key='mf')
        valmfs = set(tuple(zip(valmf.user_id, valmf.friend_id)))
        valpos = valmfs #valpos = (valmfs | valafs) 
        links = set([(a,b) for (a,b) in valpos if (a in trainids) and (b in trainids)])
        valpos = links - set(trainpos) 
        return list(valpos)

    # Load training and validation data
    @staticmethod
    def getdata():
        # Training set: user profile, friend links
        [users, trainpos, trainneg] = dproc.loaddata()
        import pandas as pd
        #['user_id', 'story', 'iam', 'meetfor', 'birthday', 'marital', 'children', 'lat', 'lng']
        trainids = pd.read_hdf("../data/common/eda/users.h5", key='01').index
        print('-> 01 Train set ids and links are finished.')

        # Validation set: new friend connections
        valpos = dproc.loadval(trainpos, trainids)
        print('-> 02 Validation set friend links are finished.')
        
        # with open('../data/one/oneload.pkl', 'wb') as f:
        #    pickle.dump([trainpos, trainneg, valpos], f)

        # Create Networkx graph from trainpos
        # import networkx as nx

        return [trainpos, trainneg, valpos]

    # Data pre-processing
    @staticmethod
    def preproc(df):
        import pandas as pd
        # df = ['user_id', 'story', 'iam', 'meetfor', 'birthday', 'marital', 'children', 'lat', 'lng']
        df.columns = ['id', 'story', 'iam', 'meetfor', 'age', 'marital', 'kids', 'lat', 'lng']
        df.set_index('id', inplace = True)
        
        """ 01. Data cleanse and imputation """
    
        #'iam', 'meetfor' to set()
        df['iam'] = df['iam'].apply(lambda x: set(x.split(',')) if x != None else set())
        df['meetfor'] = df['meetfor'].apply(lambda x: set(x.split(',')) if x != None else set())
        
        #'birthday' to age
        df['age'] = df['age'].apply(lambda x: int((x.today() - x).days/365))
        
        # has children, marital
        df['marital'].fillna(-1, inplace=True)
        df['kids'].fillna(-1, inplace=True)        

        # story
        mycleanse = cleanse()
        df['story'] = df['story'].apply(lambda x: mycleanse.cleanse(x))
        
        # df.to_hdf("../data/one/users.h5", key='02') # df = pd.read_hdf("../data/one/users.h5", key='02')

        """ 02. stories translation with GCP """
        # df = pd.read_hdf("../data/one/users.h5", key='02')
        from gcp import gcpserver
        df['story'] = df['story'].apply(lambda x: gcpserver.gcptrans(x) if x!=-1 else -1)
        # df['story'].to_hdf("../data/one/users.h5", key='03') # df['story']=pd.read_hdf("../data/one/users.h5", key='03')
        
        """ 03. Stories to S-BERT emb """
        from sentence_transformers import SentenceTransformer
        sbertmodel = SentenceTransformer('roberta-large-nli-mean-tokens')

        # Generate embeddings
        before = time.time() #listup = lambda x: [x]
        df['emb'] = df['story'].apply(lambda x: sbertmodel.encode([x]) if x!=-1 else -1)
        print("-> S-BERT embedding finished.", (time.time() - before)) #534 sec
        df.drop(columns = 'story', inplace = True)
        # df['emb'].to_hdf("../data/one/users.h5", key='04') # df['emb']=pd.read_hdf("../data/one/users.h5", key='04')
        
        #df.to_hdf("../data/one/users.h5", key='05')
        return df
    
    # Feature Engineering
    @staticmethod
    def feature(feat):        
        # feat = pd.read_hdf("../data/one/users.h5", key='05')
        import numpy as np
        def onehotencode(input, dim):
            onehot = np.zeros(dim, dtype=int)

            if input == {''}:
                return onehot
            elif input == '-1' or -1:
                input = [-1]
            elif type(input) == set:
                input = list(input)
            
            for el in input:
                ind = int(itm)
                if ind < dim: onehot[ind] = 1

            return onehot

        feat['cat'] = feat.index
        feat['cat'] = feat['cat'].apply(lambda x: np.concatenate(( onehotencode(feat.iam[x], 18), onehotencode(feat.meetfor[x], 19), onehotencode(feat.marital[x], 5), onehotencode(feat.kids[x], 4) )))

        feat = feat.drop(columns = ['iam', 'meetfor', 'marital', 'kids'])
        
        from sklearn.preprocessing import robust_scale, normalize

        feat['age'] = feat['age'].clip(18, 100)
        feat.age = robust_scale(feat.age.to_numpy()[:, None])
        feat.lat = robust_scale(feat.lat.to_numpy()[:, None])
        feat.lng = robust_scale(feat.lng.to_numpy()[:, None])

        feat['num'] = feat.index
        feat['num'] = feat['num'].apply(lambda x: [feat.age[x], feat.lat[x], feat.lng[x]])
        feat = feat.drop(columns = ['age', 'lat', 'lng'])

        #feat.to_hdf("../data/one/feat.h5", key='01')

        return df







#%%-------------
""" 02. Cleanse story """
import re
import emoji #conda install -c conda-forge emoji
class cleanse:
    #cleanse story
    r = re.compile(r'([.,/#!?$%^&*;:{}=_`~()-])[.,/#!?$%^&*;:{}=_`~()-]+')

    @classmethod
    def cleanse(cls, text):
        if (text == '') or (text == None): #.isnull()
            text = -1
        else:
            text = text.replace("\n", ". ") #remove breaks
            text = emoji.get_emoji_regexp().sub(u'', text) #remove emojis
            text = cls.r.sub(r'\1', text) #multiple punctuations
            if len(text) < 10: 
                text = -1 #short texts
        return text

#%%----------------
"""
import h5py
f = h5py.File('../data/common/eda/location.h5', 'r')
[key for key in f.keys()]

"""
