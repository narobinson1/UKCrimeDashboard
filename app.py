# Import packages
from dash import Dash, DiskcacheManager, CeleryManager, html, dcc, callback, Output, Input, State, ctx
from dash.exceptions import PreventUpdate
import dash_daq as daq

import pandas as pd
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
        f.append(s_)
        
        
    
    d = {'location':l_, 'total':s, 'fractional':f}
    df = pd.DataFrame(d)
    
    return df
    
# Get statistics from db
def get_category(l):
    cnx = mysql.connector.connect(
            user='root',
            password='rootuser',
            host='127.0.0.1',
            database='ukgovcrime')

    cursor = cnx.cursor()
    query_category_data = ("SELECT * FROM category_data WHERE location IN (%s)")
    r = tuple([l])
    cursor.execute(query_category_data, r)

    ca = []
    c = []
    for (hash, location, category, count) in cursor:
        ca.append(category)
        c.append(int(count))

    d = {'category':ca, 'count':c}
    df = pd.DataFrame(d)
    return df
    
# Get statistics from db
def get_count_map(ls):
    cnx = mysql.connector.connect(
            user='root',
            password='rootuser',
            host='127.0.0.1',
            database='ukgovcrime')

    cursor = cnx.cursor()
    
    r = tuple(ls)
    format_strings = ','.join(['%s'] * len(r))
    query_dropdown_data = ("SELECT * FROM dropdown_data WHERE location IN (%s)" % format_strings)

    cursor.execute(query_dropdown_data, r)

    l = []
    la = []
    lg = []
    c = []
    
    for (hash, location, lat, lng, count) in cursor:
        l.append(location)
        la.append(float(lat))
        lg.append(float(lng))
        c.append(int(count))

    
    d = {'location':l, 'lat':la, 'lng':lg, 'count':c}
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
                                dcc.Link(
                                    children=[
                                        html.Button(
                                            children=['Performance statistics'],
                                            style={
                                                'float':'right',
                                                'padding':'16px',
                                                'border':'3px solid',
                                                'borderColor':COLORS['general'],
                                                'background-color':COLORS['content-background'],
                                                'color':COLORS['general'],
                                                'font-weight':'bold',
                                                'box-shadow':'0 0 10px #2fa4e7'
                                            }
                                        )
                                    ],
                                    href='/behind'
                                ),
                                html.Div([
                                    html.H1('UK Crime rates', style={'margin-right': '0.5rem', 'display':'inline', 'width':'20vw', 'margin-bottom':'10rem', 'font-weight':'300'}),
                                    html.H1('| Python, Dash, MySQL', style={'font-weight':'10', 'margin-right':'0', 'padding':'0', 'width':'25vw', 'display':'inline'})
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
                                style={'background-color': COLORS['top-bar-background']},
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
                                            style={'font-weight':'100', 'margin-bottom':'2rem'}
                                        ),
                                        html.Div(
                                            children=[
                                                html.H6('Crime count divided by total population'),
                                                dcc.Dropdown(
                                                    options=[{"label": x, "value": x} for x in ['Total', 'Fractional']],
                                                    value='Total',
                                                    style={'background-color':COLORS['content-background'], 'color':'#2fa4e7'},
                                                    id='dropdown-stat-type'
                                                ),
                                            ],
                                            style={'margin-bottom':'2rem'}
                                        ),
                                        html.Div(
                                            children=[
                                                html.H6('Date period when crimes occured'),
                                                
                                                html.Div(
                                                    children=[
                                                        html.Div(
                                                            children=[
                                                                dcc.Dropdown(
                                                                    options=[{"label": str(x), "value": str(x)} for x in range(2000, 2024)],
                                                                    value='2023',
                                                                    style={'background-color':COLORS['content-background'], 'color':'#2fa4e7', 'width':'7rem', 'margin-top': '5px', 'margin-bottom': '5px'},
                                                                    placeholder='Start year',
                                                                    id='dropdown-start-year'
                                                                ),
                                                                dcc.Dropdown(
                                                                    options=[{"label": str(x), "value": str(x)} for x in range(1, 13)],
                                                                    value='1',
                                                                    style={'background-color':COLORS['content-background'], 'color':'#2fa4e7', 'width':'7rem'},
                                                                    placeholder='Start month',
                                                                    id='dropdown-start-month'
                                                                )
                                                            ],
                                                            style={'display':'inline-block', 'padding':'20px'}
                                                        ),
                                                        html.Div(
                                                            children=[
                                                                'arrow'
                                                            ],
                                                            style={'display':'inline-block'}
                                                        ),
                                                        html.Div(
                                                            children=[
                                                                dcc.Dropdown(
                                                                    options=[{"label": x, "value": x} for x in range(2000, 2024)],
                                                                    value='2023',
                                                                    style={'background-color':COLORS['content-background'], 'color':'#2fa4e7', 'width':'7rem', 'margin-top': '5px', 'margin-bottom': '5px'},
                                                                    placeholder='End year',
                                                                    id='dropdown-end-year'
                                                                ),
                                                                dcc.Dropdown(
                                                                    options=[{"label": x, "value": x} for x in range(1, 13)],
                                                                    value='12',
                                                                    style={'background-color':COLORS['content-background'], 'color':'#2fa4e7', 'width':'7rem'},
                                                                    placeholder='End month',
                                                                    id='dropdown-end-month'
                                                                )
                                                            ],
                                                            style={'display':'inline-block', 'padding':'20px'}
                                                        ),
                                                        
                                                        
                                                    ]
                                                ),
                                                dcc.Markdown(id='date-markdown', style={"padding":"20px", 'font-weight': '100', 'font-size': '22px'})
            
                                            ],
                                            style={'margin-bottom':'0rem'}
                                        ),
                                        html.Div(
                                            children=[
                                                dcc.Markdown('''
                                                    ###### Data provider
                                                    
                                                    The data used for this project was acquired through the uk.gov Police API.
                                                ''')
                                            ],
                                            style={'font-weight':'100'}
                                            
                                        )
                                        
                                    ],
                                    style={'color':COLORS['general']}
                                )
                                
                                #end children
                            ],
                            style={'width': '30%', 'display':'inline-block', 'border':'1px solid #2fa4e7', 'height':'68vh', 'padding':'20px'}
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
                                                                        config={'displayModeBar':False},
                                                                        id="output-graph-1"
                                                                    )
                                                                ],
                                                                id="graph-loading-1",
                                                                style={"padding-left": "3rem", "padding-right": "3rem", "padding-bottom": "3rem", "padding-top": "0rem"}
                                                            )
                                                        ],
                                                    )
                                                ],
                                                style={"width":"50%", 'margin-left':'0', 'display':'inline-block', 'padding':'20px 20px 20px 20px', 'border':'1px solid #2fa4e7'}
                                            ),
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
                                                                        config={'displayModeBar':False},
                                                                        id="output-graph-2"
                                                                    )
                                                                ],
                                                                id="graph-loading-2",
                                                                style={"padding-left": "3rem", "padding-right": "3rem", "padding-bottom": "3rem", "padding-top": "0rem"}
                                                            )
                                                        ],
                                                        style={'border':'1px solid #2fa4e7'}
                                                    ),
                                                ],
                                                style={"width":"50%", 'margin-right':'0', 'top':'0', 'display':'inline-block', 'padding':'18px 0px 0px 10px'}
                                            ),
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
















behind_layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                dcc.Link(
                                    children=[
                                        html.Button(
                                            children=['Return to dashboard'],
                                            style={
                                                'float':'right',
                                                'padding':'16px',
                                                'border':'3px solid',
                                                'borderColor':COLORS['general'],
                                                'background-color':COLORS['content-background'],
                                                'color':COLORS['general'],
                                                'font-weight':'bold',
                                                'box-shadow':'0 0 10px #2fa4e7'
                                            }
                                        )
                                    ],
                                    href='/'
                                ),
                                html.Div([
                                    html.H1('UK Crime rates', style={'margin-right': '0.5rem', 'display':'inline', 'width':'20vw', 'margin-bottom':'10rem', 'font-weight':'300'}),
                                    html.H1('| Python, Dash, MySQL', style={'font-weight':'10', 'margin-right':'0', 'padding':'0', 'width':'25vw', 'display':'inline'})
                                ],
                                style={'margin-bottom':'2rem', 'color':COLORS['general']}
                                ),
                            ],
                        ),
                    ],
                    style={"padding":"2rem", "background-color": COLORS['content-background']}
                ),
            ],
            style=TOPBAR_STYLE
        ),
        
        html.Div(
            children=[
                html.Div(
                    children=[
                        dcc.Markdown(
                            children=[
                            
                            ],
                            style={'color':COLORS['general']},
                            id='cache-markdown'
                        ),
                    ],
                    style={"padding-left": "3rem", "padding-right": "3rem", "padding-bottom": "3rem", "padding-top": "0rem"}
                ),
            ],
        ),
    ],
    style={"background-color":COLORS['content-background']})
    
app.layout = url_bar_and_content_div

app.validation_layout = html.Div([
    dashboard_layout,
    behind_layout,
    url_bar_and_content_div,
])



@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('lru-cache', 'data')
)
def display_page(pathname, cache):
    if pathname == '/behind':
        
        if cache == '':
            location_hits, location_misses, location_currsize, map_hits, map_misses, map_currsize, category_hits, category_misses, category_currsize = '?', '?', '?', '?', '?', '?', '?', '?', '?'
            
        if cache != '':
            location_hits = cache[0][0]
            location_misses = cache[0][1]
            location_currsize = cache[0][2]
            map_hits = cache[0][0]
            map_misses = cache[0][1]
            map_currsize = cache[0][2]
            category_hits = cache[0][0]
            category_misses = cache[0][1]
            category_currsize = cache[0][2]
            
        behind_layout = html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        dcc.Link(
                                            children=[
                                            html.Button(
                                                children=['Return to dashboard'],
                                                style={
                                                    'float':'right',
                                                    'padding':'16px',
                                                    'border':'3px solid',
                                                    'borderColor':COLORS['general'],
                                                    'background-color':COLORS['content-background'],
                                                    'color':COLORS['general'],
                                                    'font-weight':'bold',
                                                    'box-shadow':'0 0 10px #2fa4e7'
                                                }
                                            )],
                                            href='/'),
                                            html.Div([
                                                html.H1('UK Crime rates', style={'margin-right': '0.5rem', 'display':'inline', 'width':'20vw', 'margin-bottom':'10rem', 'font-weight':'300'}),
                                                html.H1('| Python, Dash, MySQL', style={'font-weight':'10', 'margin-right':'0', 'padding':'0', 'width':'25vw', 'display':'inline'})
                                            ],
                                            style={'margin-bottom':'6rem'}
                                            ),
                                            html.H1('Performance statistics')
                                    ]
                                ),
                            ],
                            style={"padding":"2rem", "background-color": COLORS['content-background'], "borderBottom":"3px solid #2fa4e7", "box-shadow":"0px 6px 10px #2fa4e7"}
                        ),
                    ],
                    style=TOPBAR_STYLE
                ),
                
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                dcc.Markdown(
                                    children=[
                                        '''
                                            ### Python
                                            
                                            * Functools lru_cache: data retrieval function calls with identical arguments are cached using lru_cache. The following data results from your interaction with the dashboard:
                                                
                                                Location cache:
                                                
                                                *Cache hits: {},*
                                                *Cache misses: {},*
                                                *Cache stores: {}*
                                                
                                                Category cache:
                                                
                                                *Cache hits: {},*
                                                *Cache misses: {},*
                                                *Cache stores: {}*
                                                
                                                Map cache:
                                                
                                                *Cache hits: {},*
                                                *Cache misses: {},*
                                                *Cache stores: {}*
                                                
                                        '''.format(location_hits, location_misses, location_currsize, category_hits, category_misses, category_currsize, map_hits, map_misses, map_currsize)
                                    ],
                                    style={'color':COLORS['general']},
                                    id='cache-markdown'
                                ),
                            ],
                            style={"padding-left": "3rem", "padding-right": "3rem", "padding-bottom": "3rem", "padding-top": "8rem"}
                        ),
                    ],
                    style={"padding":"40px"}
                ),
            ],
            style={"background-color":COLORS['content-background']})
        
        return behind_layout
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
    df = get_count_graph(dropdown_input, start_year, start_month, end_year, end_month)
    df.sort_values(axis=0, by='total', ascending=False, inplace=True)
    
    
    if stat_type == 'Total':
        stat = 'total'
    if stat_type == 'Fractional':
        stat = 'fractional'
        
    figure = px.bar(
                df,
                x='location',
                y=stat,
                height=160,
                width=400,
                color_discrete_sequence=[COLORS['general']]*len(dropdown_input))
                
    figure.update_layout(
                autosize=False,
                margin={'b':10,'r':10,'l':10,'t':10},
                plot_bgcolor=COLORS['content-background'],
                paper_bgcolor=COLORS['content-background'],
                font={'color': COLORS['general'], 'size': 10})
    
    figure.update_xaxes(showticklabels=False, title_text=stat)
    figure.update_yaxes(showticklabels=False, title_text="{} count per location".format(stat))

    d = {'1':'January', '2':'February', '3':'March', '4':'April', '5':'May', '6':'June', '7':'July', '8':'August', '9':'September', '10':'October', '11':'November', '12':'December'}
    md = '''
            > Showing statistic '{}' from {} {} until {} {}
        '''.format(stat, d[start_month], start_year, d[end_month], end_year)
        
    return figure, md
    
        
@callback(
    Output('output-graph-2', 'figure'),
    Input('output-map-1', 'clickData')
)
def update_category(click_data_map):
    if ctx.triggered_id != 'output-map-1':
        location='London'
    elif ctx.triggered_id == 'output-map-1':
        location = click_data_map['points'][0]['hovertext']

    df = get_category(location)
    df.sort_values(axis=0, by='count', ascending=False, inplace=True)

    figure = px.bar(
                df,
                x='category',
                y='count',
                height=160,
                width=400,
                color_discrete_sequence=[COLORS['general']]*len(df)
    )
    figure.update_layout(
                autosize=True,
                margin={'b':10,'r':10,'l':10,'t':10},
                plot_bgcolor=COLORS['content-background'],
                paper_bgcolor=COLORS['content-background'],
                font={'color': COLORS['top-bar-color'], 'size': 16},
                showlegend=False)
    
    figure.update_xaxes(showticklabels=False, title_text="")
    figure.update_yaxes(showticklabels=False, title_text="")
    
    return figure
    
    

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
    Input('dropdown-component-final', 'value')
)
def update_map(dropdown_input):
    l = []
    for x in dropdown_input:
        l.append(tuple([x]))

    hashable_input = tuple(l)
    df = get_count_map(hashable_input)
    
    totals = df['count']
    lat = df['lat']
    lng = df['lng']
    location = df['location']
    
    figure = px.scatter_mapbox(
                lat=lat,
                lon=lng,
                color=totals,
                size=totals,
                hover_name=location,
                color_continuous_scale=px.colors.sequential.Blues,
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

