from pydoc import classname
from tokenize import tabsize
from flask import Flask, request, render_template, jsonify
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, dcc
from dash_bootstrap_components._components.Container import Container
import plotly.graph_objs as go
import numpy as np

# instantiate the Flask app.
app = Flask(__name__, template_folder='templates')
dash_app = dash.Dash(server=app, routes_pathname_prefix="/", external_stylesheets=[dbc.themes.QUARTZ])

PLOTLY_LOGO = "static/logo.png"

header_bar = dbc.Row(
    [
        dbc.Col(
            dbc.Button("Home", color="primary", className="btn btn-primare", active=True),
            width="auto",
        ),
        dbc.Col(
            dbc.Button("Pricing", color="primary", className="btn btn-secondary"),
            width="auto",
        ),
        dbc.Col(
            dbc.Button("Blog", color="primary", className="btn btn-secondary"),
            width="auto",
        ),
        dbc.Col(
            dbc.Button("Sign In", color="primary", className="btn btn-secondary"),
            width="auto",
        ),
        dbc.Col(
            dbc.Button("Contact", color="primary", className="btn btn-secondary"),
            width="auto",
        ),
    ],
    align="center",
)

# search_bar = dbc.Row(
#     [
#         dbc.Col(dbc.Input(type="search", placeholder="Search")),
#         dbc.Col(
#             dbc.Button(
#                 "Search", color="primary", className="ms-2", n_clicks=0
#             ),
#             width="auto",
#         ),
#     ],
#     className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
#     align="center",
# )

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=PLOTLY_LOGO, height="50px")),
                        dbc.Col(dbc.NavbarBrand("Options Analytics", className="ms-2")),
                    ],
                    align="center",
                ),
                href="https://plotly.com",
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                header_bar,
                id="navbar-collapse",
                is_open=False,
                navbar=True,
            ),
        ]
    ),
    color="dark",
    dark=True,
    class_name="dash-bootstrap",
)

tabs = dbc.Container(
    [
        dcc.Store(id="store"),
        html.Div(children=[("Enter Stock/Index/ETF Ticker:" ),
        dbc.Input(id="ticker_input", placeholder="Enter Stock/Index/ETF Ticker", size="50")
        ,dbc.Button(
            "Search",
            color="secondary",
            id="button",
            className="mb-3",)]),
        # dbc.Tabs(
        #     [
        #         dbc.Tab(label="Scatter", tab_id="scatter"),
        #         dbc.Tab(label="Histograms", tab_id="histogram"),
        #     ],
        #     id="tabs",
        #     active_tab="scatter",
        # ),
        # html.Div(id="tab-content", className="p-4"),
    ]
)

dash_app.layout = html.Div([navbar, tabs], className="dash-bootstrap")


@dash_app.callback(Output("store", "data"), [Input("button", "n_clicks")])
def generate_graphs(n):
    """
    This callback generates three simple graphs from random data.
    """
    print( n)

    if not n:
        # generate empty graphs when app loads
        return {k: go.Figure(data=[]) for k in ["scatter", "hist_1", "hist_2"]}

    # simulate expensive graph generation process

    # generate 100 multivariate normal samples
    data = np.random.multivariate_normal([0, 0], [[1, 0.5], [0.5, 1]], 100)

    scatter = go.Figure(
        data=[go.Scatter(x=data[:, 0], y=data[:, 1], mode="markers")]
    )
    hist_1 = go.Figure(data=[go.Histogram(x=data[:, 0])])
    hist_2 = go.Figure(data=[go.Histogram(x=data[:, 1])])

    # save figures in a dictionary for sending to the dcc.Store
    return {"scatter": scatter, "hist_1": hist_1, "hist_2": hist_2}

# add callback for toggling the collapse on small screens
@dash_app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@dash_app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab"), Input("store", "data")],
)
def render_tab_content(active_tab, data):
    """
    This callback takes the 'active_tab' property as input, as well as the
    stored graphs, and renders the tab content depending on what the value of
    'active_tab' is.
    """
    print(active_tab)
    if active_tab and data is not None:
        if active_tab == "scatter":
            return dcc.Graph(figure=data["scatter"])
        elif active_tab == "histogram":
            return dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=data["hist_1"]), width=6),
                    dbc.Col(dcc.Graph(figure=data["hist_2"]), width=6),
                ]
            )
    return "No tab selected"
# # API Route for pulling the stock quote
# @app.route("/quote")
# def display_quote():
# 	# get a stock ticker symbol from the query string
# 	# default to AAPL
# 	symbol = request.args.get('symbol', default="AAPL")

# 	# pull the stock quote
# 	quote = yf.Ticker(symbol)

# 	#return the object via the HTTP Response
# 	return jsonify(quote.info)

# # API route for pulling the stock history
# @app.route("/history")
# def display_history():
# 	#get the query string parameters
# 	symbol = request.args.get('symbol', default="AAPL")
# 	period = request.args.get('period', default="1y")
# 	interval = request.args.get('interval', default="1mo")

# 	#pull the quote
# 	quote = yf.Ticker(symbol)
# 	#use the quote to pull the historical data from Yahoo finance
# 	hist = quote.history(period=period, interval=interval)
# 	#convert the historical data to JSON
# 	data = hist.to_json()
# 	#return the JSON in the HTTP response
# 	return data

# # This is the / route, or the main landing page route.
# @app.route("/")
# def home():
# 	# we will use Flask's render_template method to render a website template.
# 	return redirect(url_for('/dash/'))

# 	#return dash_app.layout
#     # return render_template("homepage.html")

# # dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"



# @dash_app.callback(Output("page-content", "children"), [Input("url", "pathname")])
# def render_page_content(pathname):
#     if pathname == "/":
#         return html.P("This is the content of the home page!")
#     elif pathname == "/page-1":
#         return html.P("This is the content of page 1. Yay!")
#     elif pathname == "/page-2":
#         return html.P("Oh cool, this is page 2!")
#     # If the user tries to reach a different page, return a 404 message
#     return dbc.Jumbotron(
#         [
#             html.H1("404: Not found", className="text-danger"),
#             html.Hr(),
#             html.P(f"The pathname {pathname} was not recognised..."),
#         ]
#     )

# dash_app.layout = html.Div(
#     [
#         dcc.Location(id="url"),
#         dbc.NavbarSimple(
#             children=[
#                 dbc.NavLink("Home", href="/", active="exact"),
#                 dbc.NavLink("Pricing", href="/page-1", active="exact"),
#                 dbc.NavLink("Blog", href="/page-2", active="exact"),
# 				dbc.NavLink("Sign In/Up", href="/page-2", active="exact"),
#             ],
#             brand="OptsVision Options Analytics",
#             color="primary",
#             dark=True,
#         ),
#         dbc.Container(id="page-content", className="dbc"),
#     ]
# )

# # assume you have a "long-form" data frame
# # see https://plotly.com/python/px-arguments/ for more options
# # df = pd.DataFrame({
# #     "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
# #     "Amount": [4, 1, 2, 2, 4, 5],
# #     "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
# # })

# # fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

# # dash_app.layout = html.Div(children=[
# #     html.H1(children='Vision Dashboard'),
# #     html.Div(children=''' The Analytics Dashboard for Investors'''),
# #     dcc.Graph(
# #         id='example-graph',
# #         figure=fig
# #     )
# # ])

# run the flask app.
if __name__ == "__main__":
	app.run(debug=True)