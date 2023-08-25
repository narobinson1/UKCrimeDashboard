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
    "content-background": "#180373",
    "general": "#2fa4e7"
}

TOPBAR_STYLE = {
    "background-color": COLORS['top-bar-background'],
    "color": COLORS['top-bar-color'],
}

CONTENT_STYLE = {
    "background-color": '#0e0340'
}

df_g = pd.read_csv("gb_latlon.csv")

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

d = date_range('2020', '1', '2023', '12')

def fetch_data(lat, lng):
        payload = {'lat':lat, 'lng':lng}
        r = requests.post("https://data.police.uk/api/crimes-street/all-crime", params=payload)
        if r.status_code == 404:
            return ""
        else:
            res = r.json()
            return res
            
# Get totals from db
def get_count_graph(dropdown_input):
    l_ = []
    t_ = []
    f_ = []
    la_ = []
    ln_ = []
    
    for location in dropdown_input:
        df = df_g[df_g['city'] == location]
        lat = float(df.lat)
        lng = float(df.lng)
        
        p = int(df.population)
        data = fetch_data(lat, lng)

        t = len(data)

        f = t/p
        
        l_.append(location)
        t_.append(t)
        f_.append(float(str(f*100)[:5]))
                
    d = {'location':l_, 'total':t_, 'fractional':f_}
    df = pd.DataFrame(d)

    return df
    
# Get statistics from db
def get_category(location):
    df = df_g[df_g['city'] == location]
    lat = float(df.lat)
    lng = float(df.lng)

    p = int(df.population)


    data = fetch_data(lat, lng)
    t = len(data)
    
    c = []
    cc = []
    if t != 0:
        df = pd.DataFrame(data)
        df = df['category'].value_counts()
        l = list(df)
        
        for x in df.index:
            c.append(' '.join(x.split('-')).capitalize())
            
        for x in l:
            cc.append(float(str((x/sum(l))*100)[:3]))
        
    d = {'category':c,'ratio':cc}

    df = pd.DataFrame(d)
        
    return df

    
# Get statistics from db
def get_count_map(dropdown_input):
    l_ = []
    t_ = []
    f_ = []
    la_ = []
    ln_ = []
    
    for location in dropdown_input:
        df = df_g[df_g['city'] == location]
        lat = float(df.lat)
        lng = float(df.lng)
        
        p = int(df.population)
        data = fetch_data(lat, lng)

        t = len(data)

        f = t/p
        
        l_.append(location)
        t_.append(t)
        f_.append(float(str(f*100)[:5]))
        la_.append(lat)
        ln_.append(lng)
                
    d = {'location':l_, 'total':t_, 'fractional':f_, 'lat':la_, 'lng':ln_}
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
                                        
                                        html.Img(src='assets/github.png', id='github-logo', height=70, style={'display':'inline', 'float':'right', 'padding-bottom':'16px'})
#
                                    ],
                                    href='https://github.com/narobinson1',
                                    target='_blank'
                                ),
                                html.Div(
                                    children=[
                                        html.H1('UK Crime rates', style={'margin-right': '0.5rem', 'display':'inline', 'width':'20vw', 'margin-bottom':'10rem', 'font-weight':'300'}),
                                        html.H1('| Python, Dash, MySQL', style={'font-weight':'10', 'margin-right':'0', 'padding':'0', 'width':'25vw', 'display':'inline'}),
                                        html.Button('GUIDE', className='menu-btn-guide', name='menu', style={'color':COLORS['general'], 'background-color':COLORS['content-background'], 'font-weight':'100', 'font-size':'30px', 'position':'relative', 'left':'28rem'}),
                                        html.P('''Under the section 'Choose locations' there is an extensive list of locations in the UK to choose from. These locations are used in the Dashboard configuration section, before being represented in the form of figures. The 'Dashboard configuration' section provides the possibility to illustrate either total or fractional crime counts. The fractional crime counts are the total divided by the population of the location the crimes occured, and the total crime counts is the sum of all crimes, regardless of category, which occurred in a specific location. The 'Dashboard configuration' section also provides the ability to control the time period in which the crimes occured.''', style={'color':COLORS['general'], 'font-weight':'100', 'background-color':COLORS['content-background'], 'margin-left':'-32px', 'padding':'20px','margin-top':'36px', 'border':'10px solid #0e0340'}, className='guide-text'),
                                        
                                        html.Button('NOTES', className='menu-btn-notes', name='menu', style={'color':COLORS['general'], 'background-color':COLORS['content-background'], 'font-weight':'100', 'font-size':'30px', 'position':'relative', 'left':'30rem'}),
                                        html.P('''The data functionality of the dashboard is currently unavailable. This version of the dashboard queries data directly from the UK Police Application Programming Interface, and therefore the time needed to process data in real-time would be too significant. Developed on a separate branch from the main git repository, another version of the dashboard has this data functionality available as it queries pre-processed data from a local mysql database instead of performing real-time processing. The upkeep of renting storage space on a cloud service like AWS, Google Cloud or Microsoft Azure is too expensive, so the database version of this dashboard is not accessible remotely.''', style={'color':COLORS['general'], 'font-weight':'100', 'background-color':COLORS['content-background'], 'margin-left':'-32px', 'padding':'20px','margin-top':'36px', 'border':'10px solid #0e0340'}, className='notes-text'),
                                        
                                        html.Button('ABOUT', className='menu-btn-about', name='menu', style={'color':COLORS['general'], 'background-color':COLORS['content-background'], 'font-weight':'100', 'font-size':'30px', 'position':'relative', 'left':'8rem'}),
                                        html.P('''This dashboard presents police data offered through the openly-available United Kingdom Government Police Application Programming Interface
                                        in JSON format. The data is presented as clearly as possible through interactive graphs and a central interactive map. Functionalities available include total and fractional crime count among a list of selected locations, and the ratio of specific crime categories for individual locations. The main value this dashboard offers is the possibility to shed light on the reported intensity and frequency of crimes amongst locations in the UK, through the observation of Police data.''', style={'color':COLORS['general'], 'font-weight':'100', 'background-color':COLORS['content-background'], 'margin-left':'-32px', 'padding':'20px','margin-top':'36px', 'border':'10px solid #0e0340'}, className='about-text'),
                                        html.Div(style={'color':COLORS['general'], 'font-weight':'100', 'background-color':'black', 'margin-left':'-32px', 'padding':'20px','margin-top':'36px', 'border-bottom':'1px solid', 'height':'90vh', 'width':'100vw'}, className='mist')
                                        
                                    ],
                                    style={'padding-bottom':'0rem'}
                                ),
                            ],
                            
                        ),
                    ],
                    style={"padding":"2rem 2rem 2rem 2rem", "background-color":COLORS['content-background']}
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
                                style={'background-color': COLORS['content-background'], 'font-weight':'100'},
                                id='dropdown-component-final')
                            ],
                            style={'padding':'10px 10px 10px 10px', 'color':'#2fa4e7', 'margin-bottom':'16px', 'background-color':'#180373', 'border-radius':'10px'}
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
                                                html.P('Statistical metric', style={'font-weight':'100'}),
                                                dcc.Dropdown(
                                                    options=[{"label": x, "value": x} for x in ['Total', 'Fractional']],
                                                    value='Total',
                                                    style={'background-color':COLORS['content-background'], 'color':'#2fa4e7', 'font-weight':'100'},
                                                    id='dropdown-stat-type'
                                                ),
                                            ],
                                            style={'margin-bottom':'2rem'}
                                        ),
                                        html.Div(
                                            children=[
                                                html.P('Date period when crimes occured', style={'font-weight':'100'}),
                                                
                                                html.Div(
                                                    children=[
                                                        dcc.ConfirmDialog(
                                                            id='date-selection-error',
                                                            message='The date functionality is not currently available. Take a look at the "notes" section to discover the reason why.',
                                                        ),
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
                                                                    value='1',
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
                                                dcc.Markdown(id='date-markdown-1', style={"padding":"0px", 'font-weight': '200', 'font-size': '20px', 'margin-top':'1.6rem'}),
                                                dcc.Markdown(id='date-markdown-2', style={"padding":"0px", 'font-weight': '200', 'font-size': '20px'})
            
                                            ],
                                            style={'margin-bottom':'-1rem'}
                                        ),
                                        
                                        
                                    ],
                                    style={'color':COLORS['general'], 'padding':'20px', 'margin-bottom':'16px', 'background-color':'#180373', 'border-radius':'10px'}
                                ),
                                html.Div(
                                    children=[
                                        dcc.Markdown('''
                                            ###### Data provider
                                            
                                            The data used for this project was acquired through the uk.gov Police API.
                                        ''', style={'color':COLORS['general'], 'font-size':'14px'}),
                                        
                                    ],
                                    style={'font-weight':'100', 'padding':'20px 20px 1px 20px', 'background-color':'#180373', 'border-radius':'10px'}
                                    
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
                                                                        'height': 272
                                                                    }
                                                                },
                                                                config={'displayModeBar':False, 'autosizable':True},
                                                                id="output-map-1")
                                                        ],
                                                        id="map-loading-1",
                                                        type='cube'
                                                    )
                                                ],
                                                # Parent div map loading style
                                                style={'background-color':'#180373'}
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
                                                                                        'height': 274,
                                                                                        'autosize': False,
                                                                                        'width': 460
                                                                                    }
                                                                                },
                                                                                config={'displayModeBar':False, 'editSelection':False, 'editable':False, 'showAxisDragHandles':False, 'showAxisRangeEntryBoxes':False, 'responsive':False, 'autosizable':False, 'fillFrame':False, 'scrollZoom':False},
                                                                                id="output-graph-1"
                                                                            )
                                                                        ],
                                                                        id="graph-loading-1",
                                                                        style={'position':'relative', 'left':'120px'},
                                                                    )
                                                                ],
                                                            )
                                                        ],
                                                        style={"width":"50%", 'padding':'0px 0px 0px 0px'}
                                                    ),
                                                ],
                                                style={'margin-top':'1rem', 'padding':'0px 10px 0px 0px', 'display':'inline-block', 'background-color':'#180373'}
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
                                                                                        'height': 274,
                                                                                        'autosize': False,
                                                                                        'width': 460
                                                                                    }
                                                                                },
                                                                                config={'displayModeBar':False, 'scrollZoom':False},
                                                                                id="output-graph-2"
                                                                            )
                                                                        ],
                                                                        id="graph-loading-2",
                                                                        style={'position':'relative', 'left':'120px'},
                                                                        type='circle'
                                                                    ),
                                                                    dcc.Store(id='graph-2-location-store', data='London')
                                                                ],
                                                            ),
                                                        ],
                                                        style={"width":"50%", 'padding':'0px 0px 0px 10px'}
                                                    ),
                                                ],
                                                style={'margin-top': '1rem', 'padding':'0px 0px 0px 0px', 'display':'inline-block', 'background-color':'#180373', 'float':'right'}
                                            )
                                                    
                                        ],
                                    
                                    ),
                                            #end children
                                        ]
                                )
                            ],
                            style={'width':'70%', 'display':'inline-block', 'background-color':'#0e0340', 'float':'right', 'padding': '0px 0px 0px 18px', 'height':'68vh'}

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
    Output('date-selection-error','displayed'),
    Output('dropdown-start-year', 'value'),
    Output('dropdown-start-month', 'value'),
    Output('dropdown-end-year', 'value'),
    Output('dropdown-end-month', 'value'),
    Input('dropdown-start-year', 'value'),
    Input('dropdown-start-month', 'value'),
    Input('dropdown-end-year', 'value'),
    Input('dropdown-end-month', 'value'),
    prevent_initial_call=True
)
def confirm_dialog(start_year, start_month, end_year, end_month):
    return True, '2023', '1', '2023', '1'
        
@callback(
    Output('output-graph-1', 'figure'),
    Output('date-markdown-1', 'children'),
    Input('dropdown-component-final', 'value'),
    Input('dropdown-stat-type', 'value'),
)
def update_graph_1(dropdown_input, stat_type):
    if stat_type == 'Total':
        stat = 'total'
    if stat_type == 'Fractional':
        stat = 'fractional'
        
    df = get_count_graph(dropdown_input)
    df.sort_values(axis=0, by=stat, ascending=True, inplace=True)
    
    figure = px.bar(
                df,
                x=stat,
                y='location',
                height=274,
                width=460,
                color_discrete_sequence=[COLORS['general']]*len(df),
                orientation='h')
    
    figure.update_traces(hovertemplate=None)
    figure.layout.hovermode="y"
    figure.layout.autosize=True
    figure.layout.plot_bgcolor=COLORS['content-background']
    figure.layout.paper_bgcolor=COLORS['content-background']
    figure.layout.font.color=COLORS['general']
    figure.layout.font.size=10
    
    figure.layout.yaxis.ticksuffix="  "
    figure.layout.yaxis.title=""
    figure.layout.xaxis.title="Graph 1: Incidents reported ({})".format(stat)
    figure.layout.xaxis.gridcolor=COLORS['content-background']
    figure.layout.yaxis.gridcolor=COLORS['content-background']
    figure.layout.xaxis.tickangle=90
    
    
        
    figure.update_layout(
                margin={'b':10,'r':10,'l':10,'t':10})
    

    md = '''
            > Graph 1: Showing statistic '{}'
        '''.format(stat)
        
    return figure, md
    
        
@callback(
    Output('output-graph-2', 'figure'),
    Output('graph-2-location-store', 'data'),
    Output('date-markdown-2', 'children'),
    Input('output-map-1', 'clickData'),
    State('graph-2-location-store', 'data')
)
def update_category(click_data_map, location):
    location = location
    update_store = location
    if ctx.triggered_id == 'output-map-1':
        location = click_data_map['points'][0]['hovertext']
        update_store = location
        
    

    df = get_category(location)
    df.sort_values(axis=0, by='ratio', ascending=False, inplace=True)
    
    figure = px.bar(
                df,
                x='ratio',
                y='category',
                height=274,
                width=460,
                color_discrete_sequence=[COLORS['general']]*len(df),
                orientation='h',
    )

    figure.layout.title='{}'.format(location)
    figure.layout.title.x=0.98
    figure.layout.title.y=0.9
    figure.layout.title.font.size=40
    figure.update_traces(hovertemplate=None)
    figure.layout.hovermode="y"
    figure.layout.yaxis.ticksuffix="  "
    figure.layout.xaxis.title="Graph 2: Category ratio percentage"
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

    md = '''
            > Graph 2: Showing location '{}'
        '''.format(location)
        
    return figure, update_store, md
    
    

@callback(
    Output('dropdown-component-final', 'options'),
    Output('dropdown-component-final', 'value'),
    Input('memory-output', 'data')
)
def update_dropdown(json_data):
    df = pd.read_json(json_data, orient="split")
    dropdown_list = list(df['city'].unique())
    options = [{"label": x, "value": x} for x in dropdown_list][:10]
    values = dropdown_list[:10]
    return options, values


@callback(
    Output('output-map-1', 'figure'),
    Input('dropdown-component-final', 'value'),
    Input('dropdown-stat-type', 'value'),
)
def update_map(dropdown_input, stat_type):
    df = get_count_map(dropdown_input)

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
                height=272
    )
    
    figure.update_layout(
                mapbox_style="carto-positron",
                autosize=True,
                margin={'b':0,'r':0,'l':0,'t':0},
                paper_bgcolor=COLORS['content-background'],
                coloraxis_colorbar_showticklabels=False,
                coloraxis_colorbar_title="",
                coloraxis_colorbar_x=0.92,
                coloraxis_colorbar_thickness=50
    )
                
    return figure

    
if __name__ == '__main__':
    app.run_server(debug=True)

