import pandas as pd
from sklearn.linear_model import LinearRegression
import time


def CalcBeta(dataFrame):
  nifty = pd.read_csv("NIFTY50.csv")
  auto = pd.read_csv("^CNXAUTO.csv").sort_values(by = ["Close"],ascending=False,ignore_index=True)
  nifty.rename(columns = {" Close":"Nifty"},inplace = True)
  auto.rename(columns = {"Close":"AutoNifty"},inplace = True)
  closings = pd.concat([dataFrame["Date"],nifty["Nifty"],auto["AutoNifty"],dataFrame["Close"]],axis = "columns")
  print("\n")
  print("Closing prices of stock with Nifty and Nifty Auto")
  print(closings.head())
  closings.dropna(inplace = True)
  NiftyRet = []
  StockRet = []
  AutoRet = []
  #produce a 2 year weekly analysis
  for week in range(104,0,-1):
    NiftyRet.append((nifty.Nifty[(week-1)*7] - nifty.Nifty[week*7]) * 100/nifty.Nifty[week*7])
    AutoRet.append((auto.AutoNifty[(week-1)*7] - auto.AutoNifty[week*7]) * 100/auto.AutoNifty[week*7])
    StockRet.append((dataFrame.Close[(week-1)*7] - dataFrame.Close[week*7]) * 100/dataFrame.Close[week*7])
  mapping = {"NiftyReturns":[],"AutoNiftyReturns":[],"StockReturns":[]}
  for week in range(0,103):
    mapping["NiftyReturns"].append(NiftyRet[week])
    mapping["StockReturns"].append(StockRet[week])
    mapping["AutoNiftyReturns"].append(AutoRet[week])
  dataFrame = pd.DataFrame(mapping)
  X = dataFrame[["NiftyReturns"]]
  linearModel = LinearRegression()
  linearModel.fit(X,dataFrame["StockReturns"])
  print()
  niftyBeta = round(linearModel.coef_[0],3)
  print("Beta value with regards to Nifty Index",niftyBeta)
  X = dataFrame[["AutoNiftyReturns"]]
  linearModel.fit(X,dataFrame["StockReturns"])
  auto = round(linearModel.coef_[0],3)
  print("Beta values with regards to Auto Nifty Index",auto)
  if (niftyBeta+auto)/2 < 0:
    print("Stock performs opposite to market")
  elif (niftyBeta + auto)/2 < 1:
    print("Stock moves slower than the market in the same direction")
  else:
    print("Stock moves faster than the market in the same direction")
  print("\n")

#Simple Moving averages
def MovingAvg(dataFrame,days):
  Close = dataFrame.Close
  avgDay = sum(Close[0:days])/days
  lastClosePrice = Close[0]
  if lastClosePrice>avgDay:
    return f'Simple Moving average ' + str(days) + ': BUY'
  else:
    return f'Simple Moving average ' + str(days) + ': SELL'
  

#exponential moving averages
def ExponenAvg(dataFrame,days):
  multiplier = 2/(days + 1)
  Close = dataFrame.Close
  lastClosePrice = Close[0]
  #use simple moving avg as the first EMA
  #SMA from day = days to 2*days
  EMA = sum(Close[days:2*days])/days
  #loop to find EMA
  for closePrice in Close[0:days][::-1]:
    EMA = closePrice * multiplier + EMA * (1 - multiplier)
  if lastClosePrice > EMA:
    return f'Exponential Moving average ' + str(days) + ': BUY'
  else:
    return f'Exponential Moving average ' + str(days) + ': SELL'


def RSIIndex(dataFrame):
  gainPerc = 0
  lossPerc = 0
  Close = dataFrame.Close
  prevPrice = Close[14]
  #start with average gain and loss
  for closePrice in Close[0:14][::-1]:
    if prevPrice < closePrice:
      gainPerc += ((closePrice-prevPrice)/prevPrice)*100
    else:
      lossPerc += abs(((closePrice-prevPrice)/prevPrice))*100
    prevPrice = closePrice
  #calculate WENDORF Relative Strength
  #average gain and loss
  gain = gainPerc/14
  loss = lossPerc/14
  prevPrice = Close[14]
  for closePrice in Close[0:14][::-1]:
      diff = ((closePrice - prevPrice)/prevPrice)*100
      gain = (gain * 13 + diff)/14
      loss = (loss * 13 + abs(diff))/14
  rsi = 100 - (100/(1 + gain/loss))
  if rsi < 30:
    return f'RSI ' + str(rsi) + ' : BUY'
  elif rsi > 70:
    return f'RSI ' + str(rsi) + ' : SELL'
  else:
    return f'RSI ' + str(rsi) + ' : HOLD'


print("Computing Analysis for NSE:TATAMOTORS..")
print("(As of date 21.06.2024)")
time.sleep(3)
#create a dataframe for the stock to be analysed using indicator and sort on date basis
dataFrame = pd.read_csv("TATAMOTORS.csv").sort_values(by=["Date"],ascending=False,ignore_index=True)
CalcBeta(dataFrame)
avgs = [20,50,100,200]
print("Averages")
for day in avgs:
  print(MovingAvg(dataFrame,day))
for day in avgs:
  print(ExponenAvg(dataFrame,day))
print()
print(RSIIndex(dataFrame))
