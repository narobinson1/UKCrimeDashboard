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


# Initialize the app - incorporate a Dash Bootstrap theme
external_stylesheets = [dbc.themes.CERULEAN]
app = Dash(__name__, external_stylesheets=external_stylesheets)

COLORS = {
    "top-bar-background": "#2a2630",
    "top-bar-color": "#406cc9",
    "content-background": "#2a2630"
}

TOPBAR_STYLE = {
    "top": 0,
    "left": 0,
    "right": 0,
    "width": "100%",
    "height": "10rem",
    "padding": "2rem 1rem",
    "background-color": COLORS['top-bar-background'],
    "color": COLORS['top-bar-color']
}

CONTENT_STYLE = {
    "background-color": COLORS['content-background']
}


# App layout
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H1('UK Crime rates'),
                        html.Div('Choose locations', id='dropdown-text')
                    ]
                ),
                html.Div(
                    children=[
                        dcc.Dropdown(options=[{"label": x, "value": x} for x in ['London', 'Manchester', 'Liverpool', 'Bristol']],
                        value=['London', 'Manchester', 'Liverpool'],
                        multi=True,
                        id='dropdown-component-final')
                    ]
                )
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
                                        figure={},
                                        config={'displayModeBar':False, 'autosizable':True},
                                        id="output-map-1")
                                ],
                                id="map-loading-1")
                    ]
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
                                                    'autosize': True,
                                                    'margin': {'b':0, 'r':0, 'l':0, 't':0}}},
                                            config={'displayModeBar':False},
                                            id="output-graph-1")
                                    ],
                                    id="graph-loading-1"
                                )
                            ],
                            style={"margin": "5rem", "border": "solid"}
                        ),
                        html.Div(
                            children=[
                                dcc.Loading(
                                    children=[
                                        dcc.Graph(
                                            figure={},
                                            config={'displayModeBar':False},
                                            id="output-graph-2"
                                        )
                                    ],
                                    id="graph-loading-2")
                            ],
                            style={"margin": "5rem", "border": "solid"}
                        ),
                    ]
                ),
                html.Div([dcc.Store(id='memory-output', storage_type='session', data=pd.read_csv("gb_latlon.csv", dtype=object).to_json(date_format='iso', orient='split'))])
            ],
            style=CONTENT_STYLE
        ),
    ], style={"fluid":True})


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
    print(lat)
    location = df.city
    figure = px.scatter_mapbox(lat=lat, lon=lng, color=totals, size=totals, hover_name=location, color_continuous_scale=px.colors.sequential.Bluered, zoom=5)
    figure.update_layout(mapbox_style="carto-positron", autosize=True, margin={'b':0,'r':0,'l':0,'t':0})
    
    
    return figure



@callback(
    Output('output-graph-1', 'figure'),
    Input('dropdown-component-final', 'value'),
    State('memory-output', 'data')
)
def update_graph(dropdown_input, state):
    figure = px.bar(get_totals(dropdown_input, state), x='mock_list', y='mock_results', height=200)
    print(figure['layout'])
    return figure

    
    
@callback(
    Output('output-graph-2', 'figure'),
    Input('output-graph-1', 'clickData'),
    Input('output-map-1', 'clickData'),
    Input('dropdown-component-final', 'value'),
    State('memory-output', 'data')
)
def display_click(click_data_graph, click_data_map, value, state):
    if ctx.triggered_id == 'output-map-1':
        location = click_data_map['points'][0]['hovertext']
        figure = px.bar(get_counts_df(location, state)["category"].value_counts(), height=200)
        return figure

    if ctx.triggered_id == 'dropdown-component-final':
        label = value[0]
        figure = px.bar(get_counts_df(label, state)["category"].value_counts(), height=200)
        return figure
        
    if ctx.triggered_id == 'output-graph-1':
        label = click_data_graph['points'][0]['label']
        figure = px.bar(get_counts_df(label, state)["category"].value_counts(), height=200)
        return figure



# Fetch raw data
def fetch_data(lat=51.5072, lng=-0.1275):
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
        api_data = fetch_data(inst.lat, inst.lng)
        df_inst = pd.DataFrame(api_data)
        mock_results.append(len(df_inst))
    result = {'mock_list': mock_list, 'mock_results': mock_results}
    df = pd.DataFrame.from_dict(result)
    return df
    
# Get statistics from raw data
def get_counts_df(city_value, json_data):
    df = pd.read_json(json_data, orient="split")
    inst = df[df['city'] == city_value]
    api_data = fetch_data(inst.lat, inst.lng)
    return pd.DataFrame(api_data)
   
def get_counts_json(city_value, json_data):
    df = pd.read_json(json_data, orient="split")
    inst = df[df['city'] == city_value]
    api_data = fetch_data(inst.lat, inst.lng)
    return api_data
    
if __name__ == '__main__':
    app.run_server(debug=True)

