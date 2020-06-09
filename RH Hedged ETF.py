
"""
Created on Mon Jun  1 21:11:53 2020

@author: Eric Dudgeon
"""
import requests, json
import numpy as np
import pandas as pd
import os
import sys
import alpaca_trade_api as tradeapi
import time
from datetime import datetime

api_key = "PKUHS2CISSH3TCD24QKG"
seceret_key = "j0WvbZJkSqg/eLVosPmSyy7URzU6QkLWGAvU298X"
alpha_key = "TVZTEH37YN9NVTJP"
base_url = "https://paper-api.alpaca.markets"
headers = {'APCA-API-KEY-ID':api_key,"APCA-API-SECRET-KEY":seceret_key}
account_url = "{}/v2/account".format(base_url)
orders_url = "{}/v2/orders".format(base_url)
positions_url = "{}/v2/positions".format(base_url)

def simple_order(symbol, qty, side, type, time_in_force):
    data = {
        "symbol":symbol,
        "qty":qty,
        "side":side,
        "type":type,
        "time_in_force":time_in_force
    }
    r = requests.post(orders_url,json=data,headers=headers)
    return json.loads(r.content)

def get_account():
    r = requests.get(account_url,headers=headers)
    return json.loads(r.content)
### get standard deviation/Variance data
TQQQ_prices =[]
TMF_prices = []
EDZ_prices = []

def std_data(symbol,lists):
    alpha_data = pd.read_json(r"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="+symbol+"&apikey=alpha_key")
    data = alpha_data.iloc[5:20]
    data = data["Time Series (Daily)"]
    for a,b in data.items():
        lists.append(float(b["1. open"]))

std_data("TQQQ",TQQQ_prices)
std_data("TMF",TMF_prices)
std_data("EDZ",EDZ_prices)

### get annual TQQQ price MAX
annual_data = []
TQQQ_full_data = pd.read_json(r"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=TQQQ&outputsize=full&apikey=alpha_key")
data = TQQQ_full_data.iloc[5:257]
data = data["Time Series (Daily)"]
for a,b in data.items():
    annual_data.append(float(b["4. close"]))
annual_max = float(max(annual_data))

### get current prices
def get_current_price(symbol):
    price = pd.read_json(r"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol="+symbol+"&interval=1min&apikey=alpha_key")
    price = price.iloc[6]
    price = price["Time Series (1min)"]
    current_price = float(price["1. open"])
    return current_price 

TQQQ_current = get_current_price("TQQQ")
TMF_current = get_current_price("TMF")
EDZ_current = get_current_price("EDZ")


### get variance for prices
def variance(p):
    p = p[::-1]
    p = pd.Series(p)
    p = p.pct_change()[1:15].std()**2
    return p

TQQQ_variance = variance(TQQQ_prices)
TMF_variance = variance(TMF_prices)
EDZ_variance = variance(EDZ_prices)

### calculate rebalnce Weights
symbols = ([
    ['TQQQ', 0.5],
    ['TMF', 0.25],
    ['EDZ',0.25],
])

wt = {}
for ticker,weight in symbols:
    if ticker =='TQQQ':
        wt[ticker] = (weight*(annual_max/TQQQ_current)/TQQQ_variance)
    elif ticker =="TMF":
        wt[ticker] = (weight/TMF_variance)
    else:
        wt[ticker] = (weight/EDZ_variance)

total_wt = sum([wt[x] for x in wt])

for ticker, weight in wt.items():
    wt[ticker] = weight/total_wt 
    
weights_list = list(map(list, wt.items()))
print(weights_list)


### REBALANCE PORTFOLIO ###
#get current positions

def get_positions():
    p = requests.get(positions_url,headers=headers)
    return json.loads(p.content)

pos = get_positions()
pos = pd.Series(pos)
positions_dict = {}
for a,b in pos.items():
    sym = b["symbol"]
    value = b["market_value"]
    positions_dict[sym] = float(value)
total_pos_wt = sum([positions_dict[x] for x in positions_dict])
for ticker, weight in positions_dict.items():
    positions_dict[ticker] = weight/total_pos_wt   
print(postions_dict)
    
#get current cash on hand

cash = get_account()["cash"]
cash = float(cash)

#calculate weight changes needed for rebalance

r_dict = {}
for ticker, weight in wt.items():
    target = weight - positions_dict[ticker]
    r_dict[ticker] = target
print(r_dict)

#calculate shares to sell or buy

port_value = get_account()["portfolio_value"]
calc_value = float(port_value) - float(cash)

TQQQ_shares = round((r_dict["TQQQ"] * calc_value)/TQQQ_current)
TMF_shares = round((r_dict["TMF"] * calc_value)/TMF_current)
EDZ_shares = round((r_dict["EDZ"] * calc_value)/EDZ_current)

#sell shares
if TQQQ_shares < 0:
    TQQQ_shares = abs(TQQQ_shares)
    simple_order("TQQQ",TQQQ_shares,"sell","market","gtc")
if TMF_shares < 0:
    TMF_shares = abs(TMF_shares)
    simple_order("TMF",TMF_shares,"sell","market","gtc")
if EDZ_shares < 0:
    EDZ_shares = abs(EDZ_shares)
    simple_order("EDZ",EDZ_shares,"sell","market","gtc")
    
#buy shares
    
if TQQQ_shares > 0:
    simple_order("TQQQ",TQQQ_shares,"buy","market","gtc")
if TMF_shares > 0:
    simple_order("TMF",TMF_shares,"buy","market","gtc")
if EDZ_shares > 0:
    simple_order("EDZ",EDZ_shares,"buy","market","gtc")

#### Notes / Exceptions needing to be handled
### if account doesnt have enough cash for an order
### when live trading 3% cash will probably be needed for trading
### If no initial postions or if other positions are present 
### currently ONLY supports postions in TQQQ,TMF,EDZ for paper trading