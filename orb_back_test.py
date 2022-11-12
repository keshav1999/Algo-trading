# -*- coding: utf-8 -*-
"""
Created on Sun Apr  3 22:15:28 2022
@author: neera
"""
import pandas as pd
import datetime
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
if __name__ == '__main__':
    print_hi()