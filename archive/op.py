import os
import pandas as pd
import time

# %%
#Text cleansing
def cleanse(text):
    import re
    import emoji #conda install -c conda-forge emoji
    text = text.replace("\n", " ") #remove breaks
    text = emoji.get_emoji_regexp().sub(u'',text) #remove emojis
    r = re.compile(r'([.,/#!?$%^&*;:{}=_`~()-])[.,/#!?$%^&*;:{}=_`~()-]+')
    text = r.sub(r'\1', text) #multiple punctuations
    if len(text) < 10: text = None #short texts
    return text

#Translate the text to english
def trans(in_stories):
    from googletrans import Translator #conda install -c conda-forge googletrans
    #from langdetect import detect

    langlist =[]; count = 0 #langdist = []
    for index, row in in_stories.iterrows():
        t = Translator()
        txt = cleanse(row['myStory']) #cleanse  
        if (txt != None) and (txt != ''):
            time.sleep(.5)
            try: 
                langlist.append(t.translate(txt).text) #detect(txt)
                count += 1
                #if count >= 300 : return langlist
                print('Index:', index, ' Count:', count)
            except: 
                print( index, '\n', txt , '\n', '###'); langlist.append(None)  
                break
        else: langlist.append(None)
    return langlist

def removenull(text):
    return text[(text['myStory'] != '') & (~text['myStory'].isnull())]
 
# %%
def loadone(): #load the dfs
    os.chdir('./data/raw')
    uNodes = pd.read_hdf("uNodes.h5", key='uNodes')
    #fLinks = pd.read_hdf("fLinks.h5", key='fLinks')
    #aNodes = pd.read_hdf("aNodes.h5", key='aNodes')
    #aLinks = pd.read_hdf("aLinks.h5", key='aLinks')
    #cLinks = pd.read_hdf("cLinks", key='cLinks')
    os.chdir('../..')
    return uNodes#[uNodes, fLinks, aNodes, aLinks]

# %% Clear all variables
def clearvars():
    import sys
    sys.modules[__name__].__dict__.clear()