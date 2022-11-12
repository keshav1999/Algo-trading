# -*- coding: utf-8 -*-
"""
"""
import pandas as pd
import datetime
import pandas_ta as ta
import numpy as np

def print_hi():
    df = pd.read_csv("sbin.csv")

    df['datetime'] = pd.to_datetime(df['datetime'])

    df = df.set_index('datetime')

    td = {}
    trades = pd.DataFrame()
    total_trades = 0
    signal = ""

    prevday = False

    for i in range(len(df)):
        dat = df.iloc[i]

        if dat.name.date() != prevday:
            orb = False
            prevday = dat.name.date()
            total_trades = 0

        if orb == False and dat.name.time() == datetime.time(9, 29):
            date_string = dat.name.date().strftime("%Y-%m-%d")
            orb_df = df.loc[date_string + " " + "9:15:00": date_string + " " + "9:29:00"]
            high = orb_df['high'].max()
            low = orb_df['low'].min()
            orb = True

        elif orb == True:
            if signal == "" and total_trades < 3 and dat.name.time() < datetime.time(15, 0):
                if dat['high'] > high:
                    signal = "buy"
                    td = {"buyprice": high, "buytime": dat.name.time(), "date": dat.name.date(), "sl": low,
                          "type": "buy", "quantity": 100}
                    total_trades = total_trades + 1

                if dat['low'] < low:
                    signal = "sell"
                    td = {"sellprice": low, "selltime": dat.name.time(), "date": dat.name.date(), "sl": high,
                          "type": "sell", "quantity": 100}
                    total_trades = total_trades + 1

            if signal == "buy":
                if dat['low'] < td['sl']:
                    td['sellprice'] = td['sl']
                    td['selltime'] = dat.name.time()
                    td['pnl'] = (td['sellprice'] - td['buyprice']) * td['quantity']
                    trades = trades.append(td, ignore_index=True)
                    signal = ""

                if dat.name.time() == datetime.time(15, 15):
                    td['sellprice'] = dat['open']
                    td['selltime'] = dat.name.time()
                    td['pnl'] = (td['sellprice'] - td['buyprice']) * td['quantity']
                    trades = trades.append(td, ignore_index=True)
                    signal = ""

            if signal == "sell":
                if dat['high'] > td['sl']:
                    td['buyprice'] = td['sl']
                    td['buytime'] = dat.name.time()
                    td['pnl'] = (td['sellprice'] - td['buyprice']) * td['quantity']
                    trades = trades.append(td, ignore_index=True)
                    signal = ""

                if dat.name.time() == datetime.time(15, 15):
                    td['buyprice'] = dat['open']
                    td['buytime'] = dat.name.time()
                    td['pnl'] = (td['sellprice'] - td['buyprice']) * td['quantity']
                    trades = trades.append(td, ignore_index=True)
                    signal = ""

    trades.to_csv("orb_trades.csv")

def rsi_ind(df, n):
    rsi = ta.rsi(df['close'], n)
    return rsi
def super_trend(df, l, m):
    supertr = ta.supertrend(high=df['high'], low=df['low'], close=df['close'], length=l, multiplier=float(m))
    return supertr[f'SUPERT_{l}_{float(m)}']
def rsi_backtest():

    df = pd.read_csv("sbin.csv")

    df['datetime'] = pd.to_datetime(df['datetime'])

    df = df.set_index('datetime')

    ohlc_dict = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}

    df = df.resample('5min').agg(ohlc_dict).dropna()





    df['rsi'] = rsi_ind(df, 14)
    df['supertrend'] = super_trend(df, 10, 2)

    df['buy'] = np.where((df["close"] > df['supertrend']) & (df['rsi'] > 60), True, False)
    df['sell'] = np.where((df["close"] < df['supertrend']) & (df['rsi'] < 40), True, False)

    td = {}
    trades = pd.DataFrame()
    signal = ""

    for i in range(len(df)):
        print(i)
        dat = df.iloc[i]

        if signal == "" and dat.name.time() < datetime.time(15, 0):
            if dat['buy'] == True:
                signal = "buy"
                target = dat['close'] + (dat['close'] - dat['supertrend'])
                td = {"buyprice": dat['close'], "buytime": dat.name.time(), "date": dat.name.date(),
                      "sl": dat['supertrend'],
                      "type": "buy", "quantity": 100, "target": target, "pos": "open"}

            if dat['sell'] == True:
                signal = "sell"
                target = dat['close'] - (dat['supertrend'] - dat['close'])
                td = {"sellprice": dat['close'], "selltime": dat.name.time(), "date": dat.name.date(),
                      "sl": dat['supertrend'],
                      "type": "sell", "quantity": 100, "target": target, "pos": "open"}

        if signal == "buy":
            if dat['low'] < td['sl'] and td['pos'] == "open":
                td['pos'] = "closed"
                td['sellprice'] = td['sl']
                td['selltime'] = dat.name.time()
                td['pnl'] = (td['sellprice'] - td['buyprice']) * td['quantity']
                trades = trades.append(td, ignore_index=True)
                signal = ""

            if dat['high'] > td['target'] and td['pos'] == "open":
                td['pos'] = 'closed'
                td['sellprice'] = target
                td['selltime'] = dat.name.time()
                td['pnl'] = (td['sellprice'] - td['buyprice']) * td['quantity']
                trades = trades.append(td, ignore_index=True)
                signal = ""

            if dat.name.time() > datetime.time(15, 15) and td['pos'] == "open":
                td['pos'] = 'closed'
                td['sellprice'] = dat['open']
                td['selltime'] = dat.name.time()
                td['pnl'] = (td['sellprice'] - td['buyprice']) * td['quantity']
                trades = trades.append(td, ignore_index=True)
                signal = ""

            if td['pos'] == "open" and dat['supertrend'] > td['sl']:
                td['sl'] = dat['supertrend']

        if signal == "sell":
            if dat['high'] > td['sl'] and td['pos'] == "open":
                td['pos'] = "closed"
                td['buyprice'] = td['sl']
                td['buytime'] = dat.name.time()
                td['pnl'] = (td['sellprice'] - td['buyprice']) * td['quantity']
                trades = trades.append(td, ignore_index=True)
                signal = ""

            if dat['low'] < td['target'] and td['pos'] == "open":
                td['pos'] = 'closed'
                td['buyprice'] = target
                td['buytime'] = dat.name.time()
                td['pnl'] = (td['sellprice'] - td['buyprice']) * td['quantity']
                trades = trades.append(td, ignore_index=True)
                signal = ""

            if dat.name.time() > datetime.time(15, 15) and td['pos'] == "open":
                td['pos'] = 'closed'
                td['buyprice'] = dat['open']
                td['buytime'] = dat.name.time()
                td['pnl'] = (td['sellprice'] - td['buyprice']) * td['quantity']
                trades = trades.append(td, ignore_index=True)
                signal = ""

            if td['pos'] == "open" and dat['supertrend'] < td['sl']:
                td['sl'] = dat['supertrend']

    trades.to_csv("rsi_super.csv")

if __name__ == '__main__':
    # print_hi()
    rsi_backtest()