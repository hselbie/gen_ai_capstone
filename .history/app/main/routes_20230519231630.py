from flask import session, redirect, url_for, render_template, request
from . import main
from .forms import LoginForm
from .sso_gen import generate_looker_url
from vertexai.preview.language_models import TextEmbeddingModel
from looker_metadata import get_content_metadata as gcm
import pandas as pd
import looker_sdk

ini = '/usr/local/google/home/hugoselbie/code_sample/py/ini/Looker_23_3.ini'
sdk = looker_sdk.init40(config_file=ini)


@main.route('/', methods=['GET', 'POST'])
def index():
    """Login form to enter a room."""
    form = LoginForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        session['room'] = form.room.data
        return redirect(url_for('.chat'))
    elif request.method == 'GET':
        form.name.data = session.get('name', '')
        form.room.data = session.get('room', '')
    return render_template('index.html', form=form)


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
                           name=name, 
                           room=room)

def match_query_to_content(query):
    if not query:
        query='what is my sales dashboard'
    # get_content_metadata = gcm.GetDashboardMetadata(sdk)
    # looker_metadata = get_content_metadata.execute()
    # looker_metadata.to_csv('looker_metadata.csv')
    looker_metadata = pd.read_csv('looker_metadata.csv')

    embedding_model = TextEmbeddingModel.from_pretrained(
        "textembedding-gecko@001")
    recommended = gcm.CreateLookerEmbedding(
        sdk=sdk, looker_metadata=looker_metadata, 
        embedding_model=embedding_model, 
        query_question=query).execute()

    looker_metadata['similarity_score'] = recommended
    return_df = looker_metadata[[
        'dashboard_id', 'dash_title', 'embedding_list', 'similarity_score']]
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

    textbox_return = {"input": query, "response": f'your result is id {results_id} of dashboad {results_title}'
    return textbox_return
