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
from collections import Counter
#You have to install this package in order to be able to run the app
#pip install dash==1.6.1

df = pd.read_csv('interesting_norms.csv',sep='|',encoding='utf-8')
df = df.drop(df.index[[16,24]])
df = df.reset_index()
del df['index']
X = np.load('X_LM.npy')
X = np.delete(X, (16), axis=0)
X = np.delete(X, (24), axis=0)

dimensao_keywords = pd.read_csv('dimensao_keywords.csv',sep='|')
keywords = pd.read_csv('keywords.csv',sep='|')

keywords_list = list(set(dimensao_keywords.keywords))
keywords_list.sort()

keywords_dict = []
for i,keyword in enumerate(keywords_list):
    keywords_dict.append({'label':keyword,'value':keyword})


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([

    html.Div([
        html.H1(
            children='Mecanismo de Busca de Normas por Palavra Chave',
            style={
                'textAlign':'center',
                'color':'white',
                'backgroundColor': '#6c7e97'
            }
        )
    ]),

    html.Div([

        html.Label('Digite aqui as palavras chave:'),
        dcc.Dropdown(
            id = 'insert-keywords',
            options= keywords_dict,
            multi=True),

        html.Button('Buscar',id='button'),

        html.Label('\n'),
        dash_table.DataTable(
            id='table',
            columns = [
                {'name':'Norma','id':'Norma'},
                {'name':'Ementa','id':'Ementa'},
                {'name':'Link','id':'Link'},
                {'name':'Palavras Chave','id':'Palavras Chave'}],
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
                'backgroundColor': 'rgb(248, 248, 248)'}
                ]
        )
    ]),
])

@app.callback(
    Output(component_id='table',component_property='data'),
    [Input(component_id='button',component_property='n_clicks')],
    [State(component_id='insert-keywords',component_property='value')]
)
def search_keyword(n_clicks,user_keywords):

    if n_clicks is None: return []

    normas = []
    keywords_codes = []
    for user_keyword in user_keywords:
        key = dimensao_keywords.loc[dimensao_keywords.keywords == user_keyword].key.values[0]
        keywords_codes.append(key)
        normas.extend(keywords.loc[keywords.keywords == key].search.values)

    counter = {k: v for k, v in sorted(dict(Counter(normas)).items(), key=lambda item: item[1],reverse=True)}

    df_out = pd.DataFrame(columns=['Norma','Ementa','Texto Integral'])
    user_keywords_norma = []
    for norma,count in zip(counter.keys(),counter.values()):
        aux = df.loc[df.Norma == norma][['Norma','Ementa','Texto Integral']]
        s=''
        for user_keyword,keyword_code in zip(user_keywords,keywords_codes):
            norma_keywords = list(keywords.loc[keywords.search == norma].keywords)
            if keyword_code in norma_keywords: s = s+user_keyword+', '

        user_keywords_norma.append(s[:-2])
        df_out = df_out.append(aux)

    df_out.reset_index(inplace=True)
    del df_out['index']
    df_out.columns = ['Norma','Ementa','Link']
    df_out['Palavras Chave'] = user_keywords_norma
    return df_out.to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True)
