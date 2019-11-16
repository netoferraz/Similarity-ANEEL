import pandas as pd
import os, requests, re, time, shutil

#read the csv file
df = pd.read_csv('scraping.csv')

#checks if there are missing links
idxs = pd.isna(df['Texto Integral'])

#takes out the rows with missing links
df = df.loc[~idxs]

#takes out all the non vigent norms
df = df.loc[df['Situação'] == 'NÃO CONSTA REVOGAÇÃO EXPRESSA']

#checks the kinds of legal texts
df['Tipo'] = df.Norma.apply(lambda x: x[:3])

kinds = list(df.Tipo)
kinds_tokeep = ['REN','RES']
idxs = [kinds[i] in kinds_tokeep for i in range(len(kinds))]
df = df.loc[idxs]

#adds the name of the downloaded pdf
df['Filename'] = df['Texto Integral'].apply(lambda x: re.sub(r'http.*/','',x))

#deletes columns of unique values
del df['Material'], df['Esfera'], df['Situação']

#saves the filtered csv
df.to_csv('scraping_filtered.csv',index=False)

print('Total number of norms to download: ' + str(df.shape[0]))

#gets all valid urls
urls = list(df['Texto Integral'])

#If there is a 'Data' directory, removes it. And creates a empty one
if os.path.isdir('Data'):
    shutil.rmtree('Data')
    os.mkdir('Data')
else:
    os.mkdir('Data')

start = time.time()
for i, url in enumerate(urls):
    # Attempts to download link 3 times
    try:
        file = requests.get(url)
    except Exception as err:
        # Logs failed downloads
        print(err)
        with open("failed_downloads.txt", "a") as wf:
            wf.write(f"NUMBER: {i}. URL:{url}\n")
    else:
        # Writes data if download is successful
        filename = re.sub('http.*/','',url)
        open('Data/'+filename,'wb').write(file.content)
        if (i%100 == 0) and (i != 0):
            end = time.time()
            elpsd = end - start
            print(str(i) + ' out of ' + str(len(urls)))
            print('Elapsed time to download ' + str(i) + ' pdfs: ' + str(elpsd) + 's')
        time.sleep(0.1)
