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
import transformers
import torch
from transformers import pipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import spacy
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter

nlp = spacy.load("en_core_web_lg")

model_name = "Qwen/Qwen2.5-1.5B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    dtype="auto"
)

def embed(text):
    return nlp(text).vector

def chunk_texts(df, text_column):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    texts = df[text_column].astype(str).tolist()
    combined = " ".join(texts)
    chunks = splitter.split_text(combined)
    return chunks

def summarize(selected_text, question):
    print(1)
    summarizer = pipeline(
    "text-generation",#,
    model=model,
    tokenizer=tokenizer)#,
    #max_new_tokens=250#,
    ##do_sample=False
    #
    #)
    print(2)
    prompt = f"""Answer the question based ONLY on the text below.
    Provide 3–5 bullet points.
    Be specific and avoid generic statements.
    
    Text:
    {selected_text}
    
    Question:
    {question}
    
    Answer: """
    result = summarizer(prompt)[0]["generated_text"]
    print(3)
    print(result)
    return result.split("Summary:", 1)[-1].strip()




external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

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
    "backgroundColor": "#212529",  # Couleur noire ou gris très foncé pour le fond
    "color": "white",              # Couleur du texte
    "padding": "0.5rem 1rem",      # Espacement intérieur
    "boxShadow": "0 2px 4px rgba(0,0,0,.5)", # Une petite ombre pour la profondeur
    "zIndex": 1000,                # Assure qu'elle est au-dessus (utile si vous utilisez sticky='top')
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
    dark=True,             # Rend les liens (si vous en ajoutez) en blanc, car le fond est sombre
    color="dark",          # Utilise la couleur prédéfinie 'dark' de Bootstrap (généralement noir/gris foncé)
    sticky="top",          # (Optionnel) Garde la barre en haut de l'écran lorsque l'utilisateur fait défiler
    style=TOP_BAR_STYLE    # Applique le style défini ci-dessus pour la couleur et la bordure
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

    # df['len'] = df['text'].fillna('').apply(len)
    # df['text_no_stop_words'] = df['text'].fillna('')
    # df['text_no_stop_words'] = df['text_no_stop_words'].apply(get_number_of_words_transcript)

    # # print(len(df[df['text_no_stop_words'] == '']))
    # # print(len(df[df['text'] == '']))

    # print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

    #df['len_cat'] = "0 words"
    #df.loc[(df['len'] > 0) & (df['len'] <= 10), "len_cat"] = "1-10 words"
    #df.loc[(df['len'] > 10) & (df['len'] <= 50), "len_cat"] = "10-50 words"
    #df.loc[(df['len'] > 50), "len_cat"] = "50 + words"
    #
    #df = text_mining_columns(df=df, columns='text_transcript_customer_without_stopwords')
    #
    #df['target'] = df['target'].astype(str)
    #df['compound_score'] = df['text'].astype(str).apply(get_sentiment_compound)
    #df['most_important_sentences'] = df['text'].astype(str).apply(extract_most_important_sentences_customer)
    #df['polarity_score'] = df['text'].astype(str).apply(get_sentiment_polarity)
    #
    #df.loc[df['compound_score'] > 0.05, 'sentiment'] = "Positive"
    #df.loc[(df['compound_score'] <= 0.05) & (df['compound_score'] >= -0.05), 'sentiment'] = "Neutral"
    #df.loc[df['compound_score'] < -0.05, 'sentiment'] = "Negative"
    #df.loc[df['text'].isna()] = df['text'].apply(lambda x: 'No Comment/Transcript')
    #
    ## df = pd.DataFrame(df)
    #
    ## # print(df['text'])
    #df['text_no_stop_words'] = df['text'].fillna('').str.lower()
    #df['text_no_stop_words'] = df['text_no_stop_words'].str.replace(r'[^a-z ]', '', regex=True)
    #df['text_no_stop_words'] = df['text_no_stop_words'].apply(remove_punct_2)
    #df['text_no_stop_words'] = df['text_no_stop_words'].apply(lambda x: ' '.join([word for word in x.split() if word not in (additional_stop_words)]))
    #
    ## # df['text_no_stop_words'] = df['text_no_stop_words'].apply(lambda words: ' '.join(word for word in words if word not in additional_stop_words))
    #df['text_no_stop_words'] = df['text_no_stop_words'].apply(lambda words: ' '.join([word for word in words if word not in additional_stop_words]))
    #
    #
    #list_words = []
    #df['text_no_stop_words'] = df['text_no_stop_words'].astype(str)
    #df['text_no_stop_words'] = df['text_no_stop_words'].replace("='", '')
    #df['terms'] = ''
    #
    ## # print('before language')
    #df['language'] = df['text'].astype(str).apply(detect_lang)
    ## # print('after language')
    #
    #df['words'] = df['text_no_stop_words'].apply(to_list)
    #
    #for text in df['text_no_stop_words'].to_list():
    #    words = text.split()
    #    list_words = list_words + words
    #
    #df_bigrams = detect_ngram(df, 2).head()
    #df_bigrams['pattern'] = df_bigrams['pattern'].str.rstrip()
    #
    #list_bigrams = df_bigrams['pattern'].to_list()
    #list_words_bigrams = list_words + list_bigrams

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

    

    #dropdown_ngrams_text_mining = html.Div(
    #    [
    #        html.B('Ngrams', style={'color': 'gray'}),
    #        dcc.Dropdown(
    #            id='dropdown_text_mining_ngrams',
    #            options=[{'label': x, 'value': x} for x in range(1,3)],
    #            value=1,
    #            multi=False,
    #            style=dropdown_style)
    #    ]
    #)
#
    #
#
    #dropdown_sentiment_text_mining = html.Div(
    #    [
    #        html.B('Sentiment Score', style={'color': 'gray'}),
    #        dcc.Dropdown(
    #            id='dropdown_text_mining_sentiment',
    #            options=[{'label': 'Polarity', 'value': 'Polarity'},
    #                     {'label': 'Compound', 'value': 'Compound'}],
    #            value='Polarity',
    #            multi=False,
    #            style=dropdown_style)
    #    ]
    #)
#
    #
#
    #search_bar_include = html.Div(
    #    [
    #        html.B('Search Term', style={'color': 'gray'}),
    #        dcc.Dropdown(
    #            id='user_search_include',
    #            options=[{'label': x, 'value': x} for x in sorted(list(set(list_words_bigrams)))],
    #            value=[],
    #            multi=True,
    #            style=dropdown_style)
    #    ]
    #)
#
    #
#
    #search_bar_exclude = html.Div(
    #    [
    #        html.B('Exclude Term', style={'color': 'gray'}),
    #        dcc.Dropdown(
    #            id='user_search_exclude',
    #            options=[{'label': x, 'value': x} for x in sorted(list(set(list_words_bigrams)))],
    #            value=[],
    #            multi=True,
    #            style=dropdown_style)
    #    ]
    #)
#
    #
#
    #dropdown_column_term = html.Div(
    #    [
    #        html.B('Column Term', style={'color': 'gray'}),
    #        dcc.Dropdown(
    #            id='dropdown_column_term',
    #            options=[{'label': 'No', 'value': 'No'},
    #                     {'label': 'Yes', 'value': 'Yes'}],
    #            value='No',
    #            multi=False,
    #            style=dropdown_style)
    #    ]
    #)
#
    #
#
    #dropdown_time_term = html.Div(
    #    [
    #        html.B('Time Term', style={'color': 'gray'}),
    #        dcc.Dropdown(
    #            id='dropdown_time_term',
    #            options=[{'label': 'No', 'value': 'No'},
    #                     {'label': 'Yes', 'value': 'Yes'}],
    #            value='No',
    #            multi=False,
    #            style=dropdown_style)
    #    ]
    #)
#
    #
#
    #dropdown_language = html.Div(
    #    [
    #        html.B('Language', style={'color': 'gray'}),
    #        dcc.Dropdown(
    #            id='dropdown_language',
    #            options=[{'label': x, 'value': x} for x in df['language'].unique()],
    #            value=df['language'].unique(),
    #            multi=True,
    #            style=dropdown_style)
    #    ]
    #)

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
                            dbc.Col(html.Div(html.Button(id="submit-button",  style={"width":"50%","margin-bottom":"10px","margin-top":"10px"}, children="Send")),md=2),
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
        
        dcc.Store(id='stored-data', data=df.to_dict('records')),
        #html.Pre(contents[0:200] + '...', style={
        #    'whiteSpace': 'pre-wrap',               
        #    'wordBreak': 'break-all'
        #}),
        
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


@app.callback(Output('response', 'children'),
              Input('submit-button','n_clicks'),
              State('stored-data','data'),
              State('question','value'),
              State("dropdown_target_text_mining","value"),
              State("dropdown_time_text_mining","value"))
def make_graphs(n, df, question,target,time):
    if n is None:
        return dash.no_update
    else:
        #context = ' '.join(pd.DataFrame(df)['text'].astype(str).tolist())
        print(target)
        df = pd.DataFrame(df)
        print(df.head())
        target_str = []

        for x in target:
            target_str.append(str(x))
        chunks = chunk_texts(df[ (df["target"].astype(str).isin(target_str))
                                &(df["time"].isin(time))]
                                , "text")
        
        
        
        # 1. Create embeddings for chunks
        chunk_embeddings = [embed(chunk) for chunk in chunks]

        # 2. Embed the query
        query_emb = embed("Qualities")

        # 3. Compute similarity
        scores = [np.dot(query_emb, ce) for ce in chunk_embeddings]

        # 4. Select top chunks
        top_indices = np.argsort(scores)[-3:]   # top 3
        selected_text = " ".join([chunks[i] for i in top_indices])  

        print("selected_text")
        print(selected_text)
        x = summarize(selected_text, question)
        #print(df)
        print("x")
        print(x)
       
        result = x.split("Answer: ",1)[1]
        
        print("result")
        print(result)

        # Print the answer
        #print(result["answer"])
        
        return result



#if __name__ == '__main__':
#    app.run(debug=False)