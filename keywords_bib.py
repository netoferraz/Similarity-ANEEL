import pandas as pd
import numpy as np
import pickle, time, re, os
from scipy.cluster import hierarchy
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn.decomposition import TruncatedSVD
from classic_clustering import ClassicClustering
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter

def get_keywords_text(k:int=20):
    '''
    This function outputs the 'k' most important keywords for all the complete texts.
    '''

    data = pd.read_csv('interesting_norms.csv',sep='|',encoding='utf-8')
    data = data.drop(data.index[[16,24]])
    data = data.reset_index()
    del data['index']
    normas = list(data['Texto Extraído'].str.lower())

    cc = ClassicClustering()

    cc.define_stop_words(user_defined_stopwords=['deverá','aplicável','apresentar','caso',
                                                'janeiro','fevereiro','março','abril','maio','junho',
                                                'julho','agosto','setembro','outubro','novembro','dezembro',
                                                'rdc','resolução','normativa','colegiada','publicada','dispõe',
                                                'sobre','devem','nr','prazo','anexo','anexos','tornar','uso',
                                                'considerando','redação','tornar','diário','lista','item',
                                                'ms','união','passa','portaria','instrução','administrativa','normativa','mg','dcb',
                                                'inciso','artigo','cópia','podem','destinadas','df','deste',
                                                'listas','posteriores','possuir','outro','outra','outros','outras',
                                                'desenvolvem','prestam','cem','contém','pronto','atendam','kg','ppm','aprova',
                                                'todo','neste','desta','parte','qualquer','art','aneel'])

    cc.textos = normas

    cc.textos_tratados = [cc.trata_textos(texto) for texto in cc.textos]

    bow_tfidf,feature_names = cc.vec_tfidf(stem=False,max_features=5000)
    bow_tfidf = bow_tfidf.todense()

    keywords = []
    ponts_tfidf = []
    for i in range(bow_tfidf.shape[0]):
        norma_vector = np.array(bow_tfidf[i])
        idxs = np.array(norma_vector.argsort()[-k:][::-1]).T
        s=''
        ponts_tfidf_norm = []
        for j in range(k):
            if norma_vector[0,idxs[-(j+1)]] != 0:
                s = s + feature_names[idxs[-(j+1)][0]] + ','
                ponts_tfidf_norm.append(norma_vector[0,idxs[-(j+1)]])
        ponts_tfidf.append(ponts_tfidf_norm)
        keywords.append(s)

    return keywords,ponts_tfidf

def get_keywords_ementa(k:int=10):
    '''
    This function outputs the 'k' most important keywords for all ementas.
    '''

    data = pd.read_csv('interesting_norms.csv',sep='|',encoding='utf-8')
    data = data.drop(data.index[[16,24]])
    data = data.reset_index()
    del data['index']
    ementas = list(data.Ementa.str.lower())


    cc = ClassicClustering()

    cc.define_stop_words(user_defined_stopwords=['deverá','aplicável','apresentar','caso',
                                                'janeiro','fevereiro','março','abril','maio','junho',
                                                'julho','agosto','setembro','outubro','novembro','dezembro',
                                                'rdc','resolução','normativa','colegiada','publicada','dispõe',
                                                'sobre','devem','nr','prazo','anexo','anexos','tornar','uso',
                                                'considerando','redação','tornar','diário','lista','item',
                                                'ms','união','passa','portaria','instrução','administrativa','normativa','mg','dcb',
                                                'inciso','artigo','cópia','podem','destinadas','df','deste',
                                                'listas','posteriores','possuir','outro','outra','outros','outras',
                                                'desenvolvem','prestam','cem','contém','pronto','atendam','kg','ppm','aprova',
                                                'todo','neste','desta','parte','qualquer','art','aneel'])

    cc.textos = ementas
    cc.textos_tratados = [cc.trata_textos(texto) for texto in cc.textos]

    bow_tfidf,feature_names = cc.vec_tfidf(stem=False)
    bow_tfidf = bow_tfidf.todense()

    keywords = []
    ponts_tfidf = []
    for i in range(bow_tfidf.shape[0]):
        norma_vector = np.array(bow_tfidf[i])
        idxs = np.array(norma_vector.argsort()[-k:][::-1]).T
        s=''
        ponts_tfidf_norm =[]
        for j in range(k):
            if norma_vector[0,idxs[-(j+1)]] != 0:
                try:
                    s = s + feature_names[idxs[-(j+1)][0]] + ','
                except:
                    import pdb; pdb.set_trace()
                ponts_tfidf_norm.append(norma_vector[0,idxs[-(j+1)]])
        ponts_tfidf.append(ponts_tfidf_norm)
        keywords.append(s)

    return keywords,ponts_tfidf

def get_pontuations(norma, keyword_text, keyword_ementa, pont_tfidf_text, pont_tfidf_ementa):

    d_text = {keyword : pont.item() for keyword,pont in zip(keyword_text.split(',')[:-1][::-1],pont_tfidf_text)}
    d_ementa = {keyword : pont.item() for keyword,pont in zip(keyword_ementa.split(',')[:-1][::-1],pont_tfidf_ementa)}

    d_text_init = d_text.copy()
    d_ementa_init = d_ementa.copy()

    #d_ementa será modificado neste loop
    for key in d_text:
        if key not in d_ementa or d_text[key] > d_ementa[key]:
            d_ementa[key] = d_text[key]

    d_all = {**d_text, **d_ementa}

    for key in d_all.keys():
        if key in d_text_init and key in d_ementa_init:
            d_all[key] = 4 * d_all[key]

    d_all_rs = dict(sorted(list(d_all.items()), key=lambda x: x[1],reverse=True))
    #if norma == 'RDC 16/2014' : import pdb; pdb.set_trace()
    normas_norm=[]
    keywords_norm=[]
    ponts_norm=[]
    aux = keyword_text.split(',')[:-1]
    aux.extend(keyword_ementa.split(',')[:-1])
    count = dict(Counter(aux))
    normas_norm.extend([norma]*len(count))
    keywords_norm.extend(list(d_all_rs.keys()))
    ponts_norm.extend(list(d_all_rs.values()))
    #ponts_norm = [d_all_rs[keyword]*count[keyword] for keyword in count.keys()]

    return normas_norm, keywords_norm, ponts_norm


def get_keywords(k:int=10):
    '''
    This function outputs the keywords for each norm. This function also creates the file 'keywords.csv' witch
    aims the powerbi implementation.

    In 'keywords.csv' we have a pontuation for each keyword: the higher pontuation means that that keyword is really important
    '''
    keywords_text, ponts_tfidf_text = get_keywords_text(100)
    keywords_ementa, ponts_tfidf_ementa = get_keywords_ementa(10)

    data = pd.read_csv('interesting_norms.csv',sep='|',encoding='utf-8')
    data = data.drop(data.index[[16,24]])
    data = data.reset_index()
    del data['index']
    normas=[]
    keywords=[]
    ponts=[]
    for i,norma in enumerate(data.Norma):
        normas_norm, keywords_norm, ponts_norm = get_pontuations(norma, keywords_text[i], keywords_ementa[i],
                                                                ponts_tfidf_text[i], ponts_tfidf_ementa[i])
        normas.extend(normas_norm)
        keywords.extend(keywords_norm)
        ponts.extend(ponts_norm)

    dimensao_keywords = pd.DataFrame(zip(list(set(keywords)),list(range(len(keywords)))),columns=['keywords','key'])
    #dimensao_keywords = pd.DataFrame(df_export.keywords.unique())
    #dimensao_keywords.columns = ['keywords']
    dimensao_keywords.to_csv('dimensao_keywords.csv',sep='|',index=False)

    dic = dimensao_keywords.to_dict()['keywords']
    inv_dic = {v: k for k, v in dic.items()}

    df_export = pd.DataFrame(zip(normas,keywords),columns=['search','keywords'])
    #df_export.ponts = df_export.ponts.round(2)
    df_export.replace({'keywords' : inv_dic},inplace=True)
    df_export.to_csv('keywords.csv',sep='|',encoding='utf-8',index=False)

    keywords = []
    for keyword_text,keyword_ementa in zip(keywords_text,keywords_ementa):
        aux = []
        aux.extend(keyword_text.split(sep=','))
        aux.extend(keyword_ementa.split(sep=','))
        keywords.append(','.join(list(np.unique(aux)))[1:])

    return keywords
