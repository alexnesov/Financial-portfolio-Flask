
def create_lineChart(tick='PLUG'):
    """
    Lists of stock for both NASDAQ and NYSE are present in /utils
    Instead of having a big table with both NASDAQ and NYSE stocks
    We have two list of stocks. The requests to RDS are going to be sent relatively to which list 
    the code can find the tick. Spares time execution.
    """
    :param 1: user input in chart page
    :returns: json to generate a plotly chart in HTML

    nasdaq = list(pd.read_csv('utils/nasdaq_list.csv').iloc[:, 0])

    if tick in nasdaq:
        table_chart = 'NASDAQ_20'
    else:
        table_chart = 'NYSE_20'

    qu=f"SELECT * FROM {table_chart} WHERE Symbol='{tick}'"
    df = db_acc_obj.exc_query(db_name='marketdata', query=qu,\
        retres=QuRetType.ALLASPD)

    fig = go.Figure()

    fig = make_subplots(rows=3, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.12,
                        row_width=[0.3, 0.8, 0.2],
                        specs=[[{"rowspan":2}],
                        [None],
                        [{}]])

    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name='Close', mode='lines',
    line=dict(color='royalblue')),row=1, col=1)

    fig.add_trace(go.Scatter(x=df['Date'], y=df['Volume'], name='Volume', mode='lines',
    line=dict(color='black')), row=3, col=1)
    fig.update_yaxes(showline=False,linewidth=1,gridwidth=0.2, linecolor='grey', gridcolor='rgba(192,192,192,0.5)')

    fig.update_layout(
        plot_bgcolor='white',
        #width=1400,
        height=650,
        margin=dict(
        autoexpand=False,
        l=100,
        r=20,
        t=110,
    )
    )

    fig['layout']['xaxis2']['title']='Date'
    fig['layout']['yaxis']['title']='Close'
    fig['layout']['yaxis2']['title']='Volume'

    lineJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return lineJSON



def makeHistogram(items):

    df = pd.DataFrame(list(items), columns=['ValidTick',
        'SignalDate',
        'ScanDate',
        'NScanDaysInterval',
        'PriceAtSignal',
        'LastClostingPrice',
        'PriceEvolution',
        'Company',
        'Sector',
        'Industry'])


    df['PriceEvolution'] = pd.to_numeric(df['PriceEvolution'])    
    df = df[(df['PriceEvolution']!=0)]
    dfPivoted = pd.pivot_table(df, values='PriceEvolution',index=['SignalDate'], aggfunc=np.mean)
    dfMin = df[(df['LastClostingPrice'] < 15)]
    dfMid = df[(df['LastClostingPrice'] >= 15) & (df['LastClostingPrice'] <= 60)]
    dfMax = df[(df['LastClostingPrice'] > 60)]

    dfPivotedMin = pd.pivot_table(dfMin, values='PriceEvolution',index=['SignalDate'], aggfunc=np.mean)
    dfPivotedMid = pd.pivot_table(dfMid, values='PriceEvolution',index=['SignalDate'], aggfunc=np.mean)
    dfPivotedMax = pd.pivot_table(dfMax, values='PriceEvolution',index=['SignalDate'], aggfunc=np.mean)

    meanMin = round(dfPivotedMin.PriceEvolution.mean(),2)
    meanMid = round(dfPivotedMid.PriceEvolution.mean(),2)
    meanMax = round(dfPivotedMax.PriceEvolution.mean(),2)


    #fig = go.Figure([go.Bar(x=dfPivoted.index, y=dfPivoted['PriceEvolution'])])
    fig = go.Figure(data=[
        go.Bar(name='<15$', x=dfPivoted.index, y = dfPivotedMin.PriceEvolution),
        go.Bar(name='>=15$ & <=60$', x=dfPivoted.index, y = dfPivotedMid.PriceEvolution),
        go.Bar(name='>60$', x=dfPivoted.index, y = dfPivotedMax.PriceEvolution)
    ])
    fig.update_layout(barmode='group')

    fig.update_layout(title='Average return, per starting Signal Date \
(ex: "the stocks signaled on the 22nd December have an average return of 45% until today") low price stocks.\
<br><b>Stocks caracterized by lower prices yield significantly higher returns than other price intervals.<b>',\
        xaxis_title="SignalDate",
        yaxis_title="Avg. Return (%)",
        font=dict(size=10),
        #width=1400,
        #height=390,
        plot_bgcolor='rgba(0,0,0,0)')

    
    fig.add_hline(y=dfPivotedMin["PriceEvolution"].mean(), annotation_text=f"{meanMin}%",line_dash="dot",\
        line=dict( color="blue", width=1),annotation_font_color="blue")
    fig.add_hline(y=dfPivotedMid["PriceEvolution"].mean(), annotation_text=f"{meanMid}%",line_dash="dot", \
        line=dict( color="red", width=1),annotation_font_color="red")
    fig.add_hline(y=dfPivotedMax["PriceEvolution"].mean(), annotation_text=f"{meanMax}%",line_dash="dot", \
        annotation_font_color="green", annotation_position="bottom left", line=dict( color="green", width=1))

    fig.update_yaxes(showline=False, linewidth=1,gridwidth=0.2, linecolor='grey', gridcolor='rgba(192,192,192,0.5)',zeroline=True,zerolinewidth=1,zerolinecolor='black')


    lineJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return lineJSON



def makeSignalSectorEvol(df):

    newdf = df.reset_index().iloc[:,4:]
    # Normalization
    newdf = newdf / newdf.iloc[0] * 100

    fig = px.line(newdf, x=df.Date, y=newdf.columns,log_y=True)
    fig.update_layout(title='Evolution of average prices of Signals, per Sector',\
        xaxis_title="Date",
        yaxis_title="Normalized (log)",
        font=dict(size=10),
        #width=1400,
        #height=390,
        plot_bgcolor='rgba(0,0,0,0)')

    fig.update_yaxes(showline=False, linewidth=1,gridwidth=0.2, linecolor='grey', gridcolor='rgba(192,192,192,0.5)',zeroline=True,zerolinewidth=1,zerolinecolor='black')

    lineJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return lineJSON