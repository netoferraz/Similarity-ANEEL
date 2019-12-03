import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
#import bib
import numpy as np
import pickle
from sklearn import preprocessing
from dash.exceptions import PreventUpdate
#You have to install this package in order to be able to run the app
#pip install dash==1.6.1

data = pd.read_csv('LanguageModelFile.csv',sep='|',encoding='utf-8',index_col=False)
X = np.load('X_LM.npy')
normas_list = list(data.Norma)
orgaos_list = list(data['Órgão de origem'].unique())

normas_dict = []
for i,norma in enumerate(normas_list):
    normas_dict.append({'label':norma,'value':norma})

orgaos_dict = []
for i,orgao in enumerate(orgaos_list):
    orgaos_dict.append({'label':orgao,'value':orgao})


external_stylesheets = ['https://drive.google.com/uc?export=download&id=1UcwWovPkD6QAtC5N_-k3PfW8u8V3uZzV']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([

    html.Div([
        html.Header(
            children='Mecanismo de Busca de Normas Similares',
            id='header'
        )
    ]),

    html.Div([

        html.Label('Selecione aqui a norma desejada',style={
            'color':'#2b2b2b',
            'fontSize':'26px'
        }),
        dcc.Dropdown(
            id = 'select-norm',
            options= normas_dict),

        html.Label('Selecione aqui o órgão da norma',style={
            'color':'#2b2b2b',
            'fontSize':'26px'}
        ),
        dcc.Dropdown(
            id = 'select-orgao',
            options= orgaos_dict),

        html.Label('Indique o número de normas de output',style={
            'color':'#2b2b2b',
            'fontSize':'26px'}),
        dcc.Input(id='n_normas',type='text',value='10'),

        html.Button('Buscar',id='button'),

        html.Label('',style={
            'color':'#2b2b2b',
            'fontSize':'20px'
        }),
        dash_table.DataTable(
            id='table',
            columns = [
                {'name':'Norma','id':'Norma'},
                {'name':'Ementa','id':'Ementa'},
                {'name':'Link','id':'Link'}],
            #fixed_rows={ 'headers': True},
            data = [],
            style_data = {
                'whiteSpace':'normal',
                'height':'auto',
                'backgroundColor': '#eeeeee',
                'border':'1px solid #4a5769',
                'fontSize':'20px'
                },
            style_table={
                'maxHeight': '370px',
                'maxWidth': '900px',
                'overflowY': 'auto',
                'color':'#2b2b2b',
                'overflowX': 'auto'},
             style_cell={'textAlign': 'left'},
             style_header={
                'backgroundColor':'#6c7e97',
                'textAlign':'center',
                'fontWeight':'bold',
                'fontSize':'22px',
                'color':'#fff'},
            style_data_conditional=[{
                'if': {'row_index': 'odd'},
                'backgroundColor': '#eeeeee'},]
        )
    ],
        style={
            'padding':'20px',
        }    
    ),
])

@app.callback(
    Output(component_id='table',component_property='data'),
    [Input(component_id='button',component_property='n_clicks')],
    [State(component_id='select-norm',component_property='value'),
     State(component_id='select-orgao',component_property='value'),
     State(component_id='n_normas',component_property='value')]
)
def getKSimilarTexts(n_clicks,norma,orgao,k):

    if n_clicks is None: return []
    if norma is None: return []
    if k is None: return []

    k = int(k)
    #import pdb; pdb.set_trace()
    data = pd.read_csv('LanguageModelFile.csv',sep='|',encoding='utf-8',index_col=False)
    X = np.load('X_LM.npy')

    #All features with 0 mean and std 1
    X = preprocessing.scale(X)

    #Making sure that all vectors have unit magnitude
    for i in range(X.shape[0]):
        Xi = X[i,:]
        X[i,:] = Xi/(np.sum(Xi**2)**0.5)

    #import pdb; pdb.set_trace()
    idx = np.where((data.Norma==norma).values * (data['Órgão de origem']==orgao).values)[0]
    X_n = X[idx]

    aux = np.zeros(X.shape) + X_n
    similarity = np.sum(aux*X,axis=1)

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
    return out[['Norma','Ementa','Texto Integral']].to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)
