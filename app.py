from flask_login import login_user, current_user, logout_user, login_required
from flask import render_template, url_for, flash, redirect, request, Response
from flask_socketio import SocketIO, send
from wtforms import TextField, Form

from datetime import datetime
import os
import json

from SV import app, db
from SV.models import User, TradingIdea
from SV.users.forms import LoginForm, RegistrationForm, UpdateUserForm
from SV.users.picture_handler import add_profile_pic
from utils.db_manage import std_db_acc_obj, QuRetType
from utils.fetchData import fetchSignals, fetchTechnicals, fetchOwnership, sp500evol
from utils.graphs import makeOwnershipGraph, lineNBSignals
from utils.db_manage import std_db_acc_obj
from app_signals import page_signals

import plotly
import plotly.graph_objs as go

strToday    = str(datetime.today().strftime('%Y-%m-%d'))
magickey    = os.environ.get('magickey')
socketio    = SocketIO(app, cors_allowed_origins='*')

app.register_blueprint(page_signals)


class SearchForm(Form):
    stock               = TextField('Insert Stock', id='stock_autocomplete')
    nbRows              = TextField('Enter n° rows', id='numberRows')
    date_input          = TextField('Enter Signal Date', id='date_input')
    reset               = TextField('Reset', id='reset')
    getcsv              = TextField('Download', id='getcsv')
    mW                  = TextField('mW', id='mW')
    validChartSignal    = TextField('validChartSignal', id='validChartSignal')


@socketio.on('message')
def handleMessage(msg):
	print('Message: ' + msg)
	send(msg, broadcast=True)


@app.route('/')
def home():
    return render_template('home.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    form            = RegistrationForm()
    formW           = SearchForm(request.form)
    magic           = formW.mW.data
    
    if form.validate_on_submit():
        if magic==magickey:
            user = User(email       = form.email.data,
                        username    = form.username.data,
                        password    = form.password.data)

            db.session.add(user)
            db.session.commit()
            flash('Thanks for registering! Now you can login!')
            return redirect(url_for('login'))
        else:
            return render_template('register.html', form=form, \
            formW=formW,magics=False)


    return render_template('register.html', form=form, \
    formW=formW, magics=True)


@app.route('/welcome')
@login_required
def welcome_user():
    return render_template('welcome_user.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You logged out!')
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():

    print('Logging in. . .')
    form = LoginForm()

    if form.validate_on_submit():
        # Grab the user from our User Models table
        user = User.query.filter_by(email=form.email.data).first()

        # Check that the user was supplied and the password is right
        # The verify_password method comes from the User object
        # https://stackoverflow.com/questions/2209755/python-operation-vs-is-not

        if user is None:
            print('User is None')
            return render_template('login.html', form = form, log_error = True)
        elif user.check_password(form.password.data) and user is not None:
            # Log in the user

            login_user(user)
            # If a user was trying to visit a page that requires a login
            # flask saves that URL as 'next'.
            next = request.args.get('next')

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if next == None or not next[0] == '/':
                next = url_for('welcome_user')

            return redirect(next)
    return render_template('login.html', form=form, log_error = False)


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():

    form = UpdateUserForm()

    if form.validate_on_submit():

        if form.picture.data:
            username = current_user.username
            pic = add_profile_pic(form.picture.data,username)
            current_user.profile_image = pic

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('User Account Updated')
        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    profile_image = url_for('static', filename='profile_pics/' + current_user.profile_image)
    
    return render_template('account.html', profile_image=profile_image, form=form)


@app.route("/<username>")
def user_posts(username):
    page        = request.args.get('page',1,type=int)
    user        = User.query.filter_by(username=username).first_or_404()
    blog_posts  = TradingIdea.query.filter_by(author=user).order_by(TradingIdea.date.desc()).paginate(page=page, per_page=5)
    
    return render_template('user_blog_posts.html', blog_posts=blog_posts, user=user)


####------Standard functions and arguments for the table page------#


colNames = ['ValidTick',
            'SignalDate',
            'ScanDate', 
            'NScanDaysInterval', 
            'PriceAtSignal', 
            'Last closing price',
            'Price Evolution', 
            'Company',
            'Sector',
            'Industry']



def STD_FUNC_TABLE_PAGE():

    average, items, spSTART, spEND, nSignals, dfSignals = fetchSignals(ALL=True)
    
    std_sp                                              = sp500evol(spSTART,spEND)
    form                                                = SearchForm(request.form)
    dfSignals                                           =  dfSignals[['SignalDate','ValidTick']].\
                    groupby('SignalDate').agg(['count']).droplevel(0, axis=1)

    NbSigchart = lineNBSignals(dfSignals,std_sp.sp500Data)
    # This is the standard set of arguments used in every route page
    standard_args_table_page = dict(
        average             = average,
        items               = items[:500],
        strToday            = strToday,
        spSTART             = spSTART,
        spEND               = std_sp.spEND,
        SP500evolFLOAT      = std_sp.fetchSPEvol(),
        nSignals            = nSignals,
        NbSigchart          = NbSigchart,
        form                = form,
        colNames            = colNames,
        widthDF             = list(range(len(colNames)))
        )

    return standard_args_table_page
    
####------Standard functions and arguments for the table page------#


def tuplesToCSV(Tuples):
    """
    To be used by Flask's Reponse class, to return a csv type
    Transform tuples int a csv style sheet
    :param 1: tuples
    :returns: a long string that mimics a CSV
    """
    reReconstructedCSV = ""

    for line in Tuples:
        c1 = line[0]
        c2 = line[1].strftime("%Y-%m-%d")
        c3 = line[2].strftime("%Y-%m-%d")
        c4 = str(line[3])
        c5 = str(line[4])
        c6 = str(line[5])
        c7 = str(line[6])

        reReconstructedLine  = c1 + ',' + c2 + ','\
             + c3 + ',' + c4 + ',' + c5 + ',' + c6 + ',' + c7 + '\n'
        reReconstructedCSV = reReconstructedCSV + reReconstructedLine

    return reReconstructedCSV



@app.route('/technicals')
@login_required
def technicals():
    form    = SearchForm(request.form)
    text    = form.stock.data.upper()
    items   = fetchTechnicals()

    return render_template('technicals.html',items=items, form=form)
    


@app.route('/technicals', methods=['POST'])
@login_required
def submitTechnicals():
    form    = SearchForm(request.form)
    text    = form.stock.data.upper()
    items   = fetchTechnicals(text)

    return render_template('technicals.html', 
    items   = items,
    form    = form, 
    stock   = text)



@app.route('/ownership')
@login_required
def ownership():
    tick    = 'PLUG'
    form    = SearchForm(request.form)
    text    = form.stock.data.upper()
    items   = fetchOwnership(tick)
    plot    = makeOwnershipGraph(items, tick)

    return render_template('ownership.html',
                            items   = items,
                            form    = form,
                            plot    = plot)
                    

@app.route('/ownership', methods=['POST'])
@login_required
def submitOwnership():
    form    = SearchForm(request.form)
    text    = form.stock.data.upper()
    items   = fetchOwnership(text)
    plot    = makeOwnershipGraph(items, text)

    return render_template('ownership.html', items=items,\
    form=form, stock=text,plot=plot)


@app.route('/macroView')
@login_required
def macroView():
    return render_template('macroView.html')
    


@app.route('/investInfra')
@login_required
def investInfra():
    return render_template('investInfra.html')



@app.route('/portfolios')
@login_required
def portfolios():
    return render_template('portfolios.html')


@app.route('/crypto')
@login_required
def crypto():
    return render_template('crypto.html')



@app.route('/ideas')
@login_required
def ideas():
    return render_template('ideas.html')


@app.route('/pipelines')
@login_required
def pipelines():
    return render_template('pipelines.html')


@app.route('/brownian')
@login_required
def brownian():
    return render_template('brownian.html')



@app.route('/table')
@login_required
def table():
    """
    Standard view for the "table" page
    """
    standard_args_table_page = STD_FUNC_TABLE_PAGE()

    return render_template('table.html',
    **standard_args_table_page)


@app.route("/getCSV", methods=['GET'])
@login_required
def getCSV():
    items = fetchSignals()
    reReconstructedCSV = tuplesToCSV(Tuples=items)
    return Response(
        reReconstructedCSV,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=signals.csv"})




@app.route('/api/fetchSectorEvols')
@login_required
def get_sectors_evols():

    interval = request.args["interval"]

    print('interval: ', interval)


    qu = "SELECT * FROM marketdata.sectorEvols"
    df_sector_evols = db_acc_obj.exc_query(db_name='marketdata', query=qu,\
                        retres = QuRetType.ALLASPD)

    df_sector_evols_grped_sec = ((df_sector_evols.groupby(['Sector']).mean())
                                                                    .reset_index()
                                                                    .sort_values(by=[f'{interval}'],
                                                                    ascending=False)
                                                                    )


    fig = go.Figure([go.Bar(x=df_sector_evols_grped_sec.Sector, 
                            y=df_sector_evols_grped_sec[f'{interval}'])])

    fig.update_yaxes(showline       = False, 
                    linewidth       = 1,
                    gridwidth       = 0.2, 
                    linecolor       = 'grey', 
                    gridcolor       = 'rgba(192,192,192,0.5)',
                    zeroline        = True,
                    zerolinewidth   = 1,
                    zerolinecolor   = 'black')

    fig.update_layout(
    plot_bgcolor    = 'rgba(0,0,0,0)',
    legend          = dict(
                    orientation = "h",
                    yanchor     = "bottom",
                    y           = 1.02,
                    xanchor     = "right",
                    x           = 1
                    )
    )
    fig.update_layout(margin = dict(t=0, l=0, r=0, b=0))

    graphJSON = json.dumps(fig, cls = plotly.utils.PlotlyJSONEncoder)

    return graphJSON





if __name__ == '__main__':
    db_acc_obj = std_db_acc_obj()
    app.run(host='0.0.0.0', debug=True)