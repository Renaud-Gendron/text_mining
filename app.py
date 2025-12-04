from dash import Dash, html

app = Dash(__name__)
server = app.server

app.layout = html.Div("Hello world!")

#if __name__ == "__main__":
#    app.run(debug=True)