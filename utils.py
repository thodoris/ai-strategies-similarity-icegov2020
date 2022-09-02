# Imports
import re
import pandas as pd
import os, sys
import glob
import string
import pickle
from pathlib2 import Path
from gensim.summarization import summarize,keywords

def load_documents(eu_only=False):
    eu_list = ['denmark','france','germany','italy','sweden','uk','finland','luxembourg']
    file_list = glob.glob(os.path.join(os.getcwd(), ".\\txts\\clean\\"+ "*.txt"))
            
    corpus = {}

    for file_path in file_list:
        filename = Path(Path(file_path).stem).stem
        if not eu_only or (eu_only and filename in eu_list):
            with open(file_path,encoding='utf-8',newline=None) as f_input:
                text = f_input.read().replace("\n", " ")
                clean_text = "".join([c for c in text if c.isprintable()])
                corpus[filename]= clean_text

    return corpus  

#clean data
def clean_document(doc,remove_digits=False , remove_non_printable=False):

   
    # Remove Emails
    doc = re.sub('\S*@\S*\s?', '', doc) 

    #Remove Links & Urls
    doc = re.sub('http\S+', ' ', doc) 

    # Remove new line characters
    doc = re.sub('\s+', ' ', doc) 

    # Remove distracting single quotes
    doc = re.sub("\'", "", doc)
    
    # Remove digits
    if (remove_digits):
        doc = re.sub('\d+', '', doc)

    # Remove non printable chars
    if (remove_non_printable):
        doc = re.sub('[^a-zA-z\s]', '', doc)

    return doc

def get_corpus_dataframe(eu_only=False,allowed_postags_filter=['NOUN', 'ADJ', 'VERB', 'ADV']):
	savedmodel_filename = f'documents{"_euonly" if eu_only else ""}'
	if os.path.isfile(savedmodel_filename+'.pkl'):
		df = pd.read_pickle(savedmodel_filename+'.pkl')
	else:
		documents = load_documents(eu_only=eu_only)
		df = pd.DataFrame.from_dict(documents, orient='index', columns=['content'])
		df.index.names = ['country']

		# clean content
		df['clean_content'] = df['content'].map(lambda doc: clean_document(doc,remove_digits=True))   

		# calculate keywords using TExtRank
		df['keywords'] = df['content'].map(lambda doc: keywords(doc, ratio=0.2,words=20,lemmatize=True,pos_filter=allowed_postags_filter))  #the ratio will be ignored 
		df['clean_keywords'] = df['clean_content'].map(lambda doc: keywords(doc, ratio=0.2,words=20,lemmatize=True,pos_filter=allowed_postags_filter))  #the ratio will be ignored 

		
		# calculate summaries using TExtRank
		df['summary'] = df['content'].map(lambda doc: summarize(doc, ratio=0.2,word_count=200))  #the ratio will be ignored 
		df['clean_summary'] = df['clean_content'].map(lambda doc: summarize(doc, ratio=0.2,word_count=200))  #the ratio will be ignored 

		#save pickle (for reload)
		df.to_pickle(savedmodel_filename+'.pkl')
		
		#save excel
		df_export = df.copy()
		df_export['content'] = df_export['content'].str.slice(0,32766)
		df_export['clean_content'] = df_export['clean_content'].str.slice(0,32766)
		df_export.to_excel(savedmodel_filename+'.xls')
	
	return df

def pandas_highlight_max(data, color='yellow'):
    '''
    highlight the maximum in a Series or DataFrame
    '''
    attr = 'background-color: {}'.format(color)
    if data.ndim == 1:  # Series from .apply(axis=0) or axis=1
        is_max = data == data[data<1].max()
        return [attr if v else '' for v in is_max]
    else:  # from .apply(axis=None)
        is_max = data == data[data<1].max().max() 
        return pd.DataFrame(np.where(is_max, attr, ''),
                            index=data.index, columns=data.columns)

def pandas_highlight_min(data, color='yellow'):
    '''
    highlight the maximum in a Series or DataFrame
    '''
    attr = 'background-color: {}'.format(color)
    if data.ndim == 1:  # Series from .apply(axis=0) or axis=1
        is_min = data == data[data>0].min()
        return [attr if v else '' for v in is_min]
    else:  # from .apply(axis=None)
        is_min = data == data[data>0].min() 
        return pd.DataFrame(np.where(is_min, attr, ''),
                            index=data.index, columns=data.columns)