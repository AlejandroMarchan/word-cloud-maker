
import logging
from datetime import date
import sys
from turtle import width
import plotly.express as px
import numpy as np
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
import unidecode
import re
import time
import base64
import math

IMAGES_PATH = 'app/assets/images'
TEXTS_PATH = 'app/assets/texts'
STOPWORDS_PATH = 'app/assets/stopwords'

REPLACE_SYMBOLS = ['(', ')', '.', '"', "'", ',', ':', ';', '?', '¿', '¡', '!', 'º', 'ª', '%', '/', "\\", '*', '+', '-',
                 '=', '#', '€', '-', '_', '\n', '&', '@', '[', ']', '>', '<']
REGULAR_EXPRESSIONS = ['[0-9]+', '\\b[a-z]\\b', ' {2,}']
EXTRA_STOPWORDS = ['https', 'co', 'amp', 'http', 'gt', 'yeah', 'hey', 'uh', 'gon', 'true']

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
    title="Word cloud generator", 
    transforms=[
        MultiplexerTransform(),  # makes it possible to target an output multiple times in callbacks
        LogTransform()  # makes it possible to write log messages to a Dash component
    ],
    external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://use.fontawesome.com/releases/v6.2.0/css/all.css'],
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
                    [
                        html.Img(src=app.get_asset_url("wordcloud-icon.png"), width='40px'),
                        html.H3(
                            "Word Cloud Generator",
                            id='title'
                        )
                    ],
                    width="auto"
                )
            ],
            justify="center",
            align="center",
            style={
                'margin-top': '30px',
                'margin-bottom': '20px',
            }
        ),
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                # dbc.Row(
                                #     [
                                #         dbc.Col(
                                #             html.H3(
                                #                 "Input text", 
                                #                 className="card-title text-center"
                                #             ),
                                #             width="12"
                                #         ),
                                #     ]
                                # ),
                                # html.Hr(),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dcc.Upload(
                                                    id='upload-image',
                                                    className='upload',
                                                    children=html.Div(
                                                        [
                                                            'Drag and Drop or ',
                                                            html.A(
                                                                [
                                                                    'Select the reference image',
                                                                    html.I(className="fas fa-image ms-2"),
                                                                ], 
                                                                style={"cursor": "pointer", 'color': 'var(--bs-primary)'}
                                                            )
                                                        ],
                                                    ),
                                                    accept="image/*",
                                                    # Allow multiple files to be uploaded
                                                    multiple=False
                                                )
                                            ],
                                            width="4"
                                        ),
                                        dbc.Col(
                                            [
                                                dcc.Upload(
                                                    id='upload-text',
                                                    className='upload',
                                                    children=html.Div(
                                                        [
                                                            'Drag and Drop or ',
                                                            html.A(
                                                                [
                                                                    'Select the reference text',
                                                                    html.I(className="fas fa-file-lines ms-2"),
                                                                ], 
                                                                style={"cursor": "pointer", 'color': 'var(--bs-primary)'}
                                                            )
                                                        ],
                                                    ),
                                                    # Allow multiple files to be uploaded
                                                    multiple=False
                                                ),
                                                dbc.Textarea(
                                                    placeholder="Input text",
                                                    style={
                                                        'height': '115px',
                                                        'display': 'none'
                                                    }
                                                )
                                            ],
                                            width="4"
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Button(
                                                    [
                                                        "Generate wordcloud",
                                                        html.I(className="fa-solid fa-arrow-right ms-2")
                                                    ],
                                                    id='generate-wordcloud-btn',
                                                    color="success"
                                                ),
                                                dbc.Button(
                                                    [
                                                        html.I(className="fas fa-download me-2"),
                                                        "Download result",
                                                    ],
                                                    id='download-wordcloud-btn',
                                                    disabled=True,
                                                    color="primary",
                                                    style={
                                                        'margin-top': '10px'
                                                    }
                                                ), 
                                                dcc.Download(id="download-wordcloud")
                                            ], 
                                            width='auto',
                                            align='center',
                                            style={
                                                'display': 'grid'
                                            }
                                        )
                                    ],
                                    justify='center',
                                    align='center'
                                ),
                                # dbc.Row(
                                #     [
                                        
                                #     ],
                                #     style={
                                #         'margin-top': '20px'
                                #     }
                                # )
                            ]
                        )
                    ]
                ),
                width="12"
            ),
        ),
        dbc.Row(
            [
                # dbc.Col(
                #     [
                #         html.H4(
                #             [
                #                 "No wordclouds generated yet"
                #             ], 
                #             className="text-center",
                #             style={
                #                 'margin-top': '25px',
                #                 'margin-bottom': '20px'
                #             }
                #         ),
                #         Lottie(
                #             options=dict(loop=True, autoplay=True), width="40%",
                #             url="https://assets5.lottiefiles.com/private_files/lf30_bn5winlb.json",
                #             isClickToPauseDisabled=True,
                #             style={
                #                 'margin-bottom': '3%',
                #                 'cursor': 'default'
                #             }
                #         ),
                #     ],
                #     width='12'
                # ),
                dbc.Col(
                    html.Img(src=app.get_asset_url("images/el_quijote.png"), id="reference-img"),
                    id='reference-image-col',
                    width='4'
                ),
                dcc.Loading(
                    [
                        html.Img(src=app.get_asset_url("images/el_quijote_wordcloud.png"), id="wordcloud-img")
                    ],
                    id='wordcloud-image-col',
                    parent_className='col-4',
                    parent_style={
                        'padding': '0'
                    }
                )
            ],
            className='images-container',
            style={
                'margin-top': '20px',
            },
            align='center'
        ),
        html.Footer(
            html.H6("© Copyright 2012 - Alejandro Marchán", id="copyright", className="text-center"),
            id='footer',
            style={
                'margin-top': 'auto',
                'height': '50px'
            }
        ),
        html.P(
            id='placeholder',
            style={
                'display': 'none'
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
    Output('copyright', 'children'),
    Input('copyright', 'children'),
)
def set_copyright(dummy):
    return [
        f"© Copyright {date.today().year} - Alejandro Marchán", 
        html.A(
            html.Img(
                src='https://avatars.githubusercontent.com/u/47084443?s=40&v=4', 
                height='38px', 
                id="github-avatar",
                style={
                    'display': 'inline',
                    'margin-left': '15px',
                    'margin-bottom': '6px'
                }
            ),
            href='https://github.com/AlejandroMarchan'
        )
    ]

def clean_text(text, stopwords_language='es'):

    # Remove accents
    log.info('Removing accents')
    tic = time.process_time()
    cleaned_text = unidecode.unidecode(text).lower()
    tac = time.process_time()
    log.info(f'Took {tac - tic} seconds')
    
    # Replace all the symbols
    log.info('Removing symbols')
    tic = time.process_time()
    for word in REPLACE_SYMBOLS:
        cleaned_text = cleaned_text.replace(word, ' ')
    tac = time.process_time()
    log.info(f'Took {tac - tic} seconds')
    
    # Remove stopwords
    log.info('Removing stopwords')
    tic = time.process_time()
    stop_words = []
    with open(f'{STOPWORDS_PATH}/stopwords-{stopwords_language}.txt', 'r') as f:
        stop_words = f.readlines()
        stop_words += EXTRA_STOPWORDS
    # To stop removing stopwords
    stop_words = []
    for word in stop_words:
        word = word.rstrip('\n')
        regex = '\\b' + word + '\\b'
        p = re.compile(regex)
        cleaned_text, n_subs = p.subn(' ', cleaned_text)
    tac = time.process_time()
    log.info(f'Took {tac - tic} seconds')

    # Remove numbers, single letters and multiple spaces
    log.info('Removing numbers, single letters and multiple spaces')
    tic = time.process_time()
    for regex in REGULAR_EXPRESSIONS:
        p = re.compile(regex)
        cleaned_text, n_subs = p.subn(' ', cleaned_text)
    tac = time.process_time()
    log.info(f'Took {tac - tic} seconds')

    return cleaned_text

def generate_worcloud_image(text, mask, n_words=10000):
    wordcloud = WordCloud(collocations=False, background_color="white", mode="RGBA", max_words=n_words, mask=mask).generate(text)
    image_colors = ImageColorGenerator(mask)
    wordcloud = wordcloud.recolor(color_func=image_colors)
    return wordcloud.to_image()

@app.callback(
    Output("wordcloud-image-col", "children"), 
    Output('download-wordcloud-btn', 'disabled'),
    Input("generate-wordcloud-btn", "n_clicks"),
    prevent_initial_call=True,
)
def generate_worcloud(n_clicks):
    log.info('Generating the wordcloud')
    tic = time.process_time()
    with open(f'{TEXTS_PATH}/el_quijote.txt', 'r') as f:
        text = f.read()
    cleaned_text = clean_text(text)
    mask_image = Image.open(f'{IMAGES_PATH}/el_quijote.png').convert('RGB')
    mask_width = mask_image.size[0]
    mask_height = mask_image.size[1]
    MAX_PIXELS = 1000 * 1000
    ratio = math.sqrt(MAX_PIXELS / (mask_width * mask_height))
    final_width = math.ceil(mask_width * ratio)
    final_height = math.ceil(mask_height * ratio)
    mask = np.array(mask_image.resize((final_width, final_height)))
    MAX_PIXELS = 1600 * 1600
    ratio = math.sqrt(MAX_PIXELS / (mask_width * mask_height))
    final_width = math.ceil(mask_width * ratio)
    final_height = math.ceil(mask_height * ratio)
    image = generate_worcloud_image(cleaned_text, mask).resize((final_width, final_height))
    tac = time.process_time()
    log.info(f'Wordcloud generated in {tac - tic} seconds')

    return [html.Img(src=image, id="wordcloud-img")], False

@app.callback(
    Output("download-wordcloud", "data"), 
    Input('download-wordcloud-btn', 'n_clicks'),
    State('wordcloud-img', 'src'),
    prevent_initial_call=True,
)
def download_wordcloud(n_clicks, image_base64):
    return dcc.send_bytes(base64.b64decode(image_base64.split(',')[1]), "wordcloud.png")

@app.callback(
    Output("reference-image-col", "children"), 
    Input('upload-image', 'contents'),
    # Input('test-reference-btn', 'n_clicks'),
    prevent_initial_call=True,
)
def upload_reference_img(contents):
    if dash.callback_context.triggered[0]['prop_id'] == 'test-reference-btn.n_clicks':
        contents = f"data:image/jpg;base64,{base64.b64encode(open('app/assets/reference.JPEG', 'rb').read()).decode('utf-8')}"

    return html.Img(src=contents, id="reference-img"),

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8080, use_reloader=False)
