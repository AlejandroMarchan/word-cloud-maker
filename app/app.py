
import logging
import sys
import plotly.express as px

# Init logging
logging.basicConfig(
    format='[%(asctime)s] [%(name)s:%(lineno)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %z',
    stream=sys.stdout,
    level=10
)

log = logging.getLogger("PIL")
log.setLevel(logging.INFO)

log = logging.getLogger("urllib3.connectionpool")
log.setLevel(logging.INFO)

log = logging.getLogger("app")
log.setLevel(logging.INFO)

from dash_extensions.enrich import DashProxy, MultiplexerTransform, LogTransform, DashLogger
from dash_extensions.enrich import Input, Output, State, html, dcc, ALL, MATCH
import dash_bootstrap_components as dbc
from dash_extensions import Lottie
import dash

app = DashProxy(
    __name__, 
    title="Collage maker", 
    transforms=[
        MultiplexerTransform(),  # makes it possible to target an output multiple times in callbacks
        LogTransform()  # makes it possible to write log messages to a Dash component
    ],
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
    ],
)
app.config.suppress_callback_exceptions = True
server = app.server

app.layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.H1(
                        "Collage Maker",
                        id='title'
                    ),
                    width="auto"
                ),
                dbc.Col(
                    dbc.Button(
                        "Change title",
                        id='my-btn'
                    ),
                    width="auto"
                ),
            ],
            justify="center",
            align="center",
            style={
                'margin-top': '30px',
            }
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Loading(
                        dcc.Graph(
                            id="my-fig",
                            style={
                                'height': '60vh',
                                'display': 'none'
                            }
                        ),
                        style={
                            'height': '60vh',
                        }
                    ),
                    width="auto"
                )
            ],
            justify="center",
            align="center",
            style={
                'margin-top': '30px',
            }
        )
    ],
    style={
        'width': '90%',
        'margin': 'auto',
        'height': '100vh',
        'display': 'flex',
        'flex-direction': 'column' 
    }
)

@app.callback(
    Output('my-fig', 'figure'),
    Output('my-fig', 'style'),
    Input('my-btn', 'n_clicks'),
    State('title', 'children'),
    prevent_initial_call=True
)
def set_copyright(n_clicks, prev_title):
    df = px.data.iris()  # iris is a pandas DataFrame
    fig = px.scatter(df, x="sepal_width", y="sepal_length")
    return fig, {'height': '60vh',}

@app.callback(
    Output('title', 'children'),
    Input('my-fig', 'clickData'),
    prevent_initial_call=True
)
def set_copyright(data):
    width, length = data['points'][0]['x'], data['points'][0]['y']
    return f'Width: {width} - Length: {length}'

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8080, use_reloader=False)
