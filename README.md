# About the project
This is a project done by members of the IEEE-CIS UnB student chapter, [O Grupo de IA da UnB](http://medium.com/ieeecisunb) . Here we want to build a deep learning ṕowered search engine to help the management and consulting of legal texts. Specifically in this work, we are dealing with legal texts from ANEEL, a brazilian electricity regulatory agency.

The basic idea here is to get the vector representation, calculated by the encoder of the trained language model, and use cosine similarity to see what are de k most similar texts to a given text.

We're using fastai.

**Members**: Thiago Dantas, Matheus Costa, Vicente Moraes, Richard Junio and Guilherme Andrey.



# Describing each file in this repo:

**scraping.py**: this script does the scraping of the data we need. It consults the [website](http://biblioteca.aneel.gov.br/index.html) and gets info about all the available texts.

**scraping.csv**: this is the csv file created by scraping.py. It has more than 100K lines.

**download_useful_pdfs.py**: as the scraping.csv table has a lot of useless texts for the purpose of this project and it only has the link for the pdf file of each text, we need some code to download only the important pdfs. This is what this script does.

**scraping_filtered.csv**: csv file with only the useful texts. This csv file has something like 1500 lines.


**LM_csv_File_Creation.py**: this script reads the downloaded pdfs and writes them into a new csv, 'LanguageModelFile.csv' which is the csv that we are going to use to fine tune the language model.

**LanguageModelFile.csv**: csv file with the texts and all information from the norms that are useful to us.

**get_reps.ipynb**: this is the notebook used to train a language model and to extract the vector representation of each useful text.

**X_LM.npy**: this is a file that contains the vector representation for each text in 'LanguageModelFile.csv'.

**most_similar.py**: this script gets the K most similars texts to a given text.
