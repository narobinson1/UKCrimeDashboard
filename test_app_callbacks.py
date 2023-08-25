from contextvars import copy_context
from dash._callback_context import context_value
from dash._utils import AttributeDict

import pandas as pd
import numpy as np

# Callback functions imported
from app import update_dropdown

def test_update_dropdown_callback():
	json_data = pd.read_csv("gb_latlon.csv", dtype=object).to_json(date_format='iso', orient='split')
	output = update_dropdown(json_data)
	locations = ['London', 'Birmingham', 'Manchester', 'Liverpool', 'Portsmouth', 'Southampton', 'Nottingham', 'Bristol', 'Leicester', 'Coventry']
	assert_options = [{"label": x, "value": x} for x in locations]
	assert_values = locations
	assert_output = (assert_options, assert_values)
	assert output == assert_output



