import BQ_utils
import pandas as pd
import numpy as np
import spacy
from nltk.stem import *
from joblib import Parallel, delayed
from google.cloud import bigquery
from google.oauth2 import service_account
import json
import os
stemmer = PorterStemmer()

# Google Cloud services
# file absent in repository for security
gcp_service_account_credentials_json_filename = 'epfl-course-f41b0ed796f9.json'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_service_account_credentials_json_filename
credentials = service_account.Credentials.from_service_account_file(gcp_service_account_credentials_json_filename, scopes=[
                                                                    'https://www.googleapis.com/auth/bigquery', 'https://www.googleapis.com/auth/drive'])
project_id = 'epfl-course'
bigquery_client = bigquery.Client(credentials=credentials, project=project_id)
bigquery_client = bigquery.Client()

nlp = spacy.load("en_core_web_sm")
all_stopwords = nlp.Defaults.stop_words
# Tip for quicker processing https://prrao87.github.io/blog/spacy/nlp/performance/2020/05/02/spacy-multiprocess.html#Read-in-New-York-Times-Dataset


def lemmatize_and_get_geo_pipe(doc):

    # Perform lemmatization and stopword removal in the clean text.
    # Extract named entities labeled as "GPE" - Geo Political Entities by spacy
    # Returns a list of lemmas and a list of GPEs

    lemma_list = [str(tok.lemma_).lower() for tok in doc
                  if tok.is_alpha and tok.text.lower() not in all_stopwords]
    stem_list = [stemmer.stem(lem) for lem in lemma_list]
    geo_tokens = list(
        set([ent.text for ent in doc.ents if ((ent.label_ == "GPE"))]))
    return lemma_list, stem_list, geo_tokens

# Utility functions for parallel processing


def chunker(iterable, total_length, chunksize):
    # Divide the rows into chunks for batch processing
    return (iterable[pos: pos + chunksize] for pos in range(0, total_length, chunksize))


def flatten(list_of_lists):
    "Flatten a list of lists to a combined list"
    return [item for sublist in list_of_lists for item in sublist]


def process_chunk(texts):
    preproc_pipe = []
    # using spacy pipes to process the data more efficiently
    for doc in nlp.pipe(texts, batch_size=20):
        preproc_pipe.append(lemmatize_and_get_geo_pipe(doc))
    return preproc_pipe

# Executing the processing on multiple threads


def preprocess_parallel(texts, chunksize=100, fun=process_chunk):
    executor = Parallel(
        n_jobs=7, backend='multiprocessing', prefer="processes")
    do = delayed(process_chunk)
    tasks = (do(chunk)
             for chunk in chunker(texts, len(df), chunksize=chunksize))
    result = executor(tasks)
    return flatten(result)


# PREPROCESSING EXECUTION
months = range(1, 13)
years = range(2015, 2020)

# process the data for every year and month separately (to fit in memory and allow self-contained parallelization)
for m in months:
    for y in years:
        query = '''SELECT
                    quoteId,
                    quotation
                    FROM
                    epfl-course.ada_project.quotes
                    WHERE
                    DATE(date) BETWEEN "{}-{}-01"
                    AND LAST_DAY(DATE "{}-{}-01", MONTH)'''.format(y, m, y, m)
        # for testing add "limit 10" at end
        df = BQ_utils.bq_execute_query(query, to_dataframe=True)
        df['geoNames_lemmas'] = preprocess_parallel(
            df['quotation'], chunksize=1000)
        df[['lemmas', 'stems', 'geoNames']] = pd.DataFrame(
            df['geoNames_lemmas'].tolist(), index=df.index)
        print("{}/{} rows in {}/{} contain geo annotations".format(
            len(df[df["geoNames"].map(lambda d: len(d)) > 0].index),
            len(df.index),
            m,
            y
        ))
        df = df.drop(['quotation', 'geoNames_lemmas'], axis=1)
        print(df.head(5))
        print(df.dtypes)

        # uploading file to BQ
        BQ_utils.upload_df_to_bq(
            df, 'epfl-course.ada_project.quote_preprocessed_spacy_with_geo')
