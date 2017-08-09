from sqlalchemy import *
import sys
import pandas as pd
import numpy as np
from datetime import datetime,timedelta,date
import plotly.plotly as py
import plotly.graph_objs as go


engine = create_engine("mysql+pymysql://iepuser:iep54321@35.185.171.117/axiss")
class Axissutils:

    def getperc(self,a,b):
        try:
            return round(a*100.0/b,1)
        except:
            return 0.0

    def dateconv(self,x,formatx):
        try:
            return datetime.strptime(x,formatx)
        except:
            return 'Check'

    def cleannorthdoctor(self,x,region):
        if region == 'North':
            if x=='ADISIN':
                return 'ADISINN'
            elif x=='NEHAGUP' or x=='NEHGUP' or x=='NEHA':
                return 'NEHA'
            elif x=='AMISAC':
                return 'AMIT'
            elif x=='DEESHA':
                return 'DEESHAN'
            elif x =='NEEKAM':
                return 'NEETU'
            elif x=='OLDDOC':
                return 'SUDMEH'
            elif x=='KARKHU':
                return 'KARKHA'
            else:
                return x
        else:
            return x

    def getpatientvintage(self,activitydate,regdate,newthreshold):
        try:
            patvintage = (activitydate-dateconv(regdate,'%d-%m-%Y')).days
            if patvintage>=newthreshold:
                return 'Old'
            else:
                return 'New'
        except:
            return 'Check'

    def agebanding(self,x):
        if x<=12:
            return 'Kids <=12'
        elif 13<=x<=25:
            return 'Youth 13-25'
        elif 26<=x<=40:
            return 'Mid 26-40'
        elif 41<=x<=80:
            return 'Elder 40-80'
        elif x>=81:
            return 'Old >=81'
        else:
            return 'Check'


# In[3]:


class Axissclass(Axissutils):
	#### query based on timestamp is not working
	#### query should return all the characteristics of the proc - Region, Cluster, Work Done

    def __init__(self,start,end):
        format1 = '%d-%m-%Y'
        format2 = '%Y-%m-%d'
        retformat = format1
        self.newthreshold= 30 ### days from registration when a patient is viewed as new


        try:
            startdate = datetime.strptime(start,'%d-%m-%Y')
        except:
            startdate = datetime.strptime('01-01-2017','%d-%m-%Y')

        try:
            enddate = datetime.strptime(end,'%d-%m-%Y')
        except:
            enddate = datetime.today()

        proc = pd.read_sql("SELECT * FROM axiss", engine)
        treatment = pd.read_sql("SELECT * FROM axissplan", engine)
        centre = pd.read_csv('./Masters/centredf.csv')
        classification = pd.read_csv('./Masters/catdf.csv')

        treatment['Visit Date'] = treatment.apply(lambda x: datetime.strptime(x['Visit Date'],format1),axis=1)
        proc = proc[enddate>=proc['Receipt Date']]
        proc = proc[startdate<=proc['Receipt Date']]
        proc = proc[~proc['Receipt Date'].isnull()]
        treatment = treatment[enddate>=treatment['Visit Date']]
        treatment = treatment[startdate<=treatment['Visit Date']]
        treatment = treatment[~treatment['Visit Date'].isnull()]

        ### basic clean up which should be done before entering data into the database
        #### cleanup for mohali name change
        proc['Centre'] = proc.apply(lambda x: x['Centre'] if x['Centre']!='mohalifh28062017' else 'MOHALIFH', axis=1)
        treatment['Centre'] = treatment.apply(lambda x: x['Centre'] if x['Centre']!='mohalifh28062017' else 'MOHALIFH', axis=1)
        ##### provide centre characteristics to every centre
        proc = pd.merge(proc,centre, left_on = 'Centre', right_on='Centre',how='left')
        treatment = pd.merge(treatment,centre, left_on = 'Centre', right_on='Centre',how='left')

        ##### provide centre characteristics to every centre
        proc = pd.merge(proc,classification, left_on = 'Category', right_on='Category',how='left')
        treatment = pd.merge(treatment,classification, left_on = 'Work Required Category', right_on='Category',how='left')

        proc['Doctor'] = proc.apply(lambda x: self.cleannorthdoctor(x['Doctor'],x['Region']),axis=1)
        treatment['Doctor'] = treatment.apply(lambda x: self.cleannorthdoctor(x['Doctor'],x['Region']),axis=1)

        #### some inline classification which ideally should be done in the database but can be left out for the time being

        proc['PatientType'] = proc.apply(lambda x: self.getpatientvintage(x['Receipt Date'],x['Reg.Date'],self.newthreshold),axis=1)
        proc['AgeBand'] = proc.apply(lambda x: self.agebanding(x['Age']),axis=1)
        treatment['PatientType'] = treatment.apply(lambda x: self.getpatientvintage(x['Visit Date'],x['Reg.Date'],self.newthreshold),axis=1)
        treatment['AgeBand'] = treatment.apply(lambda x: self.agebanding(x['Age']),axis=1)

        for col in ['Cluster','Region','Hospital','Classification','PatientType','AgeBand']:
            ix = proc[proc[col].isnull()].index
            proc.loc[ix,col] = 'Not Available'
            ix = treatment[treatment[col].isnull()].index
            treatment.loc[ix,col] = 'Not Available'

        proc['Month'] = proc.apply(lambda x: x['Receipt Date'].month, axis=1)
        proc['Year'] = proc.apply(lambda x: x['Receipt Date'].year, axis=1)
        proc['DayofWeek'] = proc.apply(lambda x: x['Receipt Date'].weekday(), axis=1)

        treatment['Month'] = treatment.apply(lambda x: x['Visit Date'].month, axis=1)
        treatment['Year'] = treatment.apply(lambda x: x['Visit Date'].year, axis=1)
        treatment['DayofWeek'] = treatment.apply(lambda x: x['Visit Date'].weekday(), axis=1)

        self.proc = proc
        self.treatment = treatment
        self.centrelist = list(centre['Centre'].unique())

    def tpconversionanalysis(self,centrelist=[],grplist = []):
        if not centrelist:
            centrelist = self.centrelist
        df = self.treatment[self.treatment['Centre'].isin(centrelist)]
        if not grplist:
            grplist = ['Year','Month','Region']
        grpdf = pd.pivot_table(df,index=grplist,values=["Estimate","Reg.No"], columns = ['Converted'],aggfunc = {"Estimate": pd.np.sum, "Reg.No": lambda x: len(list(set(x)))}, fill_value = 0, margins = True).reset_index()
        self.treatpivot = grpdf
        return grpdf

    def procanalysis(self,centrelist=[],grplist = []):
        if not centrelist:
            centrelist = self.centrelist
        df = self.proc[self.proc['Centre'].isin(centrelist)]
        if not grplist:
            grplist = ['Year','Month','Region']
        grpdf = pd.pivot_table(df,index=grplist,values=["Received","Reg.No"], aggfunc = {"Received": pd.np.sum, "Reg.No": lambda x: len(list(set(x)))}, fill_value = 0, margins = True).reset_index()
        grpdf = grpdf[grpdf['Received']>0]
        grpdf['Received'] = grpdf.apply(lambda x: np.round(x['Received']*1.0/1e5,0),axis=1)
        return grpdf
