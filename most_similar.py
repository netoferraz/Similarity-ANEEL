import numpy as np
import pickle
from scipy.cluster import hierarchy
import time
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import preprocessing
from sklearn.decomposition import TruncatedSVD

def getKSimilarTexts(norma:str,assunto=None, k=None):

    data = pd.read_csv('LanguageModelFile.csv',sep='|',encoding='utf-8',index_col=False)
    data = data.dropna()
    del data['Unnamed: 0']
    idxs = data.Tipo != 'RES'
    data = (data.loc[idxs]).reset_index()
    #import pdb; pdb.set_trace()
    assuntos = np.unique(data.Assuntos)

    X = np.load('X_LM.npy')
    X = X[idxs]

    #All features with 0 mean and std 1
    X = preprocessing.scale(X)

    #Making sure that all vectors have unit magnitude
    for i in range(X.shape[0]):
        Xi = X[i,:]
        X[i,:] = Xi/(np.sum(Xi**2)**0.5)


    idx = np.where(data.Norma==norma)[0]
    if len(idx)==0:
        print('Esta norma não está em nosso estoque.')
        return

    X_n = X[idx]
    if X_n.shape[0] == 2: import pdb; pdb.set_trace()
    aux = np.zeros(X.shape) + X_n
    similarity = np.sum(aux*X,axis=1)

    if isinstance(assunto,str):
        idxs = np.where(data.Assuntos==assunto)[0]
        similarity = similarity[idxs]
        data = data.loc[data.Assuntos==assunto].reset_index()
        del data['index']
        if data.shape[0]==0:
            print('Não encontramos o assunto solicitado. Lista de assuntos disponíveis:')
            print(assuntos)
            return
    if k==None: k = len(similarity)
    idxs_max = similarity.argsort()[-k:][::-1]
    #idxs_max = idxs_max[1:]
    #import pdb; pdb.set_trace()
    out = data.loc[idxs_max]
    normas = list(out.Norma)
    ementas = list(out.Ementa)
    #import pdb; pdb.set_trace()
    similarity = (similarity + 1)/2
    similarity.sort()
    similarity = similarity[-k:][::-1]
    #import pdb; pdb.set_trace()
    return normas,ementas,similarity,out

#normas,ementas,similarity,out = getKSimilarTexts('REN - RESOLUÇÃO NORMATIVA 482/2012',k=10)
#normas,ementas,similarity,out = getKSimilarTexts('REN - RESOLUÇÃO NORMATIVA 414/2010',k=10)
normas,ementas,similarity,out = getKSimilarTexts('REN - RESOLUÇÃO NORMATIVA 063/2004',k=10)

import pdb; pdb.set_trace()
