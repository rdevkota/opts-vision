from cProfile import label
from ctypes import alignment
from logging import PlaceHolder
from flask import Flask, request, render_template, jsonify, abort, Flask, redirect, url_for
from numpy import ma
import pandas as pd
import yfinance as yf
import flask
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import talib


# instantiate the Flask app.
app = Flask(__name__, template_folder='templates')
dash_app = dash.Dash(server=app, routes_pathname_prefix="/dash/", external_stylesheets=[dbc.themes.MINTY])
dash_app.layout = html.Div(
    [
        dcc.Location(id="url"),
        dbc.NavbarSimple(
            children=[
                dbc.NavLink("Home", href="/", active=True),
                dbc.NavLink("Pricing", href="/page-1", active="exact"),
                dbc.NavLink("Blog", href="/page-2", active="exact"),
				dbc.NavLink("Sign In/Up", href="/page-2", active="exact"),
            ],
            brand="OptsVision Analytics",
            color="primary",
            dark=True,
        ),
        dbc.Container(id="page-content", className="dbc"),
    ]
)

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

@dash_app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return html.P("This is the content of the home page!")
    elif pathname == "/page-1":
        return html.P("This is the content of page 1. Yay!")
    elif pathname == "/page-2":
        return html.P("Oh cool, this is page 2!")
    return  html.Div(
    [        
        html.Br(),
        html.Br(),
        html.Br(),
        html.P('Search For Stock/ETF/Index Ticker Symbol ...'),
        dbc.InputGroup(
            [   
                dbc.Input(id="input-group-button-input", placeholder="Enter Stock/ETF/Index Ticker Symbol", type="text",  size="lg", value=''),
                dbc.Button("Search", id="input-group-button", color="secondary", n_clicks=0),
            ]
        ),
        html.Br(),
        html.Div(id='analytics-space')
    ])



@dash_app.callback(
    Output(component_id='analytics-space', component_property='children'),
    Input(component_id='input-group-button-input', component_property='value')
)

def get_stock_data(input_value):
        print(input_value)
        if len(input_value) > 1 :
            return html.Div(show_stock_data(input_value))
        return 'Enter Stock/ETF/Index Ticker Symbol ....'

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

#funtion to get the historic data
def get_historic_data(ticker):
  return yf.download(ticker, period="max")

def get_MACD(df):
  df['EMA12'] = df.Close.ewm(span=12).mean()
  df['EMA26'] = df.Close.ewm(span=26).mean()
  df['MACD'] = df.EMA12 - df.EMA26
  df['signal'] = df.MACD.ewm(span=9).mean()
  return df
  
def show_stock_data(ticker):
    df = get_historic_data(ticker)
    df.reset_index(inplace=True)

    line_colors = ["#7CEA9C", '#50B2C0', "rgb(114, 78, 145)", "hsv(348, 66%, 90%)", "hsl(45, 93%, 58%)"]

    fig = px.bar(df, "Date", "Close", barmode="relative")
    fig.update_layout({'plot_bgcolor': 'rgba(255, 255, 255, 255)',})
    fig.update_traces(marker_color='blue')
    hist_chart = dcc.Graph(id='hist-graph', figure=fig)

    macd_data = get_MACD(df)
    macd_df = macd_data[(macd_data['Date'] >= '2021-10-01')]

    fig1 = px.line(macd_df, x="Date", y=[macd_df['Date'], macd_df['Close'], macd_df['EMA12'], macd_df['EMA26']],
              hover_data={"Date": "|%B %d, %Y"},
              title='MACD Crossover')
    fig1.update_xaxes(
        dtick="M1",
        tickformat="%b\n%Y")

    macd_chart = dcc.Graph(id="macd_chart", figure=fig1)

    #rsi = talib.RSI(data["Close"])

    dash_app.layout = html.Div(children=[
        html.H1(children='Analytics For Ticker: ' + ticker),
        html.Div(children='''Historic Data'''),
        hist_chart,
        macd_chart,
    ])
    return dash_app.layout 

# run the flask app.
if __name__ == "__main__":
	app.run(debug=True)