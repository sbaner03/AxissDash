import pandas as pd
from axissClass import Axissclass
from axissPrintfigs import printfigs
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.figure_factory as ff
from datetime import datetime,timedelta,date




app = dash.Dash()
my_css_url = "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
app.css.append_css({
    "external_url": my_css_url
})


analysis = Axissclass('1-1-2017','31-07-2017')
centredf = pd.read_csv('./Masters/centredf.csv')
regionlist = list(centredf['Region'].unique())+['All']
regionoptions = [{'label': i,'value':i} for i in regionlist]
clusterlist = list(centredf['Cluster'].unique())+['All']
clusterlistoptions = [{'label': i,'value':i} for i in clusterlist]
centrelist = list(centredf['Centre'].unique())+['All']
centrelistoptions = [{'label': i,'value':i} for i in centrelist]
lenslist = ['Classification','PatientType', 'AgeBand','Gender']
lenslistoptions = [{'label': i,'value':i} for i in lenslist]
lens = 'Classification'
df, revgraph = printfigs(analysis, indicator = 'Received',grplist = ['Year','Month',lens],
              regionlist = ['All'],clusterlist = ['All'],centrelist = ['All'])
_, patgraph = printfigs(analysis, indicator = 'Reg.No',grplist = ['Year','Month',lens],
              regionlist = ['All'],clusterlist = ['All'],centrelist = ['All'])

df = df.fillna(0)
table = ff.create_table(df)
startdate = datetime.strftime(min(analysis.proc['Receipt Date']),'%d-%m')
enddate = datetime.strftime(max(analysis.proc['Receipt Date']),'%d-%m')

displaydiv = html.Div(className = 'container-fluid',children=[
    html.H1(className = "h3",children='Online Anaysis Module from {0} to {1} 2017'.format(startdate,enddate)),
    dcc.Graph(id='revgraph',figure = revgraph),
    dcc.Graph(id='patgraph',figure = patgraph),
    dcc.Graph(id='table',figure = table)
])

selectiondiv = html.Div(className = 'container-fluid', children=[
html.Img(className="img-responsive",
    src = 'http://www.axissdental.com/wp-content/themes/twentytwelve/images/logo.jpg'),
    html.Br(),
    html.Label('Select Region(s)'),
    dcc.Dropdown(
        id='region_selection',
        options=regionoptions,
        value=['All'],
        multi=True
    ),
    html.Br(),
    html.Label('Select Cluster(s)'),
    dcc.Dropdown(
        id='cluster_selection',
        options=clusterlistoptions,
        value=['All'],
        multi=True
    ),
    html.Br(),
    html.Label('Select Clinic(s)'),
    dcc.Dropdown(
        id='clinic_selection',
        options=centrelistoptions,
        value=['All'],
        multi=True
    ),
    html.Br(),
    html.Label('Select Lens'),
    dcc.Dropdown(
        id='lens_selection',
        options=lenslistoptions,
        value='Classification',
        multi=False
    )
])

app.layout = html.Div(className='row', children=[html.Div(className = 'col-sm-2',children = [selectiondiv]),html.Div(className= 'col-sm-10',children = [displaydiv])])


@app.callback(
    Output(component_id='cluster_selection',component_property = 'options'),
    [Input(component_id='region_selection', component_property='value')]
)

def updateclusteroptions(region):
    centredf = pd.read_csv('./Masters/centredf.csv')
    centredf = centredf[centredf['Region'].isin(region)]
    clusterlist = list(centredf['Cluster'].unique())+['All']
    clusterlistoptions = [{'label': i,'value':i} for i in clusterlist]
    return clusterlistoptions

@app.callback(
    Output(component_id='clinic_selection',component_property = 'options'),
    [Input(component_id='region_selection', component_property='value'),
    Input(component_id='cluster_selection', component_property='value')]
)

def updateclinicoptions(region, cluster):
    centredf = pd.read_csv('./Masters/centredf.csv')
    centredf = centredf[(centredf['Cluster'].isin(cluster))&(centredf['Region'].isin(region))]
    centrelist = list(centredf['Centre'].unique())+['All']
    centrelistoptions = [{'label': i,'value':i} for i in centrelist]
    return centrelistoptions



@app.callback(
    Output(component_id='revgraph',component_property = 'figure'),
    [Input(component_id='region_selection', component_property='value'),
    Input(component_id='cluster_selection', component_property='value'),
    Input(component_id='clinic_selection', component_property='value'),
    Input(component_id='lens_selection', component_property='value')]
)
def update_revgraph(region,cluster,clinic,lens):

    df, revgraph = printfigs(analysis, indicator = 'Received',grplist = ['Year','Month',lens],
                  regionlist = region,clusterlist = cluster,centrelist = clinic)
    return revgraph

@app.callback(
    Output(component_id='patgraph',component_property = 'figure'),
    [Input(component_id='region_selection', component_property='value'),
    Input(component_id='cluster_selection', component_property='value'),
    Input(component_id='clinic_selection', component_property='value'),
    Input(component_id='lens_selection', component_property='value')]
)
def update_patgraph(region,cluster,clinic,lens):

    df, patgraph = printfigs(analysis, indicator = 'Reg.No',grplist = ['Year','Month',lens],
                  regionlist = region,clusterlist = cluster,centrelist = clinic)
    return patgraph

@app.callback(
    Output(component_id='table',component_property = 'figure'),
    [Input(component_id='region_selection', component_property='value'),
    Input(component_id='cluster_selection', component_property='value'),
    Input(component_id='clinic_selection', component_property='value'),
    Input(component_id='lens_selection', component_property='value')]
)
def update_table(region,cluster,clinic,lens = 'classification'):
    df, fig = printfigs(analysis, indicator = 'Reg.No',grplist = ['Year','Month',lens],
                  regionlist = region,clusterlist = cluster,centrelist = clinic)
    df = df.fillna(0)
    table = ff.create_table(df)
    return table


app.run_server(debug=True)
