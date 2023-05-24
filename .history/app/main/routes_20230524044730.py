from flask import session, redirect, url_for, render_template, request
from . import main
from .forms import LoginForm
from .sso_gen import generate_looker_url
from vertexai.preview.language_models import TextEmbeddingModel
from looker_metadata import create_looker_embeddings as cle
import pandas as pd
import numpy as np
import looker_sdk
import os

ini = '/usr/local/google/home/hugoselbie/code_sample/py/ini/demo.ini'
sdk = looker_sdk.init40(config_file=ini)


@main.route('/', methods=['GET', 'POST'])
def index():
    return redirect('/chat')


@main.route('/chat',methods=['GET', 'POST'])
def chat():
    """Chat room. The user's name and room must be stored in
    the session."""
    dash_id = 'cortex-demo-genai::sap_order_to_cash_o2c_04_sales_performanceperformance_tuning'
    sso_url = generate_looker_url(dash_id).url
    name = session.get('name', '')
    room = session.get('room', '')
    if name == '' or room == '':
        return redirect(url_for('.index'))
    return render_template('chat.html', 
                           looker_sso_url=sso_url, 
                           name='https://demo.looker.com/browse', 
                           room='https://demo.looker.com/browse')

looker_embeddings = []
def match_query_to_content(query):
    if not query:
        query='what is my sales dashboard'
    if os.path.isfile('looker_metadata.csv'):
        looker_metadata = pd.read_csv('looker_metadata.csv')
    else:
        looker_metadata= gcm.GetDashboardMetadata(sdk).execute()
        looker_metadata.to_csv('looker_metadata.csv')
    looker_metadata = pd.read_csv('looker_metadata.csv')

    embedding_model = TextEmbeddingModel.from_pretrained(
        "textembedding-gecko@001")
    recommended = cle.CreateLookerEmbedding(
        sdk=sdk, looker_metadata=looker_metadata, 
        embedding_model=embedding_model, 
        query_question=query)
    if len(looker_embeddings) != 0: 
        looker_embeddings = recommended.generate_looker_embeddings()
    query_embeddings = recommended.generate_query_embeddings()

    scores = np.dot(query_embeddings,looker_embeddings.T)

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
    results = match_query_to_content(query)
    results_id = results['dashboard_id'].iloc[0]
    results_title = results['dash_title'].iloc[0]
    xyz = results['element_title'].iloc[0]
    top_dash = results[['dashboard_id', 'dash_title']].iloc[0:10]
    top_dash = top_dash.drop_duplicates()

    top_dash = top_dash.to_html()

    textbox_return = {"input": query, 
                      "response": f'your best result is id {results_id} of dashboad {results_title}',
                      "best_element": f'your best element title is {xyz}',
                      "top_n_dashboards": top_dash}
    return textbox_return
