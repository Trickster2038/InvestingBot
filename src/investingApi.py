import investpy

gPapersTypes = {'indices':'Индексы', 'stocks':'Акции', 'cryptos':'Крипто', 'currencies':'Валюты'}

def get_paper_info(ticker):
    search_result = investpy.search_quotes(text=ticker, n_results=1)
    s = ''
    s += 'Название: ' + (search_result.name or 'None')  + '\n'
    s += 'Тикер: ' + (search_result.symbol or 'None') + '\n'
    s += 'Страна: ' + (search_result.country or 'None') + '\n'
    s += 'Тип: ' + (gPapersTypes[search_result.pair_type] or None) + '\n'
    s += 'Биржа: ' + (search_result.exchange or 'None') + '\n'
    info = search_result.retrieve_information()
    s += 'Дневной диапазон: ' + (info['dailyRange'] or 'None') + '\n'
    s += 'Недельный диапазон: ' + (info['weekRange'] or 'None') + '\n'
    s += 'Годовое изменение: ' + (info['oneYearReturn'] or 'None') + '\n\n'

    s += 'Покупка vs Продажа (всего)\n'
    k = get_tech_analyses(ticker, 'daily')
    s += 'День: ' + '{} vs {} ({})'.format(k[0], k[1], k[2]) + '\n'
    k = get_tech_analyses(ticker, 'weekly')
    s += 'Неделя: ' + '{} vs {} ({})'.format(k[0], k[1], k[2]) + '\n'
    k = get_tech_analyses(ticker, 'monthly')
    s += 'Месяц: ' + '{} vs {} ({})'.format(k[0], k[1], k[2]) + '\n\n'
    return s

def get_papers_overall(tickers):
    s = ''
    for x in tickers:
        search_result = investpy.search_quotes(text=x, n_results=1)
        recent_data = search_result.retrieve_recent_data()
        change = recent_data[-1:]["Change Pct"].array[0]
        if change > 0:
            change = '+' + str(change) 
        name = (search_result.name or 'None')
        symbol = (search_result.symbol or 'None')
        s += '*{} ({})*\n'.format(name, symbol)
        s += 'Дневное изменение: {}%\n'.format(change)
        info = search_result.retrieve_information()
        s += 'Дневной диапазон: ' + (info['dailyRange'] or 'None') + '\n'
        s += 'Недельный диапазон: ' + (info['weekRange'] or 'None') + '\n'
        s += 'Годовое изменение: ' + (info['oneYearReturn'] or 'None') + '\n\n'
    return s

def get_tech_analyses(ticker, inter):
    search_result = investpy.search_quotes(text=ticker, n_results=1)
    technical_indicators = search_result.retrieve_technical_indicators(interval=inter)
    signals = technical_indicators['signal'].array
    buy = 0
    sell = 0
    for x in signals:
        if x == 'buy':
            buy += 1
        if x == 'sell':
            sell += 1
    return [buy, sell, len(signals)]

def get_tech_overall(tickers):
    s = 'Покупка vs Продажа (всего)\n\n'
    for x in tickers:
        search_result = investpy.search_quotes(text=x, n_results=1)
        name = (search_result.name or 'None')
        symbol = (search_result.symbol or 'None')
        s += '*{} ({})*\n'.format(name, symbol)

        k = get_tech_analyses(x, 'daily')
        s += 'День: ' + '{} vs {} ({})'.format(k[0], k[1], k[2]) + '\n'
        k = get_tech_analyses(x, 'weekly')
        s += 'Неделя: ' + '{} vs {} ({})'.format(k[0], k[1], k[2]) + '\n'
        k = get_tech_analyses(x, 'monthly')
        s += 'Месяц: ' + '{} vs {} ({})'.format(k[0], k[1], k[2]) + '\n\n'
    return s