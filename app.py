import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import pickle
from sklearn import preprocessing
from dash.exceptions import PreventUpdate
#You have to install this package in order to be able to run the app
#pip install dash==1.6.1

df = pd.read_csv('interesting_norms.csv',sep='|',encoding='utf-8')
X = np.load('X_LM.npy')
normas_list = list(df.Norma)
orgaos_list = list(df['Órgão de origem'].unique())

normas_dict = []
for i,norma in enumerate(normas_list):
    normas_dict.append({'label':norma,'value':norma})

orgaos_dict = []
for i,orgao in enumerate(orgaos_list):
    orgaos_dict.append({'label':orgao,'value':orgao})


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([

    html.Div([
        html.H1(
            children='Mecanismo de Busca de Normas Similares',
            style={
                'textAlign':'center',
                'color':'white',
                'backgroundColor': '#6c7e97'
            }
        )
    ]),

    html.Div([

        html.Label('Selecione aqui a norma desejada:'),
        dcc.Dropdown(
            id = 'select-norm',
            options= normas_dict),

        html.Label('Selecione aqui a o órgão da norma:'),
        dcc.Dropdown(
            id = 'select-orgao',
            options= orgaos_dict),

        html.Label('Indique o número de normas a serem mostradas:'),
        dcc.Input(id='n_normas',type='text',value='10'),

        html.Button('Buscar',id='button'),

        html.Label('\n'),
        dash_table.DataTable(
            id='table',
            columns = [
                {'name':'Norma','id':'Norma'},
                {'name':'Similaridade','id':'Similaridade'},
                {'name':'Ementa','id':'Ementa'},
                {'name':'Link','id':'Link'},
                {'name':'Size','id':'Size'}],
            #fixed_rows={ 'headers': True},
            data = [],
            style_data = {
                'whiteSpace':'normal',
                'height':'auto'},
            style_table={
                'maxHeight': '370px',
                #'maxWidth': '700px',
                'overflowY': 'scroll',
                'overflowX': 'scroll'},
             style_cell={'textAlign': 'left'},
             style_header={
                'backgroundColor':'#6c7e97',
                'fontWeight':'bold',
                'color':'white'},
            style_data_conditional=[{
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'},
                {'if': {'column_id':'Similaridade'},
                'textAlign':'center'}
                ]
        )
    ]),
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

    data = pd.read_csv('interesting_norms.csv',sep='|',encoding='utf-8')

    X = np.load('X_LM.npy')

    #All features with 0 mean and std 1
    X = preprocessing.scale(X)

    #Making sure that all vectors have unit magnitude
    for i in range(X.shape[0]):
        Xi = X[i,:]
        X[i,:] = Xi/(np.sum(Xi**2)**0.5)

    #import pdb; pdb.set_trace()
    idx = np.where(data.Norma==norma)[0]
    if len(idx) > 1:
        if orgao is None: return []
        idx = np.where((data.Norma==norma).values * (data['Órgão de origem']==orgao).values)[0]
    X_n = X[idx]

    aux = np.zeros(X.shape) + X_n
    similarity = np.sum(aux*X,axis=1)

    idxs_max = similarity.argsort()[-k:][::-1]
    #idxs_max = idxs_max[1:]
    #import pdb; pdb.set_trace()
    out = data.loc[idxs_max]
    out = out.reset_index()
    del out['index']
    normas = list(out.Norma)
    ementas = list(out.Ementa)
    #import pdb; pdb.set_trace()
    similarity = (similarity + 1)/2
    similarity.sort()
    similarity = similarity[-k:][::-1]
    out['Link'] = out['Texto Integral']
    out['Similaridade'] = (pd.Series(similarity)).round(4)
    # DEBUG: i dont have to keep this column but it helps with the
    texts = list(out['Texto Extraído'])
    out['Size'] = out['Texto Extraído'].apply(lambda x: len(x))
    return out[['Norma','Similaridade','Ementa','Link','Size']].to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)
