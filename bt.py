import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt


def pivothigh(df):
    """ Function to find the pivot high with alternating pivots or fidning the lowest between two pivots high or vice cersa"""

    pivots =[]
    dates = []
    counter = 0
    lastPivot = 0
    Range = [0,0,0,0,0,0,0,0,0,0]
    daterange = [0,0,0,0,0,0,0,0,0,0]

    for i in df.index:

        currentMax = max(Range,default = 0)
        value=round(df["High"][i],2)

        Range=Range[1:9]
        Range.append (value)
        daterange=daterange[1:9]
        daterange.append(i)

        if currentMax == max(Range , default=0):
            counter = counter + 1
        else:
            counter = 0

        if counter == 5:

            lastPivot=currentMax
            dateloc =Range.index(lastPivot)
            lastDate = daterange[dateloc]
            pivots.append(lastPivot)
            dates.append(lastDate)
            
    return pivots,dates


def pivotlow(df):

    pivots1 =[]
    dates1 = []
    counter = 0
    lastPivot = 0
    Range = [0,0,0,0,0,0,0,0,0,0]
    daterange = [0,0,0,0,0,0,0,0,0,0]

    for i in df.index:

        currentMin = min(Range,default = 0)
        value = round(df["Low"][i],2)

        Range = Range[1:9]
        Range.append (value)
        daterange = daterange[1:9]
        daterange.append(i)

        if currentMin == min(Range ,default=0):
            counter = counter + 1
        else:
            counter = 0

        if counter == 5:

            lastPivot = currentMin
            dateloc = Range.index(lastPivot)
            lastDate = daterange[dateloc]
            pivots1.append(lastPivot)
            dates1.append(lastDate)
            
    return pivots1,dates1



df = pd.read_csv("nfmarch1915min.csv")

df.dropna(inplace=True)
df.reset_index(inplace=True)


##### adding old strategy to perform a backtest

df['BH'] = abs(df['Open'] - df['Close'])
df['CH'] = abs(df['High'] - df['Low'])
df['IC'] = df['BH'] / df['CH'] * 100
df['tiny'] = df['CH'] / df['Open'] * 100

def tinyic(df):
    
    if df['tiny'] < 0.15 and df['IC'] < 50.0:
        return True
    else:
        return False

df["tinyic"] = df.apply(tinyic, axis=1)
df.reset_index(inplace=True)
df = df.drop(['index'],axis=1)

df.loc[df['tinyic'] == True, 'SLB'] = df['Low']*0.999
df.loc[df['tinyic'] == True, 'SLS'] = df['High']*1.001

for i in (df.index):
    print(i)
    if ((df.iloc[i]['Date_Time'][-8:]) == "09:15:00"):
        #print("Cuurent index numer is ",i)
        df.loc[i,'DO'] = df.iloc[i]['Open']

df = df.fillna(method = 'ffill')
df = df.fillna(method = 'bfill')

#####




a,b = pivothigh(df)
c,d = pivotlow(df)

a.pop(0)
b.pop(0)
c.pop(0)
d.pop(0)

#####
""" Code to create spl dataframe that can later be merged to the main data frame """

df2 = pd.DataFrame(list(zip(c,d)),
                   columns=['SPL','id11'])

df2.reset_index(inplace=True)

ls = []
for i in range(len(df2.index)):
    
    z = df["Date_Time"][df2["id11"][i]]
    ls.append(z)
    
df2["Date_Time"] = pd.to_datetime(ls)
df2["Date_Time"]= df2["Date_Time"].astype(str)

#print(df["Date_Time"][df2["id11"][3]])
print((df2.head()))

df3 = pd.merge(left = df,on = "Date_Time", right = df2[['Date_Time','SPL']], how = 'outer')
df3.head()
#####

#####
""" Code to create sph dataframe that can later be merged to the main data frame """

df4 = pd.DataFrame(list(zip(a,b)),
                   columns=['SPH','id11'])

df4.reset_index(inplace=True)

ls = []
for i in range(len(df4.index)):
    
    z = df["Date_Time"][df4["id11"][i]]
    ls.append(z)
    
df4["Date_Time"] = pd.to_datetime(ls)
df4["Date_Time"]= df4["Date_Time"].astype(str)

print(df4.head())

df5 = pd.merge(left = df3,on = "Date_Time", right = df4[['Date_Time','SPH']], how = 'outer')
df = df5
#####


#####
""" 
Code to make the sph and spl alternating 
Need to add another method to make sure the lowest point between 2 pivot is spl 
And the highest point between two pivot lows is sph that makes it permanent 

"""
#first search for a pivot high ::: AT this point there are no pivots 
prev_SPH = 0
prev_SPL= 0
prev_SPH_index = 0
prev_SPL_index = 0
look_for = ''
#df=df.head(100)
for i in df.index:
    
    print(i)
        #traverse row by row
    if(look_for==''):
        
        
                # how to begin - 1st entry
                #print('SPL='+str(df['SPL'][i]))
                #print('SPH='+str(df['SPH'][i]))
        if(str(df['SPL'][i]) == 'nan'):
            
            if(str(df['SPH'][i]) != 'nan'):
                look_for='SPH'
            else:
                look_for='SPL'
                
    print(look_for)
    if(look_for=='SPH'):
                #looking for SPH
                
        if(str(df['SPH'][i]) != 'nan'):       
                #if df['SPH'][i] > prev_SPH:
            prev_SPH=str(df['SPH'][i])
            df.loc[i,'newSPH'] = prev_SPH
            prev_SPH_index=i
            look_for='SPL'
            print(df.loc[i,'newSPH'])
            print('111')
                        #implement check for cases when SPH and SPLare in same row
            if(str(df['SPL'][i]) != 'nan'):       

                prev_SPL=str(df['SPL'][i])
                df.loc[i,'newSPL'] = prev_SPL
                prev_SPL_index=i

                look_for='SPH'
                print(df.loc[i,'newSPL'])
                print('000')
                                
        if(str(df['SPL'][i]) != 'nan'):  
                        
            SPL_int = float(prev_SPL)
            if(df['SPL'][i]  < SPL_int):
                                
                df.loc[prev_SPL_index,'newSPL'] = ''
                prev_SPL=str(df['SPL'][i])
                df.loc[i,'newSPL'] = prev_SPL
                prev_SPL_index=i
                look_for='SPH'

    else:
        
        if(look_for=='SPL'):
                        #looking for SPL
            if(str(df['SPL'][i]) != 'nan'):       
                prev_SPL=str(df['SPL'][i])
                df.loc[i,'newSPL'] = prev_SPL
                prev_SPL_index=i
                look_for='SPH'
                                #print(df['newSPL'][i])
                print(df.loc[i,'newSPL'])
                print('000')
                                #implement check for cases when SPH and SPLare in same row
                if(str(df['SPH'][i]) != 'nan'):       
                    
                    prev_SPH=str(df['SPH'][i])
                    df.loc[i,'newSPH'] = prev_SPH
                    prev_SPH_index=i
                    look_for='SPL'
                    print(df.loc[i,'newSPH'])
                    print('111')

            if(str(df['SPH'][i]) != 'nan'):  
                SPH_int = float(prev_SPH)
                if(df['SPH'][i]  > SPH_int):
                                        
                    df.loc[prev_SPH_index,'newSPH'] = ''
                    prev_SPH=str(df['SPH'][i])
                    df.loc[i,'newSPH'] = prev_SPH
                    prev_SPH_index=i
                    look_for='SPL'


#####

#####
""" NEed to add a functio to plot the pivots if and when necessary"""
#####


#####


#####


#####
""" Trend calculation  """



w = df[df['newSPL'].notnull()].index.tolist() # index for plotting 
a = list(df.newSPL.values)#.dropna(inplace=True)
x = [a for a in a if str(a) != 'nan']


x = [ i for i in x if i.strip() != "" ]
#print(x)
x = [float(i) for i in x]

y = df[df['newSPH'].notnull()].index.tolist()
b = list(df.newSPH.values)
z = [b for b in b if str(b) != 'nan']

z = [ i for i in z if i.strip() != "" ]
#print(z)
z = [float(i) for i in z]

df['Trend'] = np.nan
#w,y are indexes of spl and sph 
lm = max([z,x], key=len)
ls = []
ls1 = []
for i in range(1,len(lm) - 1):
    
    prev = i-1
    
    prma = z[i]
    prma1 = z[prev]
    
    print(prma,prma1)
    
    prmi = x[i]
    prmi1 = x[prev]
    
    print(prmi,prmi1)
    
    if ((prma > prma1) & (prmi > prmi1)):
        
        ls.append(y[i])
        #Break of this pivot high gives a bullish trend 
        print("bullish")
        
    elif((prma < prma1) & (prmi < prmi1)):
        
        ls1.append(w[i])
        print("bearish")

# Need to end this before it reached the index out of range 
#####

df['Trend'] = np.where(df.index.isin(ls),"Bullish", np.nan)
df['Trend1'] = np.where(df.index.isin(ls1), "Bearish",np.nan)



df['Trendz'] = df.Trend + df.Trend1

#df.dropna(inplace=True)
#df.reset_index(inplace=True)

df.loc[df['Trendz'].isin(['Bullishnan']),'Trendz'] = 'Bullish'
df.loc[df['Trendz'].isin(['nanBearish']),'Trendz'] = 'Bearish'
df.loc[df['Trendz'].isin(['nannan']),'Trendz'] = np.nan

#df = df.mask(df=='nan', None).ffill()
df = df.drop(['Volume', 'SPL', 'SPH', 'Trend', 'Trend1', 'level_0'],axis=1)

df['Trendz'] = df['Trendz'].ffill()
print(df[20:40])
#####

#####
# Need to add large pivots also to this code 



#####
tl = []
tl2 = []

count = 0
pos = 0
long_trade_triggered = 0
short_trade_triggered = 0

for index, row in df[1:].iterrows():
    
    previous_row = df.iloc[index-1]
    if pos == 0:
        
        print("No position looking for either long or short")
        
        if ((previous_row['tinyic'] == True) & (previous_row['Trendz'] == "Bullish") & (row['High'] > previous_row['High']*1.001) & (row['High'] > previous_row['DO'])):
            
            print("long")
            pos = 1
            long_trade_triggered = 1
            short_trade_triggered = 0
            tl.append([row['Date_Time'],previous_row['High']*1.001,"BUY"])
   
        elif ((previous_row['tinyic'] == True) & (previous_row['Trendz'] == "Bearish") & (row['Low'] < previous_row['Low']*0.999) & (row['Low'] < previous_row['DO'])):
            
            print("short")
            pos = 1
            short_trade_triggered = 1
            long_trade_triggered = 0
            tl2.append([row['Date_Time'],previous_row['Low']*0.999,"SELL"])
    
    elif ((pos == 1) & (long_trade_triggered == 1)):
        
        print("Looking for SLB or looking for a short")
        
        #if (((row['Close'] < previous_row['SLB']) or (row['Low'] < previous_row['SLB']) or (row['Open'] < previous_row['SLB'])) or (row['minima'] < previous_row['SLB'])):
        if ((row['Close'] < previous_row['SLB']) or (row['Low'] < previous_row['SLB']) or (row['Open'] < previous_row['SLB'])):
        
            print("Exit Buy SL")
            pos = 0 
            long_trade_triggered = 0
            tl2.append([row['Date_Time'],previous_row['SLB'],"SL EXIT"])
            #Tinyic use these value
            
        elif ((previous_row['IC'] < 50) & (row['Low'] < previous_row['Low'] * 0.999)):
            
            print("Exit trail SL")
            pos = 0
            long_trade_triggered = 0
            tl2.append([row['Date_Time'],previous_row['Low'] * 0.999," Trail SL"])

        elif ((previous_row['tinyic'] == True) & (previous_row['Trendz'] == "Bearish") & (row['Low'] < previous_row['Low']*0.999) & (row['Low'] < previous_row['DO'])):
            
            print("short")
            pos = 1
            short_trade_triggered = 1
            long_trade_triggered = 0
            tl2.append([row['Date_Time'],previous_row['Low']*0.999,"SELL"])
            
    
    elif ((pos == 1) and (short_trade_triggered == 1)):
        
        print("Looking for SLS or looking for a long")
        
        if ((row['Close'] > previous_row['SLS'])or (row['Open'] > previous_row['SLS']) or (row['High'] > previous_row['SLS'])):
        
            print("Exit Sell SL")
            pos = 0 
            long_trade_triggered = 0
            tl.append([row['Date_Time'],previous_row['SLS'],"SL EXIT"])
            #Tinyic use these value
            
        elif ((previous_row['IC'] < 50) & (row['High'] > previous_row['High'] * 1.001)):
            
            print("Exit trail SL")
            pos = 0
            long_trade_triggered = 0
            tl.append([row['Date_Time'],previous_row['High'] * 1.001," Trail SL"])

        elif ((previous_row['tinyic'] == True) & (previous_row['Trendz'] == "Bullish") & (row['High'] > previous_row['High'] * 1.001) & (row['High']*1.001 > previous_row['DO'])):
            
            print("long")
            pos = 1
            short_trade_triggered = 0
            long_trade_triggered = 1
            tl2.append([row['Date_Time'],previous_row['High']*1.001,"BUY"])

###
df1 = pd.DataFrame(tl,columns=["Entry_time","Entry_price","Type"])
df2 = pd.DataFrame(tl2,columns=["Exit_time","Exit_price","Exit"])
frames = [df1,df2]
dff = pd.concat(frames,axis=1)

dff.dropna(inplace=True)
dff.reset_index(drop=True,inplace=True)

dff['pnl'] = dff['Exit_price'] - dff['Entry_price']
print(dff['pnl'].max(),dff['pnl'].min())

dff['entry_including_slippage'] = dff['Entry_price'] + (dff['Entry_price']*0.0005)
dff['exit_including_slippage'] = dff['Exit_price'] - (dff['Exit_price']*0.0005)
dff['pnl_including_slippage'] = dff['exit_including_slippage'] - dff['entry_including_slippage'] 

dff['pnl_including_slippage'].cumsum().plot()

####
dff['pnl_including_slippage_cumulative_sum'] = dff['pnl_including_slippage'].cumsum()
print(dff['pnl_including_slippage'].cumsum())

dff['drawdown'] = dff['pnl_including_slippage_cumulative_sum'] - dff['pnl_including_slippage_cumulative_sum'].cummax()
max_drawdown = round(dff['drawdown'].min(),2)
#print("Max dd is",max_drawdown)

dff['recovery'] = 0
for i in range(len(dff)):
    if (dff['drawdown'].iloc[i] < 0):
        dff['recovery'].iloc[i] = dff['recovery'].iloc[i-1] + 1
recovery_trades = dff['recovery'].max()
#print("No of trades to recovery",recovery_trades)

number_of_trading_days_for_this_backtest = (pd.to_datetime(dff.iloc[-1]['Entry_time'][0:10]) - pd.to_datetime(dff.iloc[0]['Entry_time'][0:10]))
#print("No of trading days in the backtest",(number_of_trading_days_for_this_backtest))

trade_log_equity_high = dff[dff['recovery'] == 0]

l = []
n = pd.to_datetime(trade_log_equity_high['Entry_time'])- pd.to_datetime(trade_log_equity_high['Entry_time'].shift())
n.dropna(inplace=True)
n.reset_index(drop=True,inplace=True)
for i in n:
    l.append(int(str(i)[0:2]))
    
print("The number of days in dd is",max(l))


####
#BT metrics
print("The total number of trades are ",len(dff))

oc = df.iloc[-1]['Close'] - df['Open'][0]
print('Nifty buy and hold ',oc)

print("Total points including slippage",dff['pnl_including_slippage'].cumsum()[len(dff)-1])

n = len(dff[dff['pnl_including_slippage']>0])
s = sum(dff[dff['pnl_including_slippage']>0]['pnl_including_slippage'])
avgwin = s/n
print("Average winner ", avgwin)

nn = len(dff[dff['pnl_including_slippage']<0])
ns = sum(dff[dff['pnl_including_slippage'] < 0]['pnl_including_slippage'])
avglos = ns/nn
print("Average loser ",avglos)

print("Max dd is",max_drawdown)

print("No of trades to recovery",recovery_trades)

#print("The number of days in dd is",max(l))

print("No of trading days in the backtest",(number_of_trading_days_for_this_backtest))
    
print("No of winners",len(dff.loc[dff['pnl'] > 0]))

print("No of losers",len(dff.loc[dff['pnl'] < 0]))
