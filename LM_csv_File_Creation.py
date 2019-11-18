import pandas as pd
import os, requests, re, time, shutil
import PyPDF2

df = pd.read_csv("scraping_filtered.csv")

pdf_list = os.listdir("Datafiltered/")

def getText2PDF(pdfFileName):
    pdf_file=open("Datafiltered/" + pdfFileName,'rb')
    read_pdf=PyPDF2.PdfFileReader(pdf_file)
    text=[]
    for i in range(0,read_pdf.getNumPages()):
        text.append(read_pdf.getPage(i).extractText())
    return ('\n'.join (text).replace("\n",''))
    
    
list_txt = []
lista_erros = []
for i in range(len(pdf_list)):
    try:
      list_txt.append(getText2PDF(pdf_list[i]))
    except:
      print("Erro na conversão do arquivo " + pdf_list[i])
      lista_erros.append(pdf_list[i])

newpdf_list = [x for x in pdf_list if x not in lista_erros]
listabool = []
for i in range(len(df)):
  listabool.append(df.iloc[i, 7] in newpdf_list)
dfbool = pd.DataFrame(listabool)
df["exists"] = dfbool
df = df[df["exists"] == True]

del df["exists"]

dflist = pd.DataFrame(list_txt)
df["Texto Extraído"] = dflist
df.to_csv("LanguageModelFile.csv", sep = "|")

verif = pd.read_csv("LanguageModelFile.csv", sep = "|")

print(verif.shape)

