import dash
from dash import html

from ..app import app

def test_001_app_heading_text(dash_duo):
    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal('#app-heading', "UK Crime rates", timeout=1)
    assert dash_duo.find_element('#app-heading').text == "UK Crime rates"
    assert dash_duo.get_logs() == [], "browser console should contain no error"
    
#def test_002_app_sub_heading_text(dash_duo):
#    dash_duo.start_server(app)
#    dash_duo.wait_for_text_to_equal('#app-sub-heading', "| Python, Dash, MySQL", timeout=1)
#    assert dash_duo.find_element('#app-sub-heading').text == "| Python, Dash, MySQL"
#    assert dash_duo.get_logs() == [], "browser console should contain no error"
    
#def test_003_app_sub_heading_text(dash_duo):
#    dash_duo.start_server(app)
#    dash_duo.wait_for_text_to_equal('#app-about-header', "ABOUT", timeout=1)
#    assert dash_duo.find_element('#app-about-header').text == "ABOUT"
#    assert dash_duo.get_logs() == [], "browser console should contain no error"

#def test_004_app_sub_heading_text(dash_duo):
#    dash_duo.start_server(app)
#    dash_duo.wait_for_text_to_equal('#app-guide-header', "GUIDE", timeout=1)
#    assert dash_duo.find_element('#app-guide-header').text == "GUIDE"
#    assert dash_duo.get_logs() == [], "browser console should contain no error"

#def test_005_app_sub_heading_text(dash_duo):
#    dash_duo.start_server(app)
#    dash_duo.wait_for_text_to_equal('#app-notes-header', "NOTES", timeout=1)
#    assert dash_duo.find_element('#app-notes-header').text == "NOTES"
#    assert dash_duo.get_logs() == [], "browser console should contain no error"


