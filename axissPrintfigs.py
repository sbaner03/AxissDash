
# coding: utf-8

# In[1]:


from sqlalchemy import *
import sys
import pandas as pd
import numpy as np
from datetime import datetime,timedelta,date
import plotly.plotly as py
import plotly.graph_objs as go
from axissClass import Axissclass


def printfigs (analysis,indicator = 'Received',grplist = ['Year','Month','Classification'],
              regionlist = ['All'],clusterlist = ['All'],centrelist = ['All']):
    centredf = pd.read_csv('./Masters/centredf.csv')
    try:
        if regionlist==['All']:
            regionlist = list(centredf['Region'].unique())
        if clusterlist==['All']:
            clusterlist = list(centredf['Cluster'].unique())
        if centrelist==['All']:
            centrelist = list(centredf['Centre'].unique())
        newcentre = list(centredf[(centredf['Region'].isin(regionlist))&(centredf['Cluster'].isin(clusterlist))&(centredf['Centre'].isin(centrelist))]['Centre'])
        if not newcentre:
            newcentre = list(centredf['Centre'].unique())
    except:
        newcentre = list(centredf['Centre'].unique())
    print (newcentre)
    df = analysis.procanalysis(newcentre, grplist = grplist)
    df = df[df['Year']!='All']
    df = df[df['Received']>0.0]
    monthdf = pd.pivot_table(df,index = 'Month',values = indicator,aggfunc = {indicator: np.sum}).reset_index()
    df = pd.merge(df,monthdf, left_on = 'Month', right_on='Month', suffixes=['','_total'],how = 'inner')
    df['Perc'] = df.apply(lambda x: np.round(x[indicator]*100.0/x[indicator+'_total'],0),axis=1)
    datalist = []
    field = grplist[2]
    slicer = list(df[field].unique())
    for counter,slx in enumerate(slicer):
        slxdf = df[df[field]==slx]
        trace = go.Bar(
            x = list(slxdf['Month']),
            y = list(slxdf[indicator]),
            text = list(['%{0}'.format(i) for i in slxdf['Perc'] if i>0]),
            textposition='bottom',
            name = slx
        )
        datalist.append(trace)

    if indicator == 'Reg.No':
        printingtext = 'Patients'
    elif indicator == 'Received':
        printingtext = 'Revenue in Rs Lacs'

    layout = go.Layout(
        title='{}'.format(printingtext),
        annotations=[dict(x=str(xi),y=yi,
                 text=str(yi),
                 xanchor='center',
                 yanchor='bottom',
                 showarrow=False,
            ) for xi, yi in zip(monthdf['Month'], monthdf[indicator])],
        legend=dict(
                orientation="h"),
        barmode='stack'
    )


    fig = go.Figure(data=datalist, layout=layout)
    return df,fig
