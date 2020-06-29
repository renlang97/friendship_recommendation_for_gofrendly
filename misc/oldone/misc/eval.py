"""
Date: 5 Apr 2020
Author: Harsha harshahn@kth.se
Implementation of evaluation metrics
Selected: auroc, hitrate, mrr
"""
#%%
""" Import libraries """
import numpy as np
# import recmetrics
#===========================================================================

"""1. Metrics of Relevance"""
#evaluate model with MSE and RMSE
#print(recmetrics.mse(test.actual, test.cf_predictions))
#print(recmetrics.rmse(test.actual, test.cf_predictions))

#%%
"""a. Area under ROC """
def auroc(true, score):
    from sklearn.metrics import roc_auc_score
    res = roc_auc_score(true, score)
    print("AUROC has been computed and the value is ", res)
    return res

#%%
"""b. MAP@K and MAR@K"""
# Precision@k = (# of recommended items @k that are relevant) / (# of recommended items @k)
# Recall@k = (# of recommended items @k that are relevant) / (total # of relevant items)
# [recmetrics.mark(actual, random_predictions, k=K)]
def meanavg(query, true, score):
    from sklearn.metrics import precision_score, recall_score
    precision = []; recall = []; res = []
    for q in range(query):
        precision.append(precision_score(true[q], score[q]))
        recall.append(recall_score(true[q], score[q]))

    res[0] = np.mean(precision); res[1] = np.mean(recall)
    print("MAP@K and MAR@K has been computed and the values are ", res[0], "and ", res[1])
    return res

#%%
""" c. Hit-rate: the fraction of queries q where i was ranked among the top K of the test sample (K = 500): True pairs showed up in top 100 list """
def hitrate(frds, rec):
    a = set(frds)
    b = set(rec)
    c = a.intersection(b) 
    res =  len(c)/len(b)  
    print("Hitrate has been computed and the value is ", res)
    return res

#==========================================================================

"""2. Metrics of Serendipity"""
#%%
"""a. Personalization """
def personalization(example_predictions):
    res = 0
    #res = recmetrics.personalization(predicted=example_predictions)
    print("Personalization of users has been computed and the value is ", res)
    return res

"""
example_predictions = [
    ['1', '2', 'C', 'D'],
    ['4', '3', 'm', 'X'],
    ['7', 'B', 't', 'X']
]"""

#%%
"""b. Diversity """ # cosine sim??
def diversity():
    res = 0
    
    print("Diversity of the list has been computed and the value is ", res)
    return res
#==============================================================================


"""3. Metrics of User Hits"""
#%%
"""a. Link-up rate """
def linkuprate():
    res=0

    print("Link-up rate has been computed and the value is ", res)
    return res

#%%
"""b. User hits ratio """
def userhits():
    res=0
    
    print("User hits ratio has been computed and the value is ", res)
    return res

#===========================================================================

"""4. Rank aware metric"""
#%%
"""a. Mean Reciprocal Rank (MRR) 
Mean Reciprocal Rank is a ranking or rank-aware metric. It is a binary relevance based
metrics and measures where is the first relevant index. Near to 1 imply the relevant items very
high up the list of recommendations. The formula is shown as below. Ri,q is the rank of user i
among recommended items for query q, and n is the total number of user pairs. """

def mrr(frds, rec):
    res = 0
    for i in frds:
        if i in rec:
            res += 1/(rec.index(i)+1)
    res = res/len(frds)
    print("MRR has been computed and the value is ", res)
    return res

#===========================================================================