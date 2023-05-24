from flask import session, redirect, url_for, render_template, request
from . import main
from vertexai.preview.language_models import TextEmbeddingModel
from match_looker_content import parse_search_input as psi
from looker_metadata import create_looker_embeddings as cle
import pandas as pd
import numpy as np
import looker_sdk
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
looker_embeddings = create_looker_embeddings()


@main.route('/', methods=['GET', 'POST'])
def index():
    return redirect('/chat')


@main.route('/chat', methods=['GET', 'POST'])
def chat():
    """Chat room. The user's name and room must be stored in
    the session."""
    dash_id = 'cortex-demo-genai::sap_order_to_cash_o2c_04_sales_performance_tuning'
    sso_url = generate_looker_url(dash_id).url
    name = session.get('name', '')
    room = session.get('room', '')
    if name == '' or room == '':
        return redirect(url_for('.index'))
    return render_template('chat.html',
                           looker_sso_url=sso_url,
                           name='https://demo.looker.com/browse',
                           room='https://demo.looker.com/browse')


def match_query_to_content(query_embeddings, looker_embeddings):
    if os.path.isfile('looker_metadata.csv'):
        looker_metadata = pd.read_csv('looker_metadata.csv')
    else:
        looker_metadata = gcm.GetDashboardMetadata(sdk).execute()
        looker_metadata.to_csv('looker_metadata.csv')
    looker_metadata = pd.read_csv('looker_metadata.csv')

    scores = np.dot(query_embeddings, looker_embeddings.T)
    looker_metadata['similarity_score'] = scores
    return_df = looker_metadata[[
        'dashboard_id', 'dash_title', 'embedding_list', 'similarity_score', 'element_title']]
    return_df = return_df.sort_values(by='similarity_score', ascending=False)
    return return_df


@main.route('/input_msg', methods=['GET'])
def input_msg():
    query = request.args.get('msg')
    if not query:
        query = 'what is my sales dashboard'
    qembeddings = create_query_embeddings(query)
    results = match_query_to_content(
        query_embeddings=qembeddings, looker_embeddings=looker_embeddings)
    top_result = results.iloc[0]
    results_id = top_result['dashboard_id']
    results_title = top_result['dash_title']
    element_title = top_result['element_title']
    top_dash = results[['dashboard_id', 'dash_title']].iloc[0:10]
    top_dash = top_dash.drop_duplicates()
    top_dash = top_dash.to_html()

    dashboard_summary = psi.dashboard_summary_extraction(query_list=top_result['embedding_list'])

    textbox_return = {"input": query,
                      "response": f'your best result is id {results_id} of dashboad {results_title}',
                      "best_element": f'your best element title is {element_title}',
                      "top_n_dashboards": top_dash,
                      "dashboard_summary": dashboard_summary}
    return textbox_return
