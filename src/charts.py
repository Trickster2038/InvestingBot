import matplotlib.pyplot as plt
# from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mpl_dates
import pandas as pd

def simple_chart(dframe):
    plt.clf()
    df = dframe
    df['Date'] = df.index 

    ax = plt.gca()
    df.plot(kind='line',x='Date',y='Open', color='blue', ax=ax)
    plt.style.use('classic')
    plt.xlabel('Дата')
    plt.ylabel('Цена при открытии')
    plt.title('Цена актива')
    # m = df['Open'].min()
    # m = [m]*len(df['Open'])
    plt.grid(color='grey', linestyle=':', linewidth=1)
    ax.grid(True)
    # plt.fill_between(df['Date'], df['Open'], m, color='#e5eff4')
    return plt