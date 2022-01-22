from flask import Flask, request, render_template, jsonify
import pandas as pd
import yfinance as yf
import flask
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
import plotly.express as px
import pandas as pd
from flask import abort, Flask, redirect, url_for



# instantiate the Flask app.
app = Flask(__name__, template_folder='templates')
dash_app = dash.Dash(server=app, routes_pathname_prefix="/dash/", external_stylesheets=[dbc.themes.VAPOR])


# API Route for pulling the stock quote
@app.route("/quote")
def display_quote():
	# get a stock ticker symbol from the query string
	# default to AAPL
	symbol = request.args.get('symbol', default="AAPL")

	# pull the stock quote
	quote = yf.Ticker(symbol)

	#return the object via the HTTP Response
	return jsonify(quote.info)

# API route for pulling the stock history
@app.route("/history")
def display_history():
	#get the query string parameters
	symbol = request.args.get('symbol', default="AAPL")
	period = request.args.get('period', default="1y")
	interval = request.args.get('interval', default="1mo")

	#pull the quote
	quote = yf.Ticker(symbol)
	#use the quote to pull the historical data from Yahoo finance
	hist = quote.history(period=period, interval=interval)
	#convert the historical data to JSON
	data = hist.to_json()
	#return the JSON in the HTTP response
	return data

# This is the / route, or the main landing page route.
@app.route("/")
def home():
	# we will use Flask's render_template method to render a website template.
	return redirect(url_for('/dash/'))

	#return dash_app.layout
    # return render_template("homepage.html")

# dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"



@dash_app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return html.P("This is the content of the home page!")
    elif pathname == "/page-1":
        return html.P("This is the content of page 1. Yay!")
    elif pathname == "/page-2":
        return html.P("Oh cool, this is page 2!")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

dash_app.layout = html.Div(
    [
        dcc.Location(id="url"),
        dbc.NavbarSimple(
            children=[
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Pricing", href="/page-1", active="exact"),
                dbc.NavLink("Blog", href="/page-2", active="exact"),
				dbc.NavLink("Sign In/Up", href="/page-2", active="exact"),
            ],
            brand="OptsVision Options Analytics",
            color="primary",
            dark=True,
        ),
        dbc.Container(id="page-content", className="dbc"),
    ]
)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
# df = pd.DataFrame({
#     "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
#     "Amount": [4, 1, 2, 2, 4, 5],
#     "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
# })

# fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

# dash_app.layout = html.Div(children=[
#     html.H1(children='Vision Dashboard'),
#     html.Div(children=''' The Analytics Dashboard for Investors'''),
#     dcc.Graph(
#         id='example-graph',
#         figure=fig
#     )
# ])

# run the flask app.
if __name__ == "__main__":
	app.run(debug=True)