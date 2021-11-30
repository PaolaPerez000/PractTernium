from pandas.core.base import NoNewAttributesMixin
import dash
from dash import dcc, html, dash_table
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input, State
import base64
import io
import plotly.express as px
import plotly.graph_objs as go


data = None

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Ternium Practicas"

app.layout = html.Div(
    children=[ 
       
        html.Div(id="hidden-div", style={"display":"none"}) ,

        html.Div(
            children=[
                html.Div(className="centrar", children =
                    html.Img(src=app.get_asset_url ("Ternium.png"), width = "300px"),
                ),
            ],
            className="header",
        ),


        html.Div(
            children=[
                html.Div (
                    className = "menu-row", children = [
                    html.Div([  
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
                    ]),

                    html.Div( id = "test",
                        children=[
                            dcc.Dropdown(
                                id="Objetivo",
                                options=[],
                                clearable=False,
                                className="dropdown",
                            ),
                        ]
                    ),
                    ]
                ),


                html.Div(className="centrar", children = [
                html.Div(

                    id = "test2", className="Checklist",
                    children=[
                        html.Div(children="Variables a correlacionar", className="menu-title"),
                        dcc.Checklist(
                            id="varCorrelacion",
                            options=[],
                            value=[],
                            className="list",
                        ),
                    ],
                ),
                ] 

                ),
                html.Div(children="Filtrado Variable Objetivo", className="menu-title centrar" ),
                html.Div(className ="slider", children =
                    dcc.Slider(id= "sigma",
                        min=0,
                        max=3,
                        step=None,
                        marks={
                            0: 'N/A',
                            3: '3σ',
                            2: '2σ',
                            1: 'σ',
                            
                        },
                       # value=0
                    )
                ),
                html.Div(children="Elija el coeficiente de correlacion", className="menu-title centrar" ),
                html.Div(className ="slider", children =
                    dcc.Slider(id= "coeficienteCorrelacion",
                        min=0.1,
                        max=0.9,
                        step=None,
                        marks={

                            0.1: '0.1',
                            0.2: '0.2',
                            0.3: '0.3',
                            0.4: '0.4',
                            0.5: '0.5',
                            0.6: '0.6',
                            0.7: '0.7',
                            0.8: '0.8',
                            0.9: '0.9'
                            
                        },
                       # value=0
                    )
                ),


                
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    id = "cormat_table",
                    children="",
                    className ="card card2",
                ),
                html.Div(
                    id = "correlationPlot",
                    children="",
                    className = "card"
                ),
                html.Div(id ="price-chart",
                    children="",
                    className="card",
                ),
            
            ],
            className="wrapper",
        ),
        

    ]
)

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df


@app.callback(  output = [Output('test','children'),
                Output('test2', 'children')],
                inputs = [Input('upload-data', 'contents')],
                state = [State('upload-data', 'filename'),
                State('upload-data', 'last_modified')])

def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        global data

        data = [ 
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)] [0]

        varibles = list(data)
        a = [html.Div(children="Variable Objetivo", className="menu-title"),
                            dcc.Dropdown(
                                id="Objetivo",
                                options=[{"label":val,"value":val.replace(" ", "")} for val in varibles],
                                clearable=False,
                                className="dropdown",
                            ), ]  
        b = [html.Div(children="Variables a analizar", className="menu-title"),
                            dcc.Checklist(
                                id="varCorrelacion",
                                options=[{"label":val,"value":val.replace(" ", "")} for val in varibles],
                                value=[],
                                className="list",
                            ), ]  
        data.columns = [col.replace (" ", "") for col in data.columns]
              
        return (a, b)
    else: 
        return [],[]

def anylizeData(varObjetivo, varCorrelacion, sigma, coeficienteCorrelacion):
    global data
    local_data = data
    if not sigma == 0:
         
        valSigma = local_data[varObjetivo]
        menosSigma, masSigma = (valSigma.mean() - sigma * valSigma.std(), valSigma.mean() + sigma * valSigma.std())

        local_data = local_data[local_data[varObjetivo] > menosSigma]

        local_data = local_data[local_data[varObjetivo] < masSigma]
 
    

    data_correlation = local_data[varCorrelacion]

    desc_Correlacion = data_correlation.describe()

    repres_cols = [] 
    for c in desc_Correlacion.columns:
        if (desc_Correlacion.at["count",c] > len(local_data)-50): 
            repres_cols.append(c)

    not_features = [varObjetivo] 

    to_check = [c for c in repres_cols if c not in not_features] 
    to_check.extend([varObjetivo]) #objetivo 
    cormat = data_correlation[to_check].corr() 
    cormat_result = cormat[abs(cormat[varObjetivo])>=coeficienteCorrelacion].sort_values(by=varObjetivo,ascending=False)
    

    return cormat, cormat_result

@app.callback(
    [Output("price-chart", "children"), 
    Output ("cormat_table", "children"), 
    Output ("correlationPlot", "children")],

    [
        Input("Objetivo", "value"),
        Input("varCorrelacion", "value"),
        Input("sigma", "value"),
        Input ("coeficienteCorrelacion", "value")
    ],
)
def update_charts(varObjetivo, correlacion, sigma, coeficienteCorrelacion):
    
    if not (varObjetivo==None or correlacion==[] or sigma == None or coeficienteCorrelacion == None):
        global data
        cormat, cormat_result= anylizeData(varObjetivo, correlacion, sigma, coeficienteCorrelacion)
        fig = px.imshow(cormat)
        #Si es un type(series)
        cormat_result = cormat_result.iloc[:,-1].to_frame()

        #Si es un dataframe
        #cormat_result = cormat_result.iloc[:,-3:]

        correlaciones = []
        row_names = cormat_result.index.values.tolist()



        for i, j in zip(row_names, cormat_result.to_dict('records')):
            dic_base = {'Variables':i}
            dic_base.update(j)
            correlaciones.append(dic_base) 

        column_names = cormat_result.columns.values.tolist()
        column_names.insert(0,'Variables')


        figuraplot = go.Figure(data=[go.Scatter(x=data['Fecha'], y=data[value], name=value) for value in row_names])

         

        return [dcc.Graph(
                        config={"displayModeBar": False},
                        figure=fig
                    ), 
                dash_table.DataTable(
                id='tbl', data=correlaciones,
                columns=[{"name": i, "id": i} for i in column_names],
                ),
                dcc.Graph(
                    figure=figuraplot
                )
                ]
    else:
        return ['', '','']

if __name__ == "__main__":
    app.run_server(debug=True)
    