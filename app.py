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

if 'REDIS_URL' in os.environ:
    # Use Redis & Celery if REDIS_URL set as an env variable
    from celery import Celery
    celery_app = Celery(__name__, broker=os.environ['REDIS_URL'], backend=os.environ['REDIS_URL'])
    background_callback_manager = CeleryManager(celery_app)

else:
    # Diskcache for non-production apps when developing locally
    import diskcache
    cache = diskcache.Cache("./cache")
    background_callback_manager = DiskcacheManager(cache)
    

# Initialize the app - incorporate a Dash Bootstrap theme
external_stylesheets = [dbc.themes.CERULEAN]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# App layout
app.layout = dbc.Container([
    dbc.Row([
        html.Div('UK Crime rates'),
        html.Div('Choose locations', id='dropdown-text')
    ]),
    dbc.Row([
        dcc.Dropdown(options=[{"label": x, "value": x} for x in ['London', 'Manchester', 'Liverpool', 'Bristol']],
            value=['London', 'Manchester', 'Liverpool'],
            multi=True,
            id='dropdown-component-final')
    ]),
    dbc.Row([
        dcc.Graph(id="output-map-1", figure={})
    ]),
    
    dbc.Row([
        dcc.Loading(id="graph-loading-1", children=[dcc.Graph(id="output-graph-1", figure={})])
    ]),
    dbc.Row([
        dcc.Loading(id="graph-loading-2", children=[dcc.Graph(id="output-graph-2", figure={})])
    ]),
    dcc.Store(id='memory-output', storage_type='session', data=pd.read_csv("gb_latlon.csv", dtype=object).to_json(date_format='iso', orient='split'))
], fluid=True)


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
    Output('output-map-1', 'figure', allow_duplicate=True),
    Input('output-map-1', 'clickData'),
    State('dropdown-component-final', 'value'),
    State('memory-output', 'data'),
    prevent_initial_call=True
)
def update_map(click_data_map, dropdown_state, memory_state):
    location = click_data_map['points'][0]['hovertext']
    data = get_counts_json(location, memory_state)
    print(data[0])
    lat = []
    lng = []
    category = []
    for x in data:
        lat.append(float(x['location']['latitude']))
        lng.append(float(x['location']['longitude']))
        category.append(x['category'])
        
    lat = pd.Series(lat)
    lng = pd.Series(lng)
    category = pd.Series(category)
        
        
    figure = px.scatter_mapbox(lat=lat, lon=lng, color=category, zoom=11)
    figure.update_layout(mapbox_style="carto-positron")
    return figure

@callback(
    Output('output-map-1', 'figure', allow_duplicate=True),
    Input('output-map-1', 'relayoutData'),
    State('dropdown-component-final', 'value'),
    State('output-map-1', 'figure'),
    State('memory-output', 'data'),
    prevent_initial_call=True
)
def update_map(relayoutData, dropdown_state, figure_state, memory_state):
    if len(relayoutData) == 1:
        return {}
            
    zoom_state = figure_state['layout']['mapbox']['zoom']
    print(zoom_state)
    zoom = relayoutData['mapbox.zoom']
    print(zoom)
    if zoom < 11:
        df = pd.read_json(memory_state, orient="split")
        df = df[df['city'].isin(dropdown_state)]
        df_totals = get_totals(dropdown_state, memory_state)
        totals = df_totals['mock_results'].tolist()
        lat = df.lat
        lng = df.lng
        location = df.city
        figure = px.scatter_mapbox(lat=lat, lon=lng, color=totals, size=totals, hover_name=location, color_continuous_scale=px.colors.sequential.Bluered, zoom=zoom)
        figure.update_layout(mapbox_style="carto-positron")
            
        figure.update_layout(mapbox_center={'lat': relayoutData['mapbox.center']['lat'], 'lon': relayoutData['mapbox.center']['lon']})
        #print(figure['layout']['mapbox'])
        return figure
    else:
        raise PreventUpdate

    

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
    figure.update_layout(mapbox_style="carto-positron")
        
    return figure

    

@callback(
    Output('output-graph-1', 'figure'),
    Input('dropdown-component-final', 'value'),
    State('memory-output', 'data'),
    background=True,
    manager=background_callback_manager
)
def update_graph(dropdown_input, state):
    figure = px.bar(get_totals(dropdown_input, state), x='mock_list', y='mock_results')
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
        figure = px.bar(get_counts_df(location, state)["category"].value_counts())
        return figure

    if ctx.triggered_id == 'dropdown-component-final':
        label = value[0]
        figure = px.bar(get_counts_df(label, state)["category"].value_counts())
        return figure
        
    if ctx.triggered_id == 'output-graph-1':
        label = click_data_graph['points'][0]['label']
        figure = px.bar(get_counts_df(label, state)["category"].value_counts())
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

