
import pandas as pd
import datetime
def print_hi():
    df = pd.read_csv("orb_trades.csv")
    pnl = list(df['pnl'])
    positive = 0
    negative = 0
    for i in pnl:
        if i>0:
            positive+=i
        if i<0:
            negative+=i
    print(positive,negative,df['pnl'].sum())












if __name__ == '__main__':
    print_hi()