
from flask_login import login_required
from flask import Blueprint, request
from plotly.subplots import make_subplots
from signals_lib.detailedGeneration import consolidateSignals

import plotly
import json

import plotly.graph_objs as go

page_signals = Blueprint('page_signals', 
                        __name__,
                        static_folder   = 'SV/static',
                        template_folder = 'SV/templates')






@page_signals.route('/api/fetchSignalChartJsonData')
@login_required
def makeLinesSignal():
    # http://127.0.0.1:5000/api/fetchSignalChartJsonData
    tick = request.args["tick"]
    tick = tick.upper()

    if tick == '':
        tick ='AXR'

    print(f"tick recieved: {tick}")
    # You can have tick validation before moving ahead, if it's invalid tick then return error on UI

    df_signals = consolidateSignals(tick)

    fig = make_subplots(rows                = 7, 
                        cols                = 1,
                        shared_xaxes        = True,
                        vertical_spacing    = 0.03,
                        row_width           = [0.15, 0.15, 0.15, 0.15, 0.15,0.15,0.30],
                        specs               = [[{"rowspan":2}],
                        [None],
                        [{}],
                        [{}],
                        [{}],
                        [{}],
                        [{}]
                        ])

                        
    fig.add_trace(go.Candlestick(x=df_signals.Date,open=df_signals.Open,close=df_signals.Close,low=df_signals.Low,high=df_signals.High),
                row=1, col=1)

    fig.update_layout(xaxis_rangeslider_visible=False)
    
    fig.add_trace(go.Scatter(x=df_signals.Date, y=df_signals['long_mavg'], name='long_mvg 50',mode='lines',
        line=dict(color='orange',dash='dash')),
                row=1, col=1)

    fig.add_trace(go.Scatter(x=df_signals.Date, y=df_signals['short_mavg'], name='short_mvg 10',mode='lines',
        line=dict(color='royalblue')),
                row=1, col=1)

    fig.add_trace(go.Scatter(x=df_signals.Date[df_signals.positions==1], y=df_signals.short_mavg[df_signals.positions==1], 
    name='MA crossing',mode='markers', marker_symbol='triangle-up', marker_size=10, marker_color='blue'),
                row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df_signals.Date[df_signals.doubleSignal==1], y=df_signals.short_mavg[df_signals.doubleSignal==1], 
    name='Double Signal',mode='markers', marker_symbol='triangle-up', marker_size=15, marker_color='green'),
                row=1, col=1)

    fig.add_trace(go.Scatter(x=df_signals.Date, y=df_signals['Aroon Up'], name='Aroon Up', mode='lines',
        line=dict(color='green')),
                row=3, col=1)

    fig.add_trace(go.Scatter(x=df_signals.Date, y=df_signals['Aroon Down'], name='Aroon Down', mode='lines',\
        line=dict(color='red')),
                row=3, col=1)

    fig.add_trace(go.Scatter(x=df_signals.Date, y=df_signals['Volume'], name='Volume', mode='lines',\
        line=dict(color='purple')),
                row=4, col=1)

    fig.add_trace(go.Scatter(x=df_signals.Date, y=df_signals['diff_stock_bench'], name='diff_stock_bench', mode='lines',\
        line=dict(color='purple')),
                row=5, col=1)


    fig.add_trace(go.Scatter(x=df_signals.Date, y=df_signals['rolling_mean_35'], name='rolling_mean_35', mode='lines',\
        line=dict(color='red')),
                row=6, col=1)
    
    fig.add_trace(go.Scatter(x=df_signals.Date, y=df_signals['RSI'], name='RSI', mode='lines',\
        line=dict(color='Orange')),
                row=7, col=1)

    fig.update_yaxes(showline       = False, 
                     linewidth      = 1,
                     gridwidth      = 0.2, 
                     linecolor      = 'grey', 
                     gridcolor      = 'rgba(192,192,192,0.5)',
                     zeroline       = True,
                     zerolinewidth  = 1,
                     zerolinecolor  ='black')


    fig.update_traces(line_width=1.5)
    fig.update_layout(
    title   =    f'Trend Reversal Detection for {tick}',
    height  =   1100,
    plot_bgcolor='rgba(0,0,0,0)',
    margin  =   dict(
        autoexpand = False,
        l = 100,
        r = 20,
        t = 110,
        ),
    legend = dict(
        orientation     = "h",
        yanchor         = "bottom",
        y               = 1.02,
        xanchor         = "right",
        x               = 1
        )
    )
    fig.update_yaxes(showline=False, linewidth=1,gridwidth=0.2, linecolor='grey', gridcolor='rgba(192,192,192,0.5)')


    fig['layout']['xaxis6']['title']    = 'Date'
    fig['layout']['yaxis']['title']     = 'Price'
    fig['layout']['yaxis2']['title']    = 'Aroon'
    fig['layout']['yaxis3']['title']    = 'Volume'
    fig['layout']['yaxis4']['title']    = 'diff_stock_bench'
    fig['layout']['yaxis5']['title']    = 'rolling_mean_35'
    fig['layout']['yaxis6']['title']    = 'RSI'


    annotations = []

    annotations.append(dict(xref    = 'paper', 
                            yref    = 'paper', 
                            x       = 0, 
                            y       = -0.09,
                            xanchor = 'left', 
                            yanchor = 'top',
                            #text='Log scale is used for vol. to have better grasp incoming vol on smaller caps',
                            font=dict(family      = 'Arial',
                                    size        = 12,
                                    color       = 'rgb(150,150,150)'),
                                    showarrow   = False))

    
    fig.update_layout(annotations=annotations)
    

    graphJSON = json.dumps(fig, cls = plotly.utils.PlotlyJSONEncoder)

    return graphJSON

