# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
### Cronjob needs to run the last Wednesday over each month at noon

### import modules

### Get account

### Get Data

### define S&P Trends

#SPY = <data>
#spy_ma200 = SMA(200)
#spy_ma50 = SMA(50)
#trend_up = spy_ma50 > spy_ma200

###Stock Momentum
#momentum_lookback = 126
#momentum_skip = 10

### Fundamental Analysis Variables 
#cash_return
#fcf_yield
#roic
#ltd_to_eq

####Create Value and Quality Scores
#value = (cash_return + fcf_yield) 
#quality = roic + ltd_to_eq + value

###Creates Momentum factor
#returns_overall
#returns_recent
#momentum = returns_overall.log1p() - returns_recent.log1p()

###filter top quality and momentum - arrive at 20 stocks to buy
#top_quality = top 50 quality of the S&P500
#top_quality_momentum = top 20 mometum of top_quality
#apply trand_up top 20 stocks so the algo will move into bonds if he markets are trending down

###TRADE

### Get current holdings


# Define our rule to open/hold positions
# top momentum and don't open in a downturn but, if held, then keep

### set weighting for stocks equally weighted








