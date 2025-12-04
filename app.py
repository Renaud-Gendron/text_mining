print("--- Start Running Python code ---")

import base64
import datetime
import io
import openpyxl

import dash
from dash.dependencies import Input, Output, State
#import dash_core_components as dcc
from dash import dcc
#import dash_html_components as html
from dash import html
#import dash_table
from dash import dash_table
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
# IMPORTATIONS COMMENTÉES POUR DÉBOGAGE
# import transformers
# import torch
# from transformers import pipeline
# from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
# import spacy
# import numpy as np
# from langchain_text_splitters import RecursiveCharacterTextSplitter


print("--- Import library succeeded ---")
#nlp = spacy.load("en_core_web_lg")
#
#model_name = "Qwen/Qwen2.5-1.5B-Instruct"
#
#tokenizer = AutoTokenizer.from_pretrained(model_name)
#model = AutoModelForCausalLM.from_pretrained(
#    model_name,
#    device_map="auto",
#    dtype="auto"
#)

# Les fonctions qui utilisent les librairies lourdes peuvent causer des erreurs
# si elles ne sont pas définies (NameError). Je les mets en commentaire.
# def embed(text):
#     return nlp(text).vector

# def chunk_texts(df, text_column):
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=500,
#         chunk_overlap=50
#     )
#     texts = df[text_column].astype(str).tolist()
#     combined = " ".join(texts)
#     chunks = splitter.split_text(combined)
#     return chunks

# Le reste du code du layout et des callbacks est conservé pour vérifier le démarrage.

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.config.suppress_callback_exceptions = True

dropdown_style = {"marginTop":"0.5rem","color":"green"}


card_header_style = {"backgroundColor":"blue","color":"white","font-size":30,"fontWeight":"bold","height":"50px"}



content = html.Div([ # this code section taken from Dash docs https://dash.plotly.com/dash-core-components/upload
    
    dbc.CardHeader("File",style=card_header_style),
    
    
    
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    
    html.Div(id='output-datatable'),
    html.Div(id='output-div'),
])

# --- STYLE POUR LA BARRE SUPÉRIEURE ---
# Ce style définit la couleur de fond en noir et le texte en blanc (ou clair).
# Le "z-index" est ajouté pour s'assurer que la barre reste au-dessus des autres éléments.
TOP_BAR_STYLE = {
    "backgroundColor": "#212529",  # Couleur noire ou gris très foncé pour le fond
    "color": "white",              # Couleur du texte
    "padding": "0.5rem 1rem",      # Espacement intérieur
    "boxShadow": "0 2px 4px rgba(0,0,0,.5)", # Une petite ombre pour la profondeur
    "zIndex": 1000,                # Assure qu'elle est au-dessus (utile si vous utilisez sticky='top')
}

# --- LA VARIABLE top_bar ---
# Cette structure utilise dbc.Navbar pour créer la barre.
# Le composant dbc.Brand est idéal pour afficher le titre de l'application.

top_bar = dbc.Navbar(
    dbc.Container(
        # Contenu de la barre de navigation
        [
            # 1. Titre de l'application (aligné à gauche)
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            "Text Mining",
                            # Utilisez la classe "display-5" de Bootstrap pour un titre bien visible
                            # "me-auto" assure que cet élément prend l'espace disponible à gauche
                            className="text-white fw-bold display-6 me-auto",
                            style={"fontSize": "2rem"} # Optionnel : ajuste la taille si display-6 est trop grand
                        ),
                        align="center",
                    )
                ],
                # 'g-0' supprime les gouttières (espaces) entre les colonnes
                className="g-0 w-100",
            ),
        ],
        fluid=True, # La barre occupe toute la largeur
    ),
    # Propriétés de dbc.Navbar
    dark=True,             # Rend les liens (si vous en ajoutez) en blanc, car le fond est sombre
    color="dark",          # Utilise la couleur prédéfinie 'dark' de Bootstrap (généralement noir/gris foncé)
    sticky="top",          # (Optionnel) Garde la barre en haut de l'écran lorsque l'utilisateur fait défiler
    style=TOP_BAR_STYLE    # Applique le style défini ci-dessus pour la couleur et la bordure
)

        

app.layout = html.Div([
    html.Div([dcc.Location(id="url"),top_bar]),
    html.Div([
        dbc.Row([
            dbc.Col(content,md=12)
        ],className="g-0",style={"width":"100%"})
    ],style={"width":"100%"})
],style={"width":"100vw"})
       

def parse_contents(contents, filename, date):
    
    print(0000)
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            print(1111111)
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    print("Excel imported successfully")

    # Toutes les lignes de manipulation de DataFrame qui utilisent des fonctions NLP/LLM
    # sont également commentées car elles pourraient faire référence à des variables (comme nlp)
    # qui ne sont plus importées. Je laisse les lignes de mise à jour du layout
    # et des dropdowns en place.

    dropdown_target_text_mining = html.Div(
    [html.B("Target:",style={"color":"gray"}),
     dcc.Dropdown(id="dropdown_target_text_mining",
                  options=[{"label":x,"value":x} for x in df["target"].unique()],
                  value=df["target"].unique(),multi=True,style=dropdown_style)])
    
    

    

    dropdown_time_text_mining = html.Div(
        [
            html.B('Time', style={'color': 'gray'}),
            dcc.Dropdown(
                id='dropdown_time_text_mining',
                options=[{'label': x, 'value': x} for x in df['time'].unique()],
                value=df['time'].unique(),
                multi=True,
                style=dropdown_style)
        ]
    )

    

    return html.Div([
            html.H5(filename),
            html.H6(datetime.datetime.fromtimestamp(date)),
            dbc.Card([
                dbc.CardHeader("Filters",style=card_header_style),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col(dropdown_target_text_mining,style={"width":"50%","margin-bottom":"10px","margin-top":"10px"},md=6),
                            dbc.Col(dropdown_time_text_mining,style={"width":"50%","margin-bottom":"10px","margin-top":"10px"},md=6),
                                ]),
                            ]),
                    ]),
            dbc.Card([
                dbc.CardHeader("AI Assistant",style=card_header_style),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col(html.Div(dbc.Input(
                                                            type="text",
                                                            id="question", # ID requis par l'utilisateur
                                                            placeholder="Tapez votre question ici...",
                                                            className="mb-3",
                                                            n_submit=0 # Permet d'envoyer en appuyant sur Entrée
                                                        )),md=10),
                            dbc.Col(html.Div(html.Button(id="submit-button",  style={"width":"50%","margin-bottom":"10px","margin-top":"10px"}, children="Send")),md=2),
                            dbc.Label("Réponse de l'IA :", className="block text-sm font-medium mb-3 text-gray-300 mt-4"),
                                html.Div(
                                    "🤖 Hi ! Ask me any question.",
                                    id="response", # ID requis par l'utilisateur
                                    style={
                                            'minHeight': '100px',
                                            'padding': '1.5rem',
                                            #'backgroundColor': '#374151', # Gris moyen pour le fond de la réponse
                                            'borderRadius': '0.75rem',
                                            'whiteSpace': 'pre-wrap', # Important pour les retours à la ligne
                                            'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                                        },
                                    className="text-gray-200"
                    ),
                            ]),
                    ]),
            ]),
                
        #
        
        # Je commente cette ligne car df n'existe pas si le fichier n'a pas été lu
        # dcc.Store(id='stored-data', data=df.to_dict('records')),
        # Pour ne pas avoir d'erreur NameError 'df'
        
        dcc.Store(id='stored-data', data=''), # Remplacé par une valeur vide
        
    ])


@app.callback(Output('output-datatable', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    #print("function activated")
    if list_of_contents is not None:
        #print("not none")
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children