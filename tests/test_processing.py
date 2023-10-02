from contextvars import copy_context
from dash._callback_context import context_value
from dash._utils import AttributeDict

import pandas as pd
import numpy as np

# Callback functions imported
from ..app import date_range, get_count_graph, get_category, get_count_map

def test_date_range():
    output = date_range(2020, 1, 2023, 12)
    assert output == ['2020-01', '2020-02', '2020-03', '2020-04', '2020-05', '2020-06', '2020-07', '2020-08', '2020-09', '2020-10', '2020-11', '2020-12', '2021-01', '2021-02', '2021-03', '2021-04', '2021-05', '2021-06', '2021-07', '2021-08', '2021-09', '2021-10', '2021-11', '2021-12', '2022-01', '2022-02', '2022-03', '2022-04', '2022-05', '2022-06', '2022-07', '2022-08', '2022-09', '2022-10', '2022-11', '2022-12', '2023-01', '2023-02', '2023-03', '2023-04', '2023-05', '2023-06', '2023-07', '2023-08', '2023-09', '2023-10', '2023-11', '2023-12']
    
def test_get_count_graph():
    output = get_count_graph(['London', 'Birmingham', 'Manchester', 'Liverpool', 'Portsmouth', 'Southampton', 'Nottingham', 'Bristol', 'Leicester', 'Coventry'])
    l = ['London', 'Birmingham', 'Manchester', 'Liverpool', 'Portsmouth', 'Southampton', 'Nottingham', 'Bristol', 'Leicester', 'Coventry']
    t = [6729, 1952, 92, 1253, 1190, 978, 1534, 1442, 1417, 1024]
    f = [0.059, 0.066, 0.003, 0.145, 0.139, 0.114, 0.199, 0.254, 0.278, 0.282]
    df = pd.DataFrame({'location': l, 'total': t, 'fractional': f})
    assert (output == df).all
    
def test_get_category():
    output = get_category('London')
    c = ['Other theft', 'Theft from the person', 'Violent crime', 'Anti social behaviour', 'Shoplifting', 'Robbery', 'Vehicle crime', 'Public order', 'Drugs', 'Criminal damage arson', 'Burglary', 'Bicycle theft', 'Possession of weapons', 'Other crime']
    ct = [30.0, 26.0, 9.4, 9.3, 5.6, 4.6, 3.2, 2.8, 2.3, 1.6, 1.4, 1.3, 0.4, 0.2]
    print(output)
    df = pd.DataFrame({'category': c, 'ratio': ct})
    print(df)
    assert (output == df).all

