import pandas as pd
import os, requests, re, time, shutil
import PyPDF2

df = pd.read_csv("LanguageModelFile.csv",sep='|')
#import pdb; pdb.set_trace()
df = df.dropna()
del df['Unnamed: 0']
idxs = df.Tipo != 'RES'
df = (df.loc[idxs]).reset_index()
del df['index']
urls = list(df['Texto Integral'])

pdf_list = list(df['Filename'])

def getText2PDF(pdfFileName):
    pdf_file=open("Datafiltered/" + pdfFileName,'rb')
    read_pdf=PyPDF2.PdfFileReader(pdf_file)
    text=[]
    for i in range(0,read_pdf.getNumPages()):
        text.append(read_pdf.getPage(i).extractText())
    return ('\n'.join (text).replace("\n",''))

list_txt = []
for i in range(len(pdf_list)):
    try:
      list_txt.append(getText2PDF(pdf_list[i]))
    except:
      print("Erro na conversão do arquivo " + pdf_list[i])
      list_txt.append('Arquivo corrompido.')

df['Texto Extraído'] = pd.Series(list_txt)
df.to_csv("interesting_norms.csv", sep = "|",index=False)
