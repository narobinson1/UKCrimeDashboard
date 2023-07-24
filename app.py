# Import packages
from dash import Dash, DiskcacheManager, CeleryManager, html, dcc, callback, Output, Input, State, ctx
from dash.exceptions import PreventUpdate

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

import dash_bootstrap_components as dbc

import requests
import functools

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

tab_style = {
    "borderBottom": "1px solid",
    "borderBottomColor": COLORS['general'],
    "padding": "12px",
    "fontWeight": "bold",
    "color": COLORS['general'],
    
}

tab_selected_style = {
    "borderBottom": "2px solid",
    "borderBottomColor": COLORS['general'],
    "backgroundColor": COLORS['content-background'],
    "color": COLORS['general'],
    "padding": "12px",
    "fontWeight": "bold",
}

url_bar_and_content_div = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Store(id='lru-cache', storage_type='session', data='')
], style={"background-color": COLORS['content-background'], "height":"100vh"})

# Fetch raw data
@functools.lru_cache()
def fetch_data(hashable_tuple):
    print(hashable_tuple)
    lat_lng = list(hashable_tuple)
    lat = list(lat_lng[0])
    lng = list(lat_lng[1])
    payload = {'lat':lat, 'lng':lng}
    r = requests.post("https://data.police.uk/api/crimes-street/all-crime", params=payload)
    res = r.json()

    return res

# Get totals from raw data
def get_totals(input, json_data):
    mock_list = input
    df = pd.read_json(json_data, orient="split")
    mock_results = []
    for mock_city in mock_list:
        inst = df[df['city'] == mock_city]
        hashable_input = tuple([tuple(inst.lat), tuple(inst.lng)])
        api_data = fetch_data(hashable_input)
        df_inst = pd.DataFrame(api_data)
        mock_results.append(len(df_inst))
    result = {'mock_list': mock_list, 'mock_results': mock_results}
    df = pd.DataFrame.from_dict(result)
    return df
    
# Get statistics from raw data
def get_counts_df(city_value, json_data):
    df = pd.read_json(json_data, orient="split")
    inst = df[df['city'] == city_value]
    hashable_input = tuple([tuple(inst.lat), tuple(inst.lng)])
    api_data = fetch_data(hashable_input)
    return pd.DataFrame(api_data)
   
def get_counts_json(city_value, json_data):
    df = pd.read_json(json_data, orient="split")
    inst = df[df['city'] == city_value]
    hashable_input = tuple([tuple(inst.lat), tuple(inst.lng)])
    api_data = fetch_data(hashable_input)
    return api_data
    

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
                                html.H1('UK Crime rates'),
                                html.Div('Choose locations', id='dropdown-text')
                            ]
                        ),
                        html.Div(
                            children=[
                                dcc.Dropdown(options=[{"label": x, "value": x} for x in ['London', 'Manchester', 'Liverpool', 'Bristol']],
                                value=['London', 'Manchester', 'Liverpool'],
                                multi=True,
                                style={'background-color': COLORS['top-bar-background']},
                                id='dropdown-component-final')
                            ]
                        )
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
                                id="map-loading-1")
                    ],
                    style={"margin-bottom": 0}
                ),
                html.Div(
                    children=[
                        dcc.Tabs(
                            children=[
                                dcc.Tab(label='By Total', value='tab-1', style=tab_style, selected_style=tab_selected_style),
                                dcc.Tab(label='By Category', value='tab-2', style=tab_style, selected_style=tab_selected_style)
                            ],
                            colors={
                                'primary':COLORS['content-background'],
                                'background':COLORS['content-background']
                            },
                            value='tab-1',
                            id='tabs-graphs',
                        ),
                        html.Div(
                            children=[
                                dcc.Loading(
                                    children=[
                                        html.Div(
                                            children=[
                                                html.H6('Showing results for London'),
                                            ],
                                            style={"padding-top": "2rem"},
                                            id='results-header'
                                        ),
                                        dcc.Graph(
                                            figure={
                                                'layout':{
                                                    'height': 200,
                                                    'autosize': True,
                                                    'margin': {'b':0, 'r':0, 'l':0, 't':0}
                                                }
                                            },
                                            config={'displayModeBar':False},
                                            id="output-graph"
                                        )
                                    ],
                                    id="graph-loading-1"
                                )
                            ],
                            style={"padding-left": "3rem", "padding-right": "3rem", "padding-bottom": "3rem", "padding-top": "0rem"}
                        ),
                    ],
                ),
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
                                    )],
                                    href='/'),
                                html.H1('UK Crime rates'),
                            ]
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
                                '''
                                    ### Python
                                    * Functools lru_cache: data retrieval function calls with identical arguments are cached using lru_cache. The following data results from your interaction with the dashboard:
                                        
                                        *Cache hits: {},*
                                        *Cache misses: {},*
                                        *Cache stores: {}*
                                '''.format(fetch_data.cache_info().hits, fetch_data.cache_info().misses, fetch_data.cache_info().currsize)
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
            cache_hits, cache_misses, cache_currsize = '?', '?', '?'
        if cache != '':
            cache_hits = cache[0]
            cache_misses = cache[1]
            cache_currsize = cache[3]
            
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
                                        html.H1('UK Crime rates'),
                                    ]
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
                                        '''
                                            ### Python
                                            
                                            * Functools lru_cache: data retrieval function calls with identical arguments are cached using lru_cache. The following data results from your interaction with the dashboard:
                                                
                                                *Cache hits: {},*
                                                *Cache misses: {},*
                                                *Cache stores: {}*
                                        '''.format(cache_hits, cache_misses, cache_currsize)
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
        
        return behind_layout
    if pathname == '/':
        return dashboard_layout
    else:
        return '404'

@callback(
    Output('output-graph', 'figure', allow_duplicate=True),
    Output('results-header', 'children', allow_duplicate=True),
    Output('lru-cache', 'data'),
    Input('tabs-graphs', 'value'),
    State('dropdown-component-final', 'value'),
    State('memory-output', 'data'),
    prevent_initial_call=True
)
def tab_defaults(tab, dropdown_input, state):
    if tab == 'tab-1':
        figure = px.bar(
                    get_totals(dropdown_input, state),
                    x='mock_list',
                    y='mock_results',
                    height=200,
                    color_discrete_sequence=[COLORS['general']]*len(dropdown_input)
        )
        
        figure.update_layout(
                    autosize=True,
                    margin={'b':0,'r':0,'l':0,'t':50},
                    plot_bgcolor=COLORS['content-background'],
                    paper_bgcolor=COLORS['content-background'],
                    font={'color': COLORS['general'], 'size': 16})
        
        figure.update_xaxes(showticklabels=False, title_text="")
        figure.update_yaxes(showticklabels=False, title_text="")
        
        header = html.H4('Showing results for chosen locations...')
        
        cache = fetch_data.cache_info()
        
        return figure, header, cache
        
    if tab == 'tab-2':
        location = dropdown_input[0]
        df = get_counts_df(location, state)["category"].value_counts()
        figure = px.bar(
                    df,
                    height=200,
                    color_discrete_sequence=[COLORS['general']]*len(df)
        )
        
        figure.update_layout(
                    autosize=True,
                    margin={'b':0,'r':0,'l':0,'t':50},
                    plot_bgcolor=COLORS['content-background'],
                    paper_bgcolor=COLORS['content-background'],
                    font={'color': COLORS['top-bar-color'], 'size': 16},
                    showlegend=False)
                    
        figure.update_xaxes(showticklabels=False, title_text="")
        figure.update_yaxes(showticklabels=False, title_text="")
        
        header = html.H4('Showing results for {}'.format(location))
        
        cache = fetch_data.cache_info()
        
        return figure, header, cache
        
    
@callback(
    Output('output-graph', 'figure'),
    Output('results-header', 'children'),
    Input('dropdown-component-final', 'value'),
    Input('output-map-1', 'clickData'),
    State('tabs-graphs', 'value'),
    State('memory-output', 'data')
)
def load_tab(dropdown_input, click_data_map, tab, state):
    if tab == 'tab-1' and ctx.triggered_id == 'output-map-1':
        raise PreventUpdate
    if tab == 'tab-2' and ctx.triggered_id == 'dropdown-component-final':
        raise PreventUpdate
        
    if tab == 'tab-1' and ctx.triggered_id == 'dropdown-component-final':
        figure = px.bar(
                    get_totals(dropdown_input, state),
                    x='mock_list',
                    y='mock_results',
                    height=200,
                    color_discrete_sequence=[COLORS['general']]*len(dropdown_input))
                    
        figure.update_layout(
                    autosize=True,
                    margin={'b':0,'r':0,'l':0,'t':50},
                    plot_bgcolor=COLORS['content-background'],
                    paper_bgcolor=COLORS['content-background'],
                    font={'color': COLORS['general'], 'size': 16})
        
        figure.update_xaxes(showticklabels=False, title_text="")
        figure.update_yaxes(showticklabels=False, title_text="")

        header = html.H4('Showing results for chosen locations...')
    
        return figure, header
        
    if tab == 'tab-2' and ctx.triggered_id == 'output-map-1':
        location = click_data_map['points'][0]['hovertext']
        df = get_counts_df(location, state)["category"].value_counts()
        figure = px.bar(
                    df,
                    height=200,
                    color_discrete_sequence=[COLORS['general']]*len(df)
        )
        figure.update_layout(
                    autosize=True,
                    margin={'b':0,'r':0,'l':0,'t':50},
                    plot_bgcolor=COLORS['content-background'],
                    paper_bgcolor=COLORS['content-background'],
                    font={'color': COLORS['top-bar-color'], 'size': 16},
                    showlegend=False)
        
        figure.update_xaxes(showticklabels=False, title_text="")
        figure.update_yaxes(showticklabels=False, title_text="")

        header = html.H4('Showing results for {}'.format(location))
        
        return figure, header
        
    

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
    State('memory-output', 'data')
)
def update_map(dropdown_input, state):
    df = pd.read_json(state, orient="split")
    df = df[df['city'].isin(dropdown_input)]
    df_totals = get_totals(dropdown_input, state)
    totals = df_totals['mock_results'].tolist()
    lat = df.lat
    lng = df.lng
    location = df.city
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
                coloraxis_colorbar_x=0.94,
                coloraxis_colorbar_thickness=60
    )
                
    return figure

    
if __name__ == '__main__':
    app.run_server(debug=True)

