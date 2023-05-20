from flask import session, redirect, url_for, render_template, request
from . import main
from .forms import LoginForm
from .sso_gen import generate_looker_url


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


@main.route('/chat')
def chat():
    """Chat room. The user's name and room must be stored in
    the session."""
    dash_id = 'cortex-demo-genai::sap_order_to_cash_o2c_04_sales_performanceperformance_tuning'    
    sso_url = generate_looker_url(dash_id).url
    name = session.get('name', '')
    room = session.get('room', '')
    if name == '' or room == '':
        return redirect(url_for('.index'))
    return render_template('chat.html', looker_sso_url=sso_url, name=name, room=room)

@main.route('/input_msg', methods=['GET', 'POST'])
def input_msg():
    msg = request.args.get('msg')
    data = {"input":msg, "response":msg+' simple response from server'}
    return data
