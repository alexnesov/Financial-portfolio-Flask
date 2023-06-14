from flask import Blueprint, request, render_template
from flask_login import login_required
from utils.db_manage import std_db_acc_obj, QuRetType
import plotly.graph_objs as go
import json
import plotly


page_macro = Blueprint('page_macro', 
                        __name__,
                        static_folder   = 'SV/static',
                        template_folder = 'SV/templates')

db_acc_obj = std_db_acc_obj()


@page_macro.route('/macroView')
@login_required
def macroView():
    """
    Route for the macroView page.

    Returns:
        A rendered template for the macroView page.
    """

    return render_template('macroView.html')



@page_macro.route('/api/fetchSectorEvols')
@login_required
def get_sectors_evols():
    """
    API endpoint to fetch sector evolutions.

    Retrieves the interval parameter from the request arguments, queries the sectorEvols table,
    and generates a bar graph of sector evolutions for the specified interval.

    Returns:
        str: JSON representation of the generated plotly bar graph.
    """
    interval = request.args["interval"]

    print('User selected interval: ', interval)

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
