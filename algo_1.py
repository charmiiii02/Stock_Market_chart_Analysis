import pandas as pd
file_name = input("enter file name...")
df = pd.read_csv(file_name)
df.columns=['time', 'open', 'high', 'low', 'close', 'volume']
#Check if NA values are in data
df=df[df['volume']!=0]
df.reset_index(drop=True, inplace=True)
df.isna().sum()
print(df)
def pivotid(df1, l, n1, n2): 
    if l-n1 < 0 or l+n2 >= len(df1):
        return 0
    
    pividlow=1
    pividhigh=1
    for i in range(l-n1, l+n2+1):
        if(df1.low[l]>df1.low[i]):
            pividlow=0
        if(df1.high[l]<df1.high[i]):
            pividhigh=0
    if pividlow and pividhigh:
        return 3
    elif pividlow:
        return 1
    elif pividhigh:
        return 2
    else:
        return 0
    
df['pivot'] = df.apply(lambda x: pivotid(df, x.name,15,15), axis=1)
df['shortpivot'] = df.apply(lambda x: pivotid(df, x.name,5,5), axis=1)
import numpy as np
def pointpos(x):
    if x['pivot']==1:
        return x['low']-1e-3
    elif x['pivot']==2:
        return x['high']+1e-3
    else:
        return np.nan

def shortpointpos(x):
    if x['shortpivot']==1:
        return x['low']-2e-3
    elif x['shortpivot']==2:
        return x['high']+2e-3
    else:
        return np.nan
    
df['pointpos'] = df.apply(lambda row: pointpos(row), axis=1)
df['shortpointpos'] = df.apply(lambda row: shortpointpos(row), axis=1)
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
dfpl = df[15375:15440]
fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                open=dfpl['open'],
                high=dfpl['high'],
                low=dfpl['low'],
                close=dfpl['close'])])

fig.add_scatter(x=dfpl.index, y=dfpl['pointpos'], mode="markers",
                marker=dict(size=5, color="green"),
                name="pivot")
fig.add_scatter(x=dfpl.index, y=dfpl['shortpointpos'], mode="markers",
                marker=dict(size=5, color="red"),
                name="shortpivot")
fig.update_layout(xaxis_rangeslider_visible=False)
fig.show()
from scipy.stats import linregress
backcandles= 14 #!!!should be less than pivot candles
for candleid in range(8000, len(df)-backcandles):
    if df.iloc[candleid].pivot != 2 or df.iloc[candleid].shortpivot != 2:
        continue
    
    maxim = np.array([])
    minim = np.array([])
    xxmin = np.array([])
    xxmax = np.array([])
    minbcount=0 #minimas before head
    maxbcount=0 #maximas before head
    minacount=0 #minimas after head
    maxacount=0 #maximas after head
    
    for i in range(candleid-backcandles, candleid+backcandles):
        if df.iloc[i].shortpivot == 1:
            minim = np.append(minim, df.iloc[i].low)
            xxmin = np.append(xxmin, i) #could be i instead df.iloc[i].name             
            if i < candleid:
                minbcount=+1
            elif i>candleid:
                minacount+=1
        if df.iloc[i].shortpivot == 2:
            maxim = np.append(maxim, df.iloc[i].high)
            xxmax = np.append(xxmax, i) # df.iloc[i].name
            if i < candleid:
                maxbcount+=1
            elif i>candleid:
                maxacount+=1
    
    if minbcount<1 or minacount<1 or maxbcount<1 or maxacount<1:
        continue

    slmin, intercmin, rmin, pmin, semin = linregress(xxmin, minim)
    headidx = np.argmax(maxim, axis=0)
    if maxim[headidx]-maxim[headidx-1]>1.5e-3 and maxim[headidx]-maxim[headidx+1]>1.5e-3 and abs(slmin)<=1e-4 and xxmin[0]>xxmax[headidx-1] and xxmin[1]<xxmax[headidx+1]:# and (maxim[headidx]-maxim[headidx+1])>(maxim[headidx+1]-minim[headidx+1]) and (maxim[headidx]-maxim[headidx-1])>(maxim[headidx-1]-minim[headidx-1]) :
        print(minbcount,minacount,maxbcount,maxacount, slmin, candleid)
        #print(maxim)
        #print(xxmax)
        #print(minim)
        #print(xxmin)
        break
        
    if candleid % 1000 == 0:
        print(candleid)