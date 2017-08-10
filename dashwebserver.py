import pandas as pd
from axissClass import Axissclass
from axissPrintfigs import printfigs
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.figure_factory as ff



app = dash.Dash()
analysis = Axissclass('1-1-2017','31-07-2017')
centredf = pd.read_csv('./Masters/centredf.csv')
regionlist = list(centredf['Region'].unique())+['All']
regionoptions = [{'label': i,'value':i} for i in regionlist]
clusterlist = list(centredf['Cluster'].unique())+['All']
clusterlistoptions = [{'label': i,'value':i} for i in clusterlist]
centrelist = list(centredf['Centre'].unique())+['All']
centrelistoptions = [{'label': i,'value':i} for i in centrelist]
df, fig = printfigs(analysis, indicator = 'Received',grplist = ['Year','Month','Classification'],
              regionlist = ['All'],clusterlist = ['All'],centrelist = ['All'])


markdown_text = '''
Online Anaysis Module
'''

app.layout = html.Div(children=[
    html.H1(children='Online Analysis'),
    html.Label('Select Region(s)'),
    dcc.Dropdown(
        id='region_selection',
        options=regionoptions,
        value=['All'],
        multi=True
    ),
    html.Label('Select Cluster(s)'),
    dcc.Dropdown(
        id='cluster_selection',
        options=clusterlistoptions,
        value=['All'],
        multi=True
    ),
    html.Label('Select Clinic(s)'),
    dcc.Dropdown(
        id='clinic_selection',
        options=centrelistoptions,
        value=['All'],
        multi=True
    ),
    dcc.Graph(id='example-graph-1',figure = fig),
    dcc.Graph(id='example-graph-2',figure = fig)
])

@app.callback(
    Output(component_id='example-graph-1',component_property = 'figure'),
    [Input(component_id='region_selection', component_property='value'),
    Input(component_id='cluster_selection', component_property='value'),
    Input(component_id='clinic_selection', component_property='value')]
)
def update_output_fig1(region,cluster,clinic):

    df, fig = printfigs(analysis, indicator = 'Received',grplist = ['Year','Month','Classification'],
                  regionlist = region,clusterlist = cluster,centrelist = clinic)
    return fig

@app.callback(
    Output(component_id='example-graph-2',component_property = 'figure'),
    [Input(component_id='region_selection', component_property='value'),
    Input(component_id='cluster_selection', component_property='value'),
    Input(component_id='clinic_selection', component_property='value')]
)
def update_output_fig2(region,cluster,clinic):

    df, fig = printfigs(analysis, indicator = 'Reg.No',grplist = ['Year','Month','Classification'],
                  regionlist = region,clusterlist = cluster,centrelist = clinic)
    return fig


app.run_server(debug=True)
