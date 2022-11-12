# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# -*- coding: utf-8 -*-
"""
Created on Sun Apr  3 19:53:59 2022
@author: neera
"""
import requests
import datetime
import json
import pandas as pd

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=730)
    end_timestamp = str(int(datetime.datetime.timestamp(end_date))) + "000"
    start_timestamp = str(int(datetime.datetime.timestamp(start_date))) + "000"

    url = "https://api.upstox.com/historical/v2/NSE_EQ/3045/1?start_timestamp=" + start_timestamp + "&end_timestamp=" + end_timestamp

    d = requests.get(url)
    djson = json.loads(d.text)

    for i in range(len(djson['data'])):
        djson['data'][i] = djson['data'][i].replace(",", " ").split()

    df = pd.DataFrame(djson['data'], columns=['datetime', "open", "high", "low", "close", "volume"])
    df = df.apply(pd.to_numeric)
    df['datetime'] = pd.to_datetime(df['datetime'], unit="ms")
    df['datetime'] = df['datetime'].dt.tz_localize('utc').dt.tz_convert("Asia/Kolkata")
    df['datetime'] = df['datetime'].dt.tz_localize(None)

    df.to_csv("sbin.csv", index=False)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
