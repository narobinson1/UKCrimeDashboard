# Import packages
from dash import Dash, DiskcacheManager, CeleryManager, html, dcc, callback, Output, Input, State, ctx
from dash.exceptions import PreventUpdate

import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
import os

from datetime import date

import dash_bootstrap_components as dbc

import requests
import functools

import mysql.connector

# Initialize the app - incorporate a Dash Bootstrap theme
external_stylesheets = [dbc.themes.CERULEAN]
app = Dash(__name__, external_stylesheets=external_stylesheets)

COLORS = {
    "top-bar-background": "#172952",
    "top-bar-color": "#028acf",
    "content-background": "#2a2630",
    "general": "#2fa4e7"
}

TOPBAR_STYLE = {
    "background-color": COLORS['top-bar-background'],
    "color": COLORS['top-bar-color'],
}

CONTENT_STYLE = {
    "background-color": COLORS['content-background']
}


url_bar_and_content_div = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Store(id='lru-cache', storage_type='session', data='')
], style={"background-color": COLORS['content-background'], "height":"100vh"})


def date_range(start_year, start_month, end_year, end_month):
    sy = int(start_year)
    ey = int(end_year)
    
    sm = int(start_month.lstrip('0'))
    em = int(end_month.lstrip('0'))

    r = []
    for y in range(sy, ey+1):
        s = 1
        e = 13
        if y == sy:
            s = sm
            e = 13
        if y == ey:
            s = 1
            e = em + 1
            
        y = str(y)
        for m in range(s, e):
            l = []
            l.append(str(y))
            l.append("-")
            if m < 10:
                l.append("0")
            l.append(str(m))
            r.append(''.join(l))
    
    return r

# Get totals from db
def get_count_graph(dropdown_input, start_year, start_month, end_year, end_month):
    cnx = mysql.connector.connect(
            user='root',
            password='rootuser',
            host='127.0.0.1',
            database='ukgovcrime')

    cursor = cnx.cursor()
    
    t = []
    for x in dropdown_input:
        t.append(x)

    ms = date_range(start_year, start_month, end_year, end_month)
    for x in ms:
        t.append(x)
    
    t = tuple(t)
    format_locations = ','.join(['%s'] * len(dropdown_input))
    format_dates = ','.join(['%s'] * len(ms))
    query_dropdown_data = ("SELECT location, total, fractional, month FROM dropdown_data WHERE location IN (%s) AND month IN (%s)" % (format_locations, format_dates))

    cursor.execute(query_dropdown_data, t)

    l = []
    t = []
    f = []
    m = []
    for (location, total, fractional, month) in cursor:
        l.append(location)
        t.append(total)
        print(fractional[:6])
        f.append(fractional)
        m.append(month)

    d = {'location':l, 'total':t, 'fractional':f, 'month':m}
    df = pd.DataFrame(d)
    
    
    l_ = []
    s = []
    f = []
    for location in set(l):
        l_.append(location)
        x = list(df[df['location'] == location]['total'])
        s_ = 0
        for i in x:
            s_ += int(i)
        s.append(s_)
        
        x = list(df[df['location'] == location]['fractional'])
        s_ = 0
        for i in x:
            s_ += float(i)
        f.append(float(str(s_)[:6]))
        
        
    
    d = {'location':l_, 'total':s, 'fractional':f}
    df = pd.DataFrame(d)
    
    return df
    
# Get statistics from db
def get_category(location, start_year, start_month, end_year, end_month):
    cnx = mysql.connector.connect(
            user='root',
            password='rootuser',
            host='127.0.0.1',
            database='ukgovcrime')

    cursor = cnx.cursor()

    t = []
    
    t.append(location)
    ms = date_range(start_year, start_month, end_year, end_month)
    for x in ms:
        t.append(x)
    
    t = tuple(t)
    format_location = ','.join(['%s'])
    format_dates = ','.join(['%s'] * len(ms))
    query_dropdown_data = ("SELECT location, category, total, fractional, month FROM category_data WHERE location = (%s) AND month IN (%s)" % (format_location, format_dates))

    cursor.execute(query_dropdown_data, t)


    l = []
    c = []
    t = []
    f = []
    m = []
    for (location, category, total, fractional, month) in cursor:
        l.append(location)
        c.append(' '.join(category.split("-")))
        t.append(total)
        f.append(fractional)
        m.append(month)

    d = {'location':l, 'category':c, 'total':t, 'fractional':f, 'month':m}
    df = pd.DataFrame(d)
    
    
    l_ = location
    cn_ = []
    ct_ = []

    
    s = []
    f = []
    
    for category in set(c):
        cn_.append(category)
        
        x = df[df['location'] == location]
        x = list(x[x['category'] == category]['total'])
        
        s_ = 0
        for i in x:
            s_ += int(i)
        ct_.append(s_)
        
        
    ct = []
    for q in ct_:
        q = q / sum(ct_)
        ct.append(float(str(q)[:6]))
        
    
        
    
    d = {'category':cn_, 'ratio':ct}
    df = pd.DataFrame(d)
    
    return df

    
# Get statistics from db
def get_count_map(dropdown_input, start_year, start_month, end_year, end_month):
    cnx = mysql.connector.connect(
            user='root',
            password='rootuser',
            host='127.0.0.1',
            database='ukgovcrime')

    cursor = cnx.cursor()
    
    t = []
    for x in dropdown_input:
        t.append(x)

    ms = date_range(start_year, start_month, end_year, end_month)
    for x in ms:
        t.append(x)
    
    t = tuple(t)
    format_locations = ','.join(['%s'] * len(dropdown_input))
    format_dates = ','.join(['%s'] * len(ms))
    query_dropdown_data = ("SELECT location, total, fractional, lat, lng, month FROM dropdown_data WHERE location IN (%s) AND month IN (%s)" % (format_locations, format_dates))

    cursor.execute(query_dropdown_data, t)

    l = []
    coords = []
    t = []
    f = []
    m = []
    
    for (location, total, fractional, lat, lng, month) in cursor:
        l.append(location)
        coords.append([lat, lng])
        t.append(total)
        f.append(fractional)
        m.append(month)

    d = {'location':l, 'total':t, 'fractional':f, 'month':m}
    df = pd.DataFrame(d)
    
    
    z = dict()

    for i in range(len(l)):
        if l[i] not in list(d):
            z[l[i]] = coords[i]
            
    l_ = []
    la = []
    ln = []
    s = []
    f = []

    for x in l:
        if x not in l_:
            l_.append(x)
            la.append(float(z[x][0]))
            ln.append(float(z[x][1]))

    for location in l_:
        x = list(df[df['location'] == location]['total'])
        s_ = 0
        for i in x:
            s_ += int(i)
        s.append(s_)
        
        x = list(df[df['location'] == location]['fractional'])
        s_ = 0
        for i in x:
            s_ += float(i)
        f.append(float(str(s_)[:6]))
        

    
    d = {'location':l_, 'lat':la, 'lng':ln, 'total':s, 'fractional':f}
    df = pd.DataFrame(d)

    return df

dashboard_layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.A(
                                    children=[
                                        
                                        html.Img(src='assets/github.png', id='github-logo', height=70, style={'display':'inline', 'float':'right'})
#
                                    ],
                                    href='https://github.com/narobinson1',
                                    target='_blank'
                                ),
                                html.Div([
                                    html.H1('UK Crime rates', style={'margin-right': '0.5rem', 'display':'inline', 'width':'20vw', 'margin-bottom':'10rem', 'font-weight':'300'}),
                                    html.H1('| Python, Dash, MySQL', style={'font-weight':'10', 'margin-right':'0', 'padding':'0', 'width':'25vw', 'display':'inline'}),
                                    
                                    
                                ],
                                style={'padding-bottom':'2.4rem'}
                                ),
                            ],
                        ),
                    ],
                    style={"padding":"2rem 2rem 0rem 2rem", 'borderBottom':'3px solid #2fa4e7', "background-color": COLORS['content-background']}
                ),
                
            ],

        ),
        
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.H6("Choose locations"),
                                dcc.Dropdown(options=[{"label": x, "value": x} for x in ['London', 'Manchester', 'Liverpool', 'Bristol']],
                                value=['London', 'Manchester', 'Liverpool'],
                                multi=True,
                                style={'background-color': COLORS['top-bar-background'], 'font-weight':'100'},
                                id='dropdown-component-final')
                            ],
                            style={'padding':'0px 0px 20px 0px', 'color':'#2fa4e7'}
                        ),
                        html.Div(
                            children=[
                                #start children
                                html.Div(
                                    children=[
                                        html.Div(
                                            children=[
                                                dcc.Markdown('''
                                                    ###### Dashboard configuration
                                                ''')
                                            ],
                                            style={'font-weight':'100', 'margin-bottom':'1rem'}
                                        ),
                                        html.Div(
                                            children=[
                                                html.P('Crime count divided by total population', style={'font-weight':'100'}),
                                                dcc.Dropdown(
                                                    options=[{"label": x, "value": x} for x in ['Total', 'Fractional']],
                                                    value='Total',
                                                    style={'background-color':COLORS['content-background'], 'color':'#2fa4e7', 'font-weight':'100'},
                                                    id='dropdown-stat-type'
                                                ),
                                            ],
                                            style={'margin-bottom':'1rem'}
                                        ),
                                        html.Div(
                                            children=[
                                                html.P('Date period when crimes occured', style={'font-weight':'100'}),
                                                
                                                html.Div(
                                                    children=[
                                                        html.Div(
                                                            children=[
                                                                dcc.Dropdown(
                                                                    options=[{"label": str(x), "value": str(x)} for x in range(2000, 2024)],
                                                                    value='2023',
                                                                    style={'background-color':COLORS['content-background'], 'color':'#2fa4e7', 'width':'7rem', 'margin-top': '0px', 'margin-bottom': '5px', 'font-weight':'100'},
                                                                    placeholder='Start year',
                                                                    id='dropdown-start-year'
                                                                ),
                                                                dcc.Dropdown(
                                                                    options=[{"label": str(x), "value": str(x)} for x in range(1, 13)],
                                                                    value='1',
                                                                    style={'background-color':COLORS['content-background'], 'color':'#2fa4e7', 'width':'7rem', 'font-weight':'100'},
                                                                    placeholder='Start month',
                                                                    id='dropdown-start-month'
                                                                )
                                                            ],
                                                            style={'display':'inline-block', 'padding':'0px'}
                                                        ),
                                                        html.Div(
                                                            children=[
                                                                html.P('UNTIL')
                                                                #html.Img(src='assets/arrow.png', height=30, style={'display':'inline', 'position':'relative', 'bottom':'54px'})
                                                            ],
                                                            style={'display':'inline-block', 'position':'relative', 'left':'55px', 'bottom':'38px'}
                                                        ),
                                                        html.Div(
                                                            children=[
                                                                dcc.Dropdown(
                                                                    options=[{"label": x, "value": x} for x in range(2000, 2024)],
                                                                    value='2023',
                                                                    style={'background-color':COLORS['content-background'], 'color':'#2fa4e7', 'width':'7rem', 'margin-top': '0px', 'margin-bottom': '5px', 'font-weight':'100'},
                                                                    placeholder='End year',
                                                                    id='dropdown-end-year'
                                                                ),
                                                                dcc.Dropdown(
                                                                    options=[{"label": x, "value": x} for x in range(1, 13)],
                                                                    value='12',
                                                                    style={'background-color':COLORS['content-background'], 'color':'#2fa4e7', 'width':'7rem', 'font-weight':'100'},
                                                                    placeholder='End month',
                                                                    id='dropdown-end-month'
                                                                )
                                                            ],
                                                            style={'display':'inline-block', 'padding':'0px', 'float':'right'}
                                                        ),
                                                        
                                                        
                                                    ],
                                                    style={'padding':'0px 0px 0px 0px'}
                                                ),
                                                dcc.Markdown(id='date-markdown', style={"padding":"0px", 'font-weight': '200', 'font-size': '16px'})
            
                                            ],
                                            style={'margin-bottom':'0rem'}
                                        ),
                                        
                                        
                                    ],
                                    style={'color':COLORS['general'], 'border':'1px solid #2fa4e7', 'padding':'20px', 'margin-bottom':'20px'}
                                ),
                                html.Div(
                                    children=[
                                        dcc.Markdown('''
                                            ###### Data provider
                                            
                                            The data used for this project was acquired through the uk.gov Police API.
                                        ''', style={'color':COLORS['general']}),
                                        
                                    ],
                                    style={'font-weight':'100', 'border':'1px solid #2fa4e7', 'padding':'20px'}
                                    
                                )
                                #end children
                            ],
                            style={'width': '30%', 'display':'inline-block', 'height':'70.1vh', 'padding':'0px'}
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                        children=[
                                            #start children
                                            html.Div(
                                                children=[
                                                    dcc.Loading(
                                                        children=[
                                                            dcc.Graph(
                                                                figure={
                                                                    'layout':{
                                                                        'height': 320
                                                                    }
                                                                },
                                                                config={'displayModeBar':False, 'autosizable':True},
                                                                id="output-map-1")
                                                        ],
                                                        id="map-loading-1"
                                                    )
                                                ],
                                                # Parent div map loading style
                                                style={"border":"1px solid #2fa4e7"}
                                            ),

                                
                                    html.Div(
                                        children=[
                                            html.Div(
                                                children=[
                                                    html.Div(
                                                        children=[
                                                            html.Div(
                                                                children=[
                                                                    dcc.Loading(
                                                                        children=[
                                                                            dcc.Graph(
                                                                                figure={
                                                                                    'layout':{
                                                                                        'height': 400,
                                                                                        'autosize': True,
                                                                                        'margin': {'b':0, 'r':0, 'l':0, 't':0}
                                                                                    }
                                                                                },
                                                                                config={'displayModeBar':False, 'editSelection':False, 'editable':False, 'showAxisDragHandles':False, 'showAxisRangeEntryBoxes':False, 'responsive':False, 'autosizable':False, 'fillFrame':False, 'scrollZoom':False},
                                                                                id="output-graph-1"
                                                                            )
                                                                        ],
                                                                        id="graph-loading-1",
                                                                        style={"padding-left": "3rem", "padding-right": "3rem", "padding-bottom": "3rem", "padding-top": "0rem"}
                                                                    )
                                                                ],
                                                            )
                                                        ],
                                                        style={"width":"50%", 'padding':'0px 0px 0px 0px'}
                                                    ),
                                                ],
                                                style={'margin-top':'1rem', 'padding':'0px 0px 0px 0px', 'display':'inline-block', 'border':'1px solid #2fa4e7'}
                                            ),
                                                    
                                            html.Div(
                                                children=[
                                                    html.Div(
                                                        children=[
                                                            html.Div(
                                                                children=[
                                                                    dcc.Loading(
                                                                        children=[
                                                                            dcc.Graph(
                                                                                figure={
                                                                                    'layout':{
                                                                                        'height': 200,
                                                                                        'autosize': True,
                                                                                        'margin': {'b':0, 'r':0, 'l':0, 't':0}
                                                                                    }
                                                                                },
                                                                                config={'displayModeBar':False, 'scrollZoom':False},
                                                                                id="output-graph-2"
                                                                            )
                                                                        ],
                                                                        id="graph-loading-2",
                                                                        style={"padding-left": "3rem", "padding-right": "3rem", "padding-bottom": "3rem", "padding-top": "0rem"}
                                                                    ),
                                                                    dcc.Store(id='graph-2-location-store', data='London')
                                                                ],
                                                            ),
                                                        ],
                                                        style={"width":"50%", 'padding':'0px 0px 0px 0px'}
                                                    ),
                                                ],
                                                style={'margin-top': '1rem', 'padding':'0px 0px 0px 0px', 'display':'inline-block', 'border':'1px solid #2fa4e7', 'float':'right'}
                                            )
                                                    
                                        ],
                                    
                                    ),
                                            #end children
                                        ]
                                )
                            ],
                            style={'width':'70%', 'display':'inline-block', 'background-color':COLORS['content-background'], 'float':'right', 'padding': '0px 0px 0px 18px', 'height':'68vh'}

                        ),
                    ],
                    style={'padding':'20px'}
                ), # parent div
                
                
                html.Div([dcc.Store(id='memory-output', storage_type='session', data=pd.read_csv("gb_latlon.csv", dtype=object).to_json(date_format='iso', orient='split'))])
            ],
            style=CONTENT_STYLE
        ),
    ], style={"fluid":True, "background-color": "#172952"})


app.layout = url_bar_and_content_div

app.validation_layout = html.Div([
    dashboard_layout,
    url_bar_and_content_div,
])



@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('lru-cache', 'data')
)
def display_page(pathname, cache):
    if pathname == '/':
        return dashboard_layout
    else:
        return '404'

    
@callback(
    Output('output-graph-1', 'figure'),
    Output('date-markdown', 'children'),
    Input('dropdown-component-final', 'value'),
    Input('dropdown-stat-type', 'value'),
    Input('dropdown-start-year', 'value'),
    Input('dropdown-start-month', 'value'),
    Input('dropdown-end-year', 'value'),
    Input('dropdown-end-month', 'value')
)
def update_graph_1(dropdown_input, stat_type, start_year, start_month, end_year, end_month):
    if stat_type == 'Total':
        stat = 'total'
    if stat_type == 'Fractional':
        stat = 'fractional'
        
    df = get_count_graph(dropdown_input, start_year, start_month, end_year, end_month)
    df.sort_values(axis=0, by=stat, ascending=False, inplace=True)

        
    figure = px.bar(
                df,
                x=stat,
                y='location',
                height=230,
                width=480,
                color_discrete_sequence=[COLORS['general']]*len(df),
                hover_name='location',
                hover_data=stat,
                text=stat,
                orientation='h')
    
    figure.layout.autosize=True
    figure.layout.plot_bgcolor=COLORS['content-background']
    figure.layout.paper_bgcolor=COLORS['content-background']
    figure.layout.font.color=COLORS['general']
    figure.layout.font.size=10
    
    figure.layout.yaxis.title=""
    figure.layout.xaxis.title="Incidents reported ({})".format(stat)
    figure.layout.xaxis.gridcolor=COLORS['content-background']
    figure.layout.yaxis.gridcolor=COLORS['content-background']
    figure.layout.xaxis.tickangle=90
    
    
        
    figure.update_layout(
                margin={'b':10,'r':10,'l':10,'t':10})
    

    d = {'1':'January', '2':'February', '3':'March', '4':'April', '5':'May', '6':'June', '7':'July', '8':'August', '9':'September', '10':'October', '11':'November', '12':'December'}
    md = '''
            > Graph 1: Showing statistic '{}' from {} {} until {} {}
        '''.format(stat, d[start_month], start_year, d[end_month], end_year)
        
    return figure, md
    
        
@callback(
    Output('output-graph-2', 'figure'),
    Output('graph-2-location-store', 'data'),
    Input('output-map-1', 'clickData'),
    Input('dropdown-start-year', 'value'),
    Input('dropdown-start-month', 'value'),
    Input('dropdown-end-year', 'value'),
    Input('dropdown-end-month', 'value'),
    State('graph-2-location-store', 'data')
)
def update_category(click_data_map, start_year, start_month, end_year, end_month, location):
    location = location
    update_store = location
    if ctx.triggered_id == 'output-map-1':
        location = click_data_map['points'][0]['hovertext']
        update_store = location
        
    

    df = get_category(location, start_year, start_month, end_year, end_month)
    df.sort_values(axis=0, by='ratio', ascending=False, inplace=True)
    
    figure = px.bar(
                df,
                x='ratio',
                y='category',
                height=230,
                width=460,
                hover_name='category',
                hover_data='ratio',
                text='ratio',
                color_discrete_sequence=[COLORS['general']]*len(df),
                orientation='h',
    )

    figure.layout.xaxis.title="Category ratio"
    figure.layout.yaxis.title=""
    figure.layout.xaxis.gridcolor=COLORS['content-background']
    figure.layout.yaxis.gridcolor=COLORS['content-background']
    
    figure.update_layout(
                autosize=True,
                margin={'b':10,'r':10,'l':10,'t':10},
                plot_bgcolor=COLORS['content-background'],
                paper_bgcolor=COLORS['content-background'],
                font={'color': COLORS['top-bar-color'], 'size': 10},
                showlegend=False)
    
    return figure, update_store
    
    

@callback(
    Output('dropdown-component-final', 'options'),
    Output('dropdown-component-final', 'value'),
    Input('memory-output', 'data')
)
def update_dropdown(json_data):
    df = pd.read_json(json_data, orient="split")
    dropdown_list = df['city'].unique()
    options = [{"label": x, "value": x} for x in dropdown_list]
    values = dropdown_list[:10]
    return options, values


@callback(
    Output('output-map-1', 'figure'),
    Input('dropdown-component-final', 'value'),
    Input('dropdown-stat-type', 'value'),
    Input('dropdown-start-year', 'value'),
    Input('dropdown-start-month', 'value'),
    Input('dropdown-end-year', 'value'),
    Input('dropdown-end-month', 'value')
    
)
def update_map(dropdown_input, stat_type, start_year, start_month, end_year, end_month):
    df = get_count_map(dropdown_input, start_year, start_month, end_year, end_month)

    scale = px.colors.sequential.Blues[2:]
    
    if stat_type == 'Total':
        stat = 'total'
    if stat_type == 'Fractional':
        stat = 'fractional'
        
    figure = px.scatter_mapbox(df,
                lat='lat',
                lon='lng',
                color=stat,
                size=stat,
                hover_name='location',
                hover_data=stat,
                color_continuous_scale=scale,
                zoom=5,
                height=320
    )
    
    figure.update_layout(
                mapbox_style="carto-positron",
                autosize=True,
                margin={'b':0,'r':0,'l':0,'t':0},
                paper_bgcolor=COLORS['content-background'],
                coloraxis_colorbar_showticklabels=False,
                coloraxis_colorbar_title="",
                coloraxis_colorbar_x=0.90,
                coloraxis_colorbar_thickness=70
    )
                
    return figure

    
if __name__ == '__main__':
    app.run_server(debug=True)

