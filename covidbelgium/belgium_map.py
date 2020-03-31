import dash
import dash_html_components as html

from covidbelgium import app

dash = dash.Dash(
    __name__,
    server=app,
    routes_pathname_prefix='/belgium-map/'
)
dash.layout = html.Div("My Dash app")
