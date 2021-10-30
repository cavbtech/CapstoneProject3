## overall program for multi class model
import glob
import re
import string
from sklearn.svm import LinearSVC
import nltk
import pandas as pd
import pickle
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from textblob import TextBlob
import json

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')
stop_words_  = set(stopwords.words('english'))
wn           = WordNetLemmatizer()
my_sw        = ['make', 'amp',  'news','new' ,'time', 'u','s', 'photos',  'get', 'say']
csv_dtype_dict={"id": "string",
                "published_time": "string",
                "title":"string",
                "summary":"string",
                "source":"string",
                "category":"string",
                "text":"string"}


# Read Json file
def readCSVDirectory(path):
    print(f"readCSVDirectory i.,e cleansed data path={path}")
    files = glob.glob(path+"/*.csv")
    print(f"files {files}")
    df = pd.DataFrame()
    for f in files:
        print(f"reading csv file ={f}")
        csv = pd.read_csv(f,
                          error_bad_lines=False,
                          dtype=csv_dtype_dict) ##drop the bad lines may too many columns than expected
        df = df.append(csv)
    return df

## Remove  unnecessary words
def black_txt(token):
    return  token not in stop_words_ and token not in list(string.punctuation)  and len(token)>2 and token not in my_sw

## This function cleans the text for incorrect words and datavol
def cleanText(text):
    clean_text=[]
    clean_text2=[]
    text = re.sub("'","",text) #remove apostrophe
    text = re.sub("(\\d|\\W)+"," ",text)
    clean_text = [wn.lemmatize(word, pos="v") for word in word_tokenize(text.lower()) if black_txt(word)]
    clean_text2 = [word for word in clean_text if black_txt(word)]
    return " ".join(clean_text2)

# Polarity: to check the sentiment of the text
def polarity_txt(text):
    return TextBlob(text).sentiment[0]
# Subjectivity: to check if text is objective or subjective
def subj_txt(text):
    return  TextBlob(text).sentiment[1]
# Len: The number of word in the text
def len_text(text):
    if len(text.split())>0:
         return len(set(cleanText(text).split())) / len(text.split())
    else:
         return 0

# Next we are going to create some news variables columns (like metadata) to try to improve the quality of our classifier
# with the help of textblob package, we will create
# df_news.columns


#Traing the Model
## This function first cleans the news datavol and then fits the datavol for training
def trainModel(df_news):

    # df_news['text'] = df_news['title'] + " " + df_news['summary']
    #df_news['text'] = df_news['text'].apply()
    df_news['text'] = df_news['text'].apply(cleanText)
    df_news['polarity'] = df_news['text'].apply(polarity_txt)
    df_news['subjectivity'] = df_news['text'].apply(subj_txt)
    df_news['len'] = df_news['text'].apply(lambda x: len(x))

    X       =   df_news[['text', 'polarity', 'subjectivity','len']]
    y       =   df_news['category']
    encoder =   LabelEncoder()
    y       = encoder.fit_transform(y)

    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y)
    v = dict(zip(list(y), df_news['category'].to_list()))

    # text_clf = Pipeline(
    #     [('vect', CountVectorizer(analyzer="word", stop_words="english")), ('tfidf', TfidfTransformer(use_idf=True)),
    #      ('clf', MultinomialNB(alpha=.01))])
    text_clf = Pipeline(
        [('vect', CountVectorizer(analyzer="word", stop_words="english")), ('tfidf', TfidfTransformer(use_idf=True)),
         ('clf', LinearSVC())])

    text_clf.fit(x_train['text'].to_list(), list(y_train))
    return (text_clf,v)


## F1-metrics, ROC and AUC metrics are to used as the data is imbalanaced
## Can we identify other models?
## Compare various models and explanation of why MultinomialNB has been used
## Deep learning also needs to be checked
## Accuracy to be compared Deep learning vs Machine learn


# Saving the Model
def saveModel(model_output_dir, clfandvector):
    with open(model_output_dir+'/model.pkl','wb') as f:
        pickle.dump(clfandvector[0], f)

    with open(model_output_dir+'/vectorCategory.pkl', 'wb') as f:
        print(f"dictionary={clfandvector[1]}")
        pickle.dump(clfandvector[1], f)


# Main function to start the app when main.py is called
def generateSaveModel(cleansed_output_dir,model_output_dir):
    df_news         = readCSVDirectory(cleansed_output_dir)
    print(df_news.head(5))
    clfandvector    = trainModel(df_news)
    saveModel(model_output_dir,clfandvector)
