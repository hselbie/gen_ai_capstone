from flask import session, redirect, url_for, render_template, request
from . import main
from vertexai.preview.language_models import TextEmbeddingModel
import chromadb
from match_looker_content import parse_search_input as psi
from looker_metadata import create_looker_embeddings as cle
import pandas as pd
import numpy as np
import looker_sdk
from ast import literal_eval
import os


def create_looker_embeddings():
    if os.path.isfile('looker_metadata.csv'):
        looker_metadata = pd.read_csv('looker_metadata.csv')
    else:
        looker_metadata = gcm.GetDashboardMetadata(sdk).execute()
        looker_metadata.to_csv('looker_metadata.csv')
    looker_metadata = pd.read_csv('looker_metadata.csv')

    embedding_model = TextEmbeddingModel.from_pretrained(
        "textembedding-gecko@001")
    recommended = cle.CreateLookerEmbedding(
        sdk=sdk, looker_metadata=looker_metadata,
        embedding_model=embedding_model,
        query_question='test')
    looker_embeddings = recommended.generate_looker_embeddings()
    return looker_embeddings


def create_query_embeddings(query):
    if os.path.isfile('looker_metadata.csv'):
        looker_metadata = pd.read_csv('looker_metadata.csv')
    else:
        looker_metadata = gcm.GetDashboardMetadata(sdk).execute()
        looker_metadata.to_csv('looker_metadata.csv')
    looker_metadata = pd.read_csv('looker_metadata.csv')

    if not query:
        query = 'what is my sales dashboard'
    embedding_model = TextEmbeddingModel.from_pretrained(
        "textembedding-gecko@001")
    recommended = cle.CreateLookerEmbedding(
        sdk=sdk, looker_metadata=looker_metadata,
        embedding_model=embedding_model,
        query_question=query)
    query_embeddings = recommended.generate_query_embeddings()
    return query_embeddings


ini = '/usr/local/google/home/hugoselbie/code_sample/py/ini/demo.ini'
sdk = looker_sdk.init40(config_file=ini)
# looker_embeddings = create_looker_embeddings()
if os.path.isfile('looker_metadata.csv'):
    looker_metadata = pd.read_csv('looker_metadata.csv')
else:
    looker_metadata = gcm.GetDashboardMetadata(sdk).execute()
    looker_metadata.to_csv('looker_metadata.csv')
looker_metadata = pd.read_csv('looker_metadata.csv')
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="looker_embeddings")
for index, embed_list in enumerate(looker_metadata['embedding_list'].to_list()):
    total = len(looker_metadata['embedding_list'].to_list())
    dash_id = str(looker_metadata['dashboard_id'].iloc[index])
    print(f'{index}/{total}')
    collection.add(
        documents=embed_list,
        metadatas=[{"dash_id": dash_id,
                    "element_title": looker_metadata['element_title'].iloc[index]}],
        ids=[f'{index}'])




@main.route('/', methods=['GET', 'POST'])
def index():
    return redirect('/chat')


@main.route('/chat', methods=['GET', 'POST'])
def chat():
    """Chat room. The user's name and room must be stored in
    the session."""
    sso_url= 'cortex-demo-genai::sap_order_to_cash_o2c_04_sales_performance_tuning'
    name = session.get('name', '')
    room = session.get('room', '')
    if name == '' or room == '':
        return redirect(url_for('.index'))
    return render_template('chat.html',
                           looker_sso_url=sso_url,
                           name='https://demo.looker.com/browse',
                           room='https://demo.looker.com/browse')

@main.route('/input_msg', methods=['GET'])
def input_msg():
    query = request.args.get('msg')
    if not query:
        query = 'what is my sales dashboard'
    result = collection.query(
        query_texts=[query],
        n_results=5)

    top_result = literal_eval(result['documents'][0][0])[0]
    results_id = result['metadatas'][0][0]['dash_id']
    results_title = literal_eval(result['documents'][0][0])[0]
    element_title = result['metadatas'][0][0]['element_title']
    top_dash = pd.DataFrame(result['metadatas'][0])
    top_dash = top_dash.to_html()

    dashboard_summary = psi.dashboard_summary_extraction(query_list=top_result)

    textbox_return = {"input": query,
                      "response": f'your best result is id {results_id} of dashboad {results_title}',
                      "best_element": f'your best element title is {element_title}',
                      "top_n_dashboards": top_dash,
                      "dashboard_summary": dashboard_summary}
    return textbox_return
