#MHCI_BP_predictor.py

import os, sys, math, re
import numpy as np
import pandas as pd
#matplotlib inline
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_context("notebook", font_scale=1.4)
import epitopepredict as ep

from sklearn import metrics
import joblib
from sklearn.model_selection import train_test_split,cross_val_score,ShuffleSplit
from sklearn.neural_network import MLPRegressor

codes = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L',
         'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y']

def blosum_encode(seq):
    '''
    Encode protein sequence, seq, to one-dimension array.
    Use blosum62 matrix to encode the number.
    input: [string] seq (length = n)
    output: [1x24n ndarray] e
    '''
    #encode a peptide into blosum features
    s=list(seq)
    blosum62 = ep.blosum62
    x = pd.DataFrame([blosum62[i] for i in seq]).reset_index(drop=True)
    e = x.to_numpy().flatten() 
    # print(x)   
    return e

def auc_score(true,sc,cutoff=None):
    '''
    Calculate the auc score of soc curve
    '''
    if cutoff!=None:
        true = (true<=cutoff).astype(int)
        sc = (sc<=cutoff).astype(int)
    # print(true, sc)
    
    r = metrics.roc_auc_score(true, sc) 
    # #Or use the following code for alternative
    # fpr, tpr, thresholds = metrics.roc_curve(true, sc, pos_label=1)
    # r = metrics.auc(fpr, tpr)
    
    return  r

def build_predictor(training_data, allele, encoder, hidden_node):

    data = training_data[training_data['allele'] == allele]
    if len(data)<200:
        return

    # #write training dataframe to csv file
    # aw = re.sub('[*:]','_',allele) 
    # data.to_csv(os.path.join('alletes',aw+'_data.csv'))
    
    reg = MLPRegressor(hidden_layer_sizes=(hidden_node), alpha=0.01, max_iter=500,
                        activation='relu', solver='lbfgs', random_state=2)    
    X = data.peptide.apply(lambda x: pd.Series(encoder(x)),1) #Find bug: encoding result has NaN
    y = data.log50k

    ## ---- TEST ---- ##
    # print(X)
    # print (allele, len(X))
    
    reg.fit(X,y)       
    return reg

def get_allele_names(data):
    a = data.allele.value_counts()
    a =a[a>200]
    return list(a.index)

def build_prediction_model(training_data, hidden_node):
    al = get_allele_names(training_data)
    path = 'models'
    for a in al:
        aw = re.sub('[*:]','_',a) 
        fname = os.path.join(path, aw+'.joblib')
        reg = build_predictor(training_data, a, blosum_encode, hidden_node)
        if reg is not None:
            joblib.dump(reg, fname, protocol=2)

def main(hidden_node):
    training_data = ep.get_training_set(length=9)
    # print(training_data)
    build_prediction_model(training_data, hidden_node)

# main(20)