import numpy as np
import pickle
from scipy.cluster import hierarchy
import time
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import preprocessing
from sklearn.decomposition import TruncatedSVD

def getKSimilarTexts(norma:str,assunto=None, k=None):

    X = np.load('X_LM.npy')

    #All features with 0 mean and std 1
    X = preprocessing.scale(X)

    #Making sure that all vectors have unit magnitude
    for i in range(X.shape[0]):
        Xi = X[i,:]
        X[i,:] = Xi/(np.sum(Xi**2)**0.5)

    data = pd.read_csv('LanguageModelFile.csv',sep='|',encoding='utf-8',index_col=False)
    data = data.dropna()
    assuntos = np.unique(data.Assuntos)


    idx = np.where(data.Norma==norma)[0]
    if len(idx)==0:
        print('Esta norma não está em nosso estoque.')
        return

    X_n = X[idx]
    aux = np.zeros(X.shape) + X_n
    similarity = np.sum(aux*X,axis=1)

    if isinstance(assunto,str):
        idxs = np.where(data.Assuntos==assunto)[0]
        similarity = similarity[idxs]
        data = data.loc[data.Assuntos==assunto].reset_index()
        del data['index']
        if data.shape[0]==0:
            print('Não encontramos o macrotema solicitado. Lista de macrotemas disponíveis:')
            print(assuntos)
            return

    if k==None: k = len(similarity)
    idxs_max = similarity.argsort()[-k:][::-1]
    out = data.loc[idxs_max]
    normas = list(out.Norma)
    ementas = list(out.Ementa)
    #import pdb; pdb.set_trace()
    similarity = (similarity + 1)/2
    similarity.sort()
    similarity = similarity[-k:][::-1]
    #import pdb; pdb.set_trace()
    return normas,ementas,similarity,out

print(getKSimilarTexts('RES - RESOLUÇÃO CONJUNTA 005/2016',k=10))
