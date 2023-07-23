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
    "borderBottom": "1px solid #d6d6d6",
    "borderBottomColor": '#FFFFFF',
    "padding": "12px",
    "fontWeight": "bold",
    "color": COLORS['general']
}

tab_selected_style = {
    "borderBottom": "1px solid #d6d6d6",
    "borderBottomColor": COLORS['general'],
    "backgroundColor": COLORS['content-background'],
    "color": COLORS['general'],
    "padding": "12px",
    "fontWeight": "bold",
}

# App layout
app.layout = html.Div(
    children=[
        html.Div(
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
                                        figure={},
                                        config={'displayModeBar':False, 'autosizable':True},
                                        id="output-map-1")
                                ],
                                id="map-loading-1")
                    ]
                ),
                html.Div(
                    children=[
                        dcc.Tabs(
                            children=[
                                dcc.Tab(label='Tab one', value='tab-1', style=tab_style, selected_style=tab_selected_style),
                                dcc.Tab(label='Tab two', value='tab-2', style=tab_style, selected_style=tab_selected_style)
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
                                        dcc.Graph(
                                            figure={
                                                'layout':{
                                                    'autosize': True,
                                                    'margin': {'b':0, 'r':0, 'l':0, 't':0}}},
                                            config={'displayModeBar':False},
                                            id="output-graph")
                                    ],
                                    id="graph-loading-1"
                                )
                            ],
                            style={"margin": "5rem"}
                        ),
                    ],
                    style={"padding":"1rem"}
                ),
                html.Div([dcc.Store(id='memory-output', storage_type='session', data=pd.read_csv("gb_latlon.csv", dtype=object).to_json(date_format='iso', orient='split'))])
            ],
            style=CONTENT_STYLE
        ),
    ], style={"fluid":True, "background-color": "#172952"})


@callback(
    Output('output-graph', 'figure', allow_duplicate=True),
    Input('tabs-graphs', 'value'),
    State('dropdown-component-final', 'value'),
    State('memory-output', 'data'),
    prevent_initial_call=True
)
def tab_defaults(tab, dropdown_input, state):
    if tab == 'tab-1':
        figure = px.bar(get_totals(dropdown_input, state), x='mock_list', y='mock_results', height=200, title="Total count per location", color_discrete_sequence=[COLORS['general']]*len(dropdown_input))
        figure.update_layout(autosize=True, margin={'b':0,'r':0,'l':0,'t':50}, plot_bgcolor=COLORS['content-background'], paper_bgcolor=COLORS['content-background'], font={'color': COLORS['general'], 'size': 16})
        figure.update_xaxes(showticklabels=False, title_text="")
        figure.update_yaxes(showticklabels=False, title_text="")
        return figure
    if tab == 'tab-2':
        location = dropdown_input[0]
        df = get_counts_df(location, state)["category"].value_counts()
        figure = px.bar(df, height=200, title="Category counts", color_discrete_sequence=[COLORS['general']]*len(df))
        figure.update_layout(autosize=True, margin={'b':0,'r':0,'l':0,'t':50}, plot_bgcolor=COLORS['content-background'], paper_bgcolor=COLORS['content-background'], font={'color': COLORS['top-bar-color'], 'size': 16}, showlegend=False)
        figure.update_xaxes(showticklabels=False, title_text="")
        figure.update_yaxes(showticklabels=False, title_text="")
        return figure
        
    
@callback(
    Output('output-graph', 'figure'),
    Input('dropdown-component-final', 'value'),
    Input('output-map-1', 'clickData'),
    State('tabs-graphs', 'value'),
    State('memory-output', 'data')
)
def load_tab(dropdown_input, click_data_map, tab, state):
    if tab == 'tab-1' and ctx.triggered_id == 'dropdown-component-final':
        figure = px.bar(get_totals(dropdown_input, state), x='mock_list', y='mock_results', height=200, title="Total count per location", color_discrete_sequence=[COLORS['general']]*len(dropdown_input))
        figure.update_layout(autosize=True, margin={'b':0,'r':0,'l':0,'t':50}, plot_bgcolor=COLORS['content-background'], paper_bgcolor=COLORS['content-background'], font={'color': COLORS['general'], 'size': 16})
        figure.update_xaxes(showticklabels=False, title_text="")
        figure.update_yaxes(showticklabels=False, title_text="")
        print(1)
        return figure
    if tab == 'tab-1' and ctx.triggered_id == 'output-map-1':
        print(2)
        raise PreventUpdate
        
    if tab == 'tab-2' and ctx.triggered_id == 'output-map-1':
        location = click_data_map['points'][0]['hovertext']
        print(location)
        df = get_counts_df(location, state)["category"].value_counts()
        figure = px.bar(df, height=200, title="Category counts", color_discrete_sequence=[COLORS['general']]*len(df))
        figure.update_layout(autosize=True, margin={'b':0,'r':0,'l':0,'t':50}, plot_bgcolor=COLORS['content-background'], paper_bgcolor=COLORS['content-background'], font={'color': COLORS['top-bar-color'], 'size': 16}, showlegend=False)
        figure.update_xaxes(showticklabels=False, title_text="")
        figure.update_yaxes(showticklabels=False, title_text="")
        print(3)
        print(figure)
        return figure
    if tab == 'tab-2' and ctx.triggered_id == 'dropdown-component-final':
        print(4)
        raise PreventUpdate
    

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
    figure = px.scatter_mapbox(lat=lat, lon=lng, color=totals, size=totals, hover_name=location, color_continuous_scale=px.colors.sequential.Blues, zoom=5, height=300)
    figure.update_layout(mapbox_style="carto-positron", autosize=True, margin={'b':0,'r':0,'l':0,'t':0}, paper_bgcolor=COLORS['content-background'], coloraxis_colorbar_showticklabels=False, coloraxis_colorbar_title="")
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

