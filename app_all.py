from flask_login import current_user, login_required
from flask import render_template, url_for, flash, redirect, request, Response
from wtforms import TextField, Form
from flask import Blueprint, request
from datetime import datetime
import os
from typing import List, Tuple, Dict, Any

from SV import db
from SV.models import User
from SV.users.forms import RegistrationForm, UpdateUserForm
from SV.users.picture_handler import add_profile_pic
from utils.fetchData import fetchSignals, fetchTechnicals, fetchOwnership, sp500evol
from utils.graphs import makeOwnershipGraph, lineNBSignals


page_all = Blueprint('page_all', 
                    __name__,
                    static_folder   = 'SV/static',
                    template_folder = 'SV/templates')


strToday    = str(datetime.today().strftime('%Y-%m-%d'))
magickey    = os.environ.get('magickey')


class SearchForm(Form):
    stock               = TextField('Insert Stock', id='stock_autocomplete')
    nbRows              = TextField('Enter n° rows', id='numberRows')
    date_input          = TextField('Enter Signal Date', id='date_input')
    reset               = TextField('Reset', id='reset')
    getcsv              = TextField('Download', id='getcsv')
    mW                  = TextField('mW', id='mW')
    validChartSignal    = TextField('validChartSignal', id='validChartSignal')


class NConnections():
    """
    Class representing the number of connections.

    Attributes:
        n_con (int): The number of connections.

    Methods:
        query: Increments the number of connections by 1 and returns the updated value.
    """


    def __init__(self, n_con: int) -> int:
        """
        Initialize the NConnections object.

        Args:
            n_con (int): The initial number of connections.
        """

        self.n_con = n_con

    def query(self):
        self.n_con += 1
        return self.n_con

obj_n_connections = NConnections(0) 


@page_all.route('/')
def home():
    """
    Route for the home page.

    Returns:
        A rendered template for the home page.
    """

    print("Home called")


    return render_template('home.html')



@page_all.route('/register', methods=['GET', 'POST'])
def register():
    """
    Route for the registration page.

    If the form is submitted and valid:
        - Create a new user with the provided email, username, and password.
        - Flash a success message and redirect to the login page.

    Returns:
        A rendered template for the registration page.
    """

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
            return render_template('login.html', form=form)
        else:
            return render_template('register.html', form=form, \
            formW=formW,magics=False)


    return render_template('register.html', form=form, \
    formW=formW, magics=True)


@page_all.route('/welcome')
def welcome_user():
    """
    Route for the welcome user page.

    Returns:
        A rendered template for the welcome user page.
    """

    return render_template('welcome_user.html')




@page_all.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    """
    Route for the account page.

    If the form is submitted and valid:
        - Update the user's account details (username and email).
        - Flash a success message.
        - Redirect to the account page.

    Returns:
        A rendered template for the account page.
    """
    form = UpdateUserForm()

    if form.validate_on_submit():

        if form.picture.data:
            username = current_user.username
            pic = add_profile_pic(form.picture.data,username)
            current_user.profile_image = pic

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        return redirect(url_for('page_all.account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    profile_image = url_for('static', filename='profile_pics/' + current_user.profile_image)
    
    return render_template('account.html', profile_image=profile_image, form=form)



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



def STD_FUNC_TABLE_PAGE() -> Dict[str, Any]:
    """
    Retrieves signals, performs calculations, and prepares a dictionary of standard arguments
    used in every route page.
    :return: A dictionary containing the standard arguments for the table page.
    """
    average, items, spSTART, spEND, nSignals, dfSignals = fetchSignals(ALL=True)
    print("spSTART, spEND: ", spSTART, spEND)
    
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


def tuplesToCSV(tuples: List[Tuple]) -> str:
    """
    Converts a list of tuples into a CSV-style string.
    :param tuples: A list of tuples.
    :return: A long string that mimics a CSV.
    """
    reReconstructedCSV = ""

    for line in tuples:
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



@page_all.route('/technicals')
@login_required
def technicals():
    form    = SearchForm(request.form)
    text    = form.stock.data.upper()
    items   = fetchTechnicals()

    return render_template('technicals.html',items=items, form=form)
    


@page_all.route('/ownership', methods=['POST'])
def submitOwnership():
    form    = SearchForm(request.form)
    text    = form.stock.data.upper()
    items   = fetchOwnership(text)
    plot    = makeOwnershipGraph(items, text)

    return render_template('ownership.html', items=items,\
    form=form, stock=text,plot=plot)

    


@page_all.route('/investInfra')
def investInfra():
    return render_template('investInfra.html')


@page_all.route('/portfolios')
def portfolios():
    return render_template('portfolios.html')



@page_all.route('/pipelines')
@login_required
def pipelines():
    return render_template('pipelines.html')


@page_all.route('/table')
@login_required
def table():
    """
    Standard view for the "table" page
    """
    standard_args_table_page = STD_FUNC_TABLE_PAGE()

    print("**standard_args_table_page", standard_args_table_page.keys())

    return render_template('table.html',
    **standard_args_table_page)


@page_all.route("/getCSV", methods=['GET'])
def getCSV():
    items = fetchSignals()
    print("items: ")
    print(items)
    reReconstructedCSV = tuplesToCSV(tuples=items)
    return Response(
        reReconstructedCSV,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=signals.csv"})



