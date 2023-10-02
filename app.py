# Import packages

from __future__ import annotations

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
from dash_extensions import DeferScript
from dash.dependencies import Component
from plotly.graph_objects import Figure
# Initialize the app - incorporate a Dash Bootstrap theme
external_stylesheets = [dbc.themes.CERULEAN]
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

COLORS = {
    "content-background": "#180373",
    "general": "#f0948d"
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


def date_range(start_year: int, start_month: int, end_year: int, end_month: int) -> list[str]:
    """Creates and returns a list of dates in consequtive order in the string format 'YYYY-MM'
    
    Args:
        start_year (int): The start year of the range of dates
        start_month (int): The start month of the range of dates
        end_year (int): The end year of the range of dates
        end_month (int): The end month of the ranges of dates
    
    Returns:
        list: a list of strings in the format 'YYYY-MM'
    """
    r = []
    for y in range(start_year, end_year+1):
        s = 1
        e = 13
        if y == start_year:
            s = start_month
            e = 13
        if y == end_year:
            s = 1
            e = end_month + 1
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

d = date_range(2020, 1, 2023, 12)

def fetch_data(lat: float, lng: float):
    """Post request including latitude and longitude coordinates sent to Police API, crime data returned as json object
    
    Args:
        lat (float): The latitude of the desired city
        lng (float): The longitude of the desired city
    
    Returns:
        list: a json object containing crime data for desired city
    """
    payload = {'lat':lat, 'lng':lng}
    r = requests.post("https://data.police.uk/api/crimes-street/all-crime", params=payload)
    if r.status_code == 404:
        return ""
    else:
        res = r.json()
        return res

    
# Get totals from db
def get_count_graph(dropdown_input: list[str]) -> pd.DataFrame:
    """Total and fractional counts for each city in dropdown_input derived and stored in pandas dataframe
    
    Args:
        dropdown_input (list[str]): A list of city names
        
    Returns:
        pd.DataFrame: a dataframe containing total and fractional counts for each city
    """
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
    d = {'location': l_, 'total': t_, 'fractional': f_}
    df = pd.DataFrame(d)
    return df
    


# Get statistics from db
def get_category(location: str) -> pd.DataFrame:
    """Total and fractional counts for each category in 'location' derived and stored in pandas dataframe
    
    Args:
        location (str): A city name in the UK
        
    Returns:
        pd.DataFrame: a dataframe containing total and fractional counts for each city
    """
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
def get_count_map(dropdown_input: list[str]) -> pd.DataFrame:
    """Total and fractional counts, including latitude and longitude coordinates, for each city in dropdown_input derived and stored in pandas dataframe
    
    Args:
        dropdown_input (list[str]): A list of city names
        
    Returns:
        pd.DataFrame: a dataframe containing total and fractional counts, including latitude and longitude coordinates, for each city
    """
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
        DeferScript(src="assets/tutorial.js"),
        html.Div(style={'color':COLORS['general'], 'font-weight':'100', 'background-color':'black', 'height':'100vh', 'width':'100vw'}, id='mist-id'),
        html.Div([
            html.H6('Welcome!'),
            html.P('Follow this brief tutorial to get started.'),
            html.Button('next', id='tutorial-1-btn-forward')
            ],
            id='tutorial-1',
            className='visible'
        ),
        html.Div([
            html.H6('Header'),
            html.P('Hover over the headers for more information'),
            html.Button('.', id='tutorial-2-btn-back'),
            html.Button('.', id='tutorial-2-btn-forward')
            ],
            id='tutorial-2',
            className='hidden',
        ),
        html.Div([
            html.H6('Locations'),
            html.P('Choose locations from a list of 10 cities'),
            html.Button('.', id='tutorial-3-btn-back'),
            html.Button('.', id='tutorial-3-btn-forward')
            ],
            id='tutorial-3',
            className='hidden',
        ),
        html.Div([
            html.H6('Config'),
            html.P('Adjust date periods and the statistical metric displayed'),
            html.Button('.', id='tutorial-4-btn-back'),
            html.Button('.', id='tutorial-4-btn-forward')
            ],
            id='tutorial-4',
            className='hidden',
        ),
        html.Div([
            html.H6('Location graph'),
            html.P('This graph shows the statistical metric per location'),
            html.Button('.', id='tutorial-5-btn-back'),
            html.Button('.', id='tutorial-5-btn-forward')
            ],
            id='tutorial-5',
            className='hidden',
        ),
        html.Div([
            html.H6('Category graph'),
            html.P('This graph shows the statistical metric per category'),
            html.Button('.', id='tutorial-6-btn-back'),
            html.Button('.', id='tutorial-6-btn-forward')
            ],
            id='tutorial-6',
            className='hidden',
        ),
        html.Div([
            html.H6('Map'),
            html.P('This map illustrates the crime intensity in cities visually'),
            html.Button('.', id='tutorial-7-btn-back'),
            html.Button('.', id='tutorial-7-btn-forward')
            ],
            id='tutorial-7',
            className='hidden',
        ),
        html.Div([
            html.H6('End of tutorial'),
            html.P('Thank you for following the tutorial!'),
            html.Button('.', id='tutorial-8-btn-back'),
            html.Button('.', id='tutorial-8-btn-forward')
            ],
            id='tutorial-8',
            className='hidden',
        ),
        

        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.A(
                                    children=[
                                        html.Img(src='assets/github.png', id='github-logo', height=70, style={'display':'inline', 'float':'right', 'padding-bottom':'16px'})
                                    ],
                                    href='https://github.com/narobinson1',
                                    target='_blank'
                                ),
                                html.Div(
                                    children=[
                                        html.H1('UK Crime rates', id='app-heading', style={'margin-right': '0.5rem', 'display':'inline', 'width':'20vw', 'margin-bottom':'10rem', 'font-weight':'300', 'color':COLORS['general']}),
                                        html.H1('| a statistical dashboard', id='app-sub-heading', style={'font-weight':'10', 'margin-right':'0', 'padding':'0', 'width':'25vw', 'display':'inline', 'color':COLORS['general']}),
                                        html.Button('GUIDE', id='app-guide-header', className='menu-btn-guide', name='menu', style={'color':COLORS['general'], 'background-color':COLORS['content-background'], 'font-weight':'100', 'font-size':'30px', 'position':'relative', 'left':'28rem'}),
                                        html.P('''Under the section 'Choose locations' there is an extensive list of locations in the UK to choose from. These locations are used in the Dashboard configuration section, before being represented in the form of figures. The 'Dashboard configuration' section provides the possibility to illustrate either total or fractional crime counts. The fractional crime counts are the total divided by the population of the location the crimes occured, and the total crime counts is the sum of all crimes, regardless of category, which occurred in a specific location. The 'Dashboard configuration' section also provides the ability to control the time period in which the crimes occured.''', style={'color':COLORS['general'], 'font-weight':'100', 'background-color':COLORS['content-background'], 'margin-left':'-32px', 'padding':'20px','margin-top':'36px', 'border':'10px solid #0e0340'}, className='guide-text'),
                                        
                                        html.Button('NOTES', id='app-notes-header', className='menu-btn-notes', name='menu', style={'color':COLORS['general'], 'background-color':COLORS['content-background'], 'font-weight':'100', 'font-size':'30px', 'position':'relative', 'left':'30rem'}),
                                        html.P('''The data functionality of the dashboard is currently unavailable. This version of the dashboard queries data directly from the UK Police Application Programming Interface, and therefore the time needed to process data in real-time would be too significant. Developed on a separate branch from the main git repository, another version of the dashboard has this data functionality available as it queries pre-processed data from a local mysql database instead of performing real-time processing. The upkeep of renting storage space on a cloud service like AWS, Google Cloud or Microsoft Azure is too expensive, so the database version of this dashboard is not accessible remotely.''', style={'color':COLORS['general'], 'font-weight':'100', 'background-color':COLORS['content-background'], 'margin-left':'-32px', 'padding':'20px','margin-top':'36px', 'border':'10px solid #0e0340'}, className='notes-text'),
                                        
                                        html.Button('ABOUT', id='app-about-header', className='menu-btn-about', name='menu', style={'color':COLORS['general'], 'background-color':COLORS['content-background'], 'font-weight':'100', 'font-size':'30px', 'position':'relative', 'left':'8rem'}),
                                        html.P('''This dashboard presents police data offered through the openly-available United Kingdom Government Police Application Programming Interface
                                        in JSON format. The data is presented as clearly as possible through interactive graphs and a central interactive map. Functionalities available include total and fractional crime count among a list of selected locations, and the ratio of specific crime categories for individual locations. The main value this dashboard offers is the possibility to shed light on the reported intensity and frequency of crimes amongst locations in the UK, through the observation of Police data.''', style={'color':COLORS['general'], 'font-weight':'100', 'background-color':COLORS['content-background'], 'margin-left':'-32px', 'padding':'20px','margin-top':'36px', 'border':'10px solid #0e0340'}, className='about-text'),
                                    ],
                                    style={'padding-bottom':'0rem'}
                                ),
                            ],
                        ),
                    ],
                    style={"padding":"2rem 2rem 2rem 2rem", "background-color":COLORS['content-background']}
                ),
            ],
            id='header-id',
            className='header'
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
                                style={'background-color': COLORS['content-background'], 'font-weight':'100', 'color':COLORS['general']},
                                id='dropdown-component-final')
                            ],
                            style={'padding':'10px 10px 10px 10px', 'color':COLORS['general'], 'margin-bottom':'16px', 'background-color':'#180373', 'border-radius':'10px'},
                            id='location-dropdown-id',
                            className='location-dropdown above'
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.Div(
                                            children=[
                                                dcc.Markdown('''
                                                    ###### Dashboard configuration
                                                ''')
                                            ],
                                            style={'font-weight':'100', 'margin-bottom':'2rem', 'color':COLORS['general']}
                                        ),
                                        html.Div(
                                            children=[
                                                html.P('Statistical metric', style={'font-weight':'100'}),
                                                dcc.Dropdown(
                                                    options=[{"label": x, "value": x} for x in ['Total', 'Fractional']],
                                                    value='Total',
                                                    style={'background-color':COLORS['content-background'], 'color':COLORS['general'], 'font-weight':'100'},
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
                                                                    style={'background-color':COLORS['content-background'], 'color':COLORS['general'], 'width':'7rem', 'margin-top': '0px', 'margin-bottom': '5px', 'font-weight':'100'},
                                                                    placeholder='Start year',
                                                                    id='dropdown-start-year'
                                                                ),
                                                                dcc.Dropdown(
                                                                    options=[{"label": str(x), "value": str(x)} for x in range(1, 13)],
                                                                    value='1',
                                                                    style={'background-color':COLORS['content-background'], 'color':COLORS['general'], 'width':'7rem', 'font-weight':'100'},
                                                                    placeholder='Start month',
                                                                    id='dropdown-start-month'
                                                                )
                                                            ],
                                                            style={'display':'inline-block', 'padding':'0px'}
                                                        ),
                                                        html.Div(
                                                            children=[
                                                                html.P('UNTIL')
                                                            ],
                                                            style={'display':'inline-block', 'position':'relative', 'left':'55px', 'bottom':'38px'}
                                                        ),
                                                        html.Div(
                                                            children=[
                                                                dcc.Dropdown(
                                                                    options=[{"label": x, "value": x} for x in range(2000, 2024)],
                                                                    value='2023',
                                                                    style={'background-color':COLORS['content-background'], 'color':COLORS['general'], 'width':'7rem', 'margin-top': '0px', 'margin-bottom': '5px', 'font-weight':'100'},
                                                                    placeholder='End year',
                                                                    id='dropdown-end-year'
                                                                ),
                                                                dcc.Dropdown(
                                                                    options=[{"label": x, "value": x} for x in range(1, 13)],
                                                                    value='1',
                                                                    style={'background-color':COLORS['content-background'], 'color':COLORS['general'], 'width':'7rem', 'font-weight':'100'},
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
                                    style={'color':COLORS['general'], 'padding':'20px', 'margin-bottom':'16px', 'background-color':'#180373', 'border-radius':'10px'},
                                    id='dashboard-configuration-id',
                                    className='dashboard-configuration'
                                ),
                                html.Div(
                                    children=[
                                        dcc.Markdown('''
                                            ###### Data provider
                                            
                                            The data used for this project was acquired through the uk.gov Police API.
                                        ''', style={'color':COLORS['general'], 'font-size':'14px'}),
                                        
                                    ],
                                    style={'font-weight':'100', 'padding':'20px 20px 1px 20px', 'background-color':'#180373', 'border-radius':'10px'},
                                    className='data-provider-statement',
                                    id='data-provider-statement-id'
                                ),
                                html.Div(html.Div([html.P('Designed by Nicolas Robinson    Email: nicolas.alexander.robinson@gmail.com   '), html.P('Designed by Nicolas Robinson    Email: nicolas.alexander.robinson@gmail.com    ')], className='marquee'), className='wrapper', id='text-marquee-id')
                            ],
                            style={'width': '30%', 'display':'inline-block', 'height':'70.1vh', 'padding':'0px'},
                            id='left-id'
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
                                                                        'height': 272
                                                                    }
                                                                },
                                                                config={'displayModeBar':False, 'autosizable':True},
                                                                id="output-map-1")
                                                        ],
                                                        id="map-loading-1",
                                                        type='circle',
                                                        color=COLORS['general']
                                                    )
                                                ],
                                                style={'background-color':'#180373'},
                                                id='map-id',
                                                className='map'
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
                                                                                        'width': 440
                                                                                    }
                                                                                },
                                                                                config={'displayModeBar':False, 'editSelection':False, 'editable':False, 'showAxisDragHandles':False, 'showAxisRangeEntryBoxes':False, 'responsive':False, 'autosizable':False, 'fillFrame':False, 'scrollZoom':False},
                                                                                id="output-graph-1"
                                                                            )
                                                                        ],
                                                                        id="graph-loading-1",
                                                                        style={'position':'relative', 'left':'120px'},
                                                                        color=COLORS['general'],
                                                                        type='circle',
                                                                    )
                                                                ],
                                                            )
                                                        ],
                                                        style={"width":"50%", 'padding':'0px 0px 0px 0px'}
                                                    ),
                                                ],
                                                style={'margin-top':'1rem', 'padding':'0px 10px 0px 0px', 'position':'relative', 'display':'inline-block', 'background-color':'#180373'},
                                                id='location-graph-id',
                                                className='location-graph'
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
                                                                                        'width': 450
                                                                                    }
                                                                                },
                                                                                config={'displayModeBar':False, 'scrollZoom':False},
                                                                                id="output-graph-2"
                                                                            )
                                                                        ],
                                                                        id="graph-loading-2",
                                                                        style={'position':'relative', 'left':'120px'},
                                                                        type='circle',
                                                                        color=COLORS['general']
                                                                    ),
                                                                    dcc.Store(id='graph-2-location-store', data='London')
                                                                ],
                                                            ),
                                                        ],
                                                        style={"width":"50%", 'padding':'0px 0px 0px 10px'}
                                                    ),
                                                ],
                                                style={'margin-top': '1rem', 'padding':'0px 0px 0px 0px', 'display':'inline-block', 'background-color':'#180373', 'float':'right'},
                                                id='category-graph-id',
                                                className='category-graph'
                                            )
                                        ],
                                    ),
                                        ]
                                )
                            ],
                            style={'width':'70%', 'display':'inline-block', 'background-color':'#0e0340', 'float':'right', 'padding': '0px 0px 0px 18px', 'height':'68vh'}
                        ),
                    ],
                    style={'padding':'20px'},
                    id='content-id'
                ),
                html.Div([dcc.Store(id='memory-output', storage_type='session', data=pd.read_csv("gb_latlon.csv", dtype=object).to_json(date_format='iso', orient='split'))])
            ],
            style=CONTENT_STYLE
        ),
    ], style={"fluid":True, "background-color": "#172952"}, id='app-id')



@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
)
def display_page(pathname: str) -> Component | str:
    """Handles URL redirection
    
    Args:
        pathname (str): The url pathname, e.g. '/'
    
    Returns:
        Component | str: the central dashboard_layout component or '404'
    """
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
def confirm_dialog(start_year: str, start_month: str, end_year: str, end_month: str) -> tuple[bool, str, str, str, str]:
    """Alerts user of the unavailability of the date functionality
    
    Args:
        start_year (str): the start year
        start_month (str): the start month
        end_year (str): the end year
        end_month (str): the end month
        
    Returns:
        tuple[Boolean, str, str, str, str]: A tuple containing original dates entered and the Boolean True
    """
    return True, start_year, start_month, end_year, end_month
        
@callback(
    Output('output-graph-1', 'figure'),
    Input('dropdown-component-final', 'value'),
    Input('dropdown-stat-type', 'value'),
)
def update_graph_1(dropdown_input: list[str], stat_type: str) -> Figure:
    """Creates a Figure object containing location-related data
    
    Args:
        dropdown_input (list[str]): A list of city names
        stat_type (str): Either 'total' or 'fractional' (divided by population count)
        
    Returns:
        Figure: a plotly figure
    """
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
                width=454,
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
        
    return figure
    
        
@callback(
    Output('output-graph-2', 'figure'),
    Input('output-map-1', 'clickData'),
    State('graph-2-location-store', 'data')
)
def update_category(click_data_map: dict, location: str) -> Figure:
    """Creates a Figure object containing category-related data for a desired location
    
    Args:
        click_data_map (dict): Contains data related to last click event
        location (str): A city in the UK
        
    Returns:
        Figure: a plotly figure
    """
    if ctx.triggered_id == 'output-map-1':
        location = click_data_map['points'][0]['hovertext']
        
    df = get_category(location)
    df.sort_values(axis=0, by='ratio', ascending=False, inplace=True)
    
    figure = px.bar(
                df,
                x='ratio',
                y='category',
                height=274,
                width=454,
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
                font={'color': COLORS['general'], 'size': 10},
                showlegend=False)
        
    return figure
    
    

@callback(
    Output('dropdown-component-final', 'options'),
    Output('dropdown-component-final', 'value'),
    Input('memory-output', 'data')
)
def update_dropdown(json_data) -> tuple[list[dict], list[str]]:
    """Updates the dropdown menu with a list of cities
    
    Args:
        json_data: Contains cities with latitude, longitude and total population data
        
    Returns:
        tuple(list[dict], list[str]): a list of dictionaries and a list of strings
    """
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
def update_map(dropdown_input: list[str], stat_type: str) -> Figure:
    """Creates a Figure object containing location-related data, including latitude and longitude
    
    Args:
        dropdown_input (list[str]): A list of city names
    
    Returns:
        Figure: a plotly figure
    """
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


app.layout = url_bar_and_content_div

app.validation_layout = html.Div([
    dashboard_layout,
    url_bar_and_content_div,
])

    
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)

