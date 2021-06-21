import telebot
import investpy
import charts
import datetime
from telebot import types
import os
import db
import investingApi
import dataframe_image as dfi

tg_token = input('Telegram token: ')
db_user = input('DB user: ')
db_pass = input('DB password: ')

bot = telebot.TeleBot(tg_token)
db.connect(db_user, db_pass)
print('Bot initialized')

gPapersTypes = {'indices':'Индексы', 'stocks':'Акции', 'cryptos':'Крипто', 'currencies':'Валюты'}

def log(x):
    print(x)

# @bot.message_handler(commands=["First"])
@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == "/config":
        config(message.from_user.id)
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Список команд: \n\
/star - добавить актив в закладки\n\
/getStars - смотреть список закладок\n")
    elif message.text == "/star":
        set_paper_type(message.from_user.id)
    elif message.text.lower() == "/getstars":
        get_papers(message.from_user.id)
    else:
        bot.send_message(message.from_user.id, "Команда не распознана. Напишите /help.")

@bot.callback_query_handler(func=lambda call: call.data in gPapersTypes.keys())
def callback_worker(call):
    db.update_paper_type(call.from_user.id, call.data)
    input_paper(call.from_user.id)

@bot.callback_query_handler(func=lambda call: call.data[0:3] == '_&_')
def callback_worker(call):
    db.add_paper(call.data[3:].split('|'), call.from_user.id)
    bot.send_message(call.from_user.id, "Актив добавлен в закладки")

@bot.callback_query_handler(func=lambda call: call.data[0:7] == '_paper_')
def callback_worker(call):
    paper = call.data[7:]
    db.update_active_paper(call.from_user.id, paper)
    interact_paper(call.from_user.id)

@bot.callback_query_handler(func=lambda call: call.data == 'delete')
def callback_worker(call):
    confirm_delete(call.from_user.id)

@bot.callback_query_handler(func=lambda call: call.data == 'truly_delete')
def callback_worker(call):
    db.delete_paper(call.from_user.id)
    bot.send_message(call.from_user.id, "Актив удален из закладок")

@bot.callback_query_handler(func=lambda call: call.data == 'no_delete')
def callback_worker(call):
    bot.send_message(call.from_user.id, "Актив cохранен")

@bot.callback_query_handler(func=lambda call: call.data == 'overall')
def callback_worker(call):
    tickers = db.get_tickers(call.from_user.id)
    msg = investingApi.get_papers_overall(tickers)
    bot.send_message(call.from_user.id, text=msg,  parse_mode= 'Markdown')

@bot.callback_query_handler(func=lambda call: call.data == 'stats')
def callback_worker(call):
    get_stats(call.from_user.id)

@bot.callback_query_handler(func=lambda call: call.data == 'info')
def callback_worker(call):
    paper = db.get_active_paper(call.from_user.id)
    msg = investingApi.get_paper_info(paper)
    bot.send_message(call.from_user.id, text=msg)

@bot.callback_query_handler(func=lambda call: call.data == 'tech_overall')
def callback_worker(call):
    tickers = db.get_tickers(call.from_user.id)
    msg = investingApi.get_tech_overall(tickers)
    bot.send_message(call.from_user.id, text=msg, parse_mode= 'Markdown')

@bot.callback_query_handler(func=lambda call: call.data in ['stats_week', 'stats_month'])
def callback_worker(call):
    user_id = call.from_user.id
    ticker = db.get_active_paper(call.from_user.id)
    search_result = investpy.search_quotes(text=ticker, n_results=1)

    recent_data = search_result.retrieve_recent_data()
    df = recent_data.copy()
    del df["High"]
    del df["Low"]
    del df["Volume"]
    df1 = df.copy()
    df.columns = ['Открытие','Закрытие','Изменение, %']
    if call.data == 'stats_week':
        fig = charts.simple_chart(df1[-7:])
        dfi.export(df[-7:],'tables/{}.png'.format(user_id))
    else:
        fig = charts.simple_chart(df1)
        dfi.export(df,'tables/{}.png'.format(user_id))

    fig.savefig('charts/{}.png'.format(user_id), dpi=100)
    img = open('charts/{}.png'.format(user_id), 'rb')
    bot.send_photo(user_id, img)
    img.close()
    os.remove('charts/{}.png'.format(user_id))

    img = open('tables/{}.png'.format(user_id), 'rb')
    bot.send_photo(user_id, img)
    img.close()
    os.remove('tables/{}.png'.format(user_id))

def set_paper_type(user_id):
    keyboard = types.InlineKeyboardMarkup(); 
    for x in gPapersTypes.keys():    
        key = types.InlineKeyboardButton(text=gPapersTypes[x], callback_data=x); 
        keyboard.add(key); 
    question = 'Выберите тип бумаг';
    bot.send_message(user_id, text=question, reply_markup=keyboard)


def input_paper(user_id):
    msg = bot.send_message(user_id, text='Введите название или тикер актива')
    bot.register_next_step_handler(msg, search_paper)

def search_paper(message):
    paperType = db.get_paper_type(message.from_user.id)
    search_result = investpy.search_quotes(text=message.text, products=[paperType], n_results=10)
    keyboard = types.InlineKeyboardMarkup()
    for x in search_result:    
        desription = "{} ({}, {})".format(x.name, x.symbol, x.exchange)
        x.symbol = x.symbol or 'None'
        x.country = x.country or 'None'
        x.pair_type = x.pair_type or 'None'
        key = types.InlineKeyboardButton(text=desription, callback_data= '_&_' + x.symbol + "|" + x.country + "|" + x.pair_type)
        keyboard.add(key)
    question = 'Выберите актив';
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

def get_papers(user_id):
    papers = db.get_papers(user_id) 
    keyboard = types.InlineKeyboardMarkup()
    key = types.InlineKeyboardButton(text='Общая статистика', callback_data = 'overall')
    keyboard.add(key)
    key = types.InlineKeyboardButton(text='Тех. Анализ', callback_data = 'tech_overall')
    keyboard.add(key)
    for x in papers:
        s = x[0] + ' - ' + x[1] + ' - ' + gPapersTypes[x[2]]
        # s = ' - '.join(x)
        key = types.InlineKeyboardButton(text=s, callback_data = '_paper_' + x[0])
        keyboard.add(key)
    question = 'Ваши активы:';
    bot.send_message(user_id, text=question, reply_markup=keyboard)

def interact_paper(user_id):
    keyboard = types.InlineKeyboardMarkup()
    key = types.InlineKeyboardButton(text='Общая информация', callback_data = 'info')
    keyboard.add(key)
    key = types.InlineKeyboardButton(text='Cтатистика', callback_data = 'stats')
    keyboard.add(key)
    key = types.InlineKeyboardButton(text='Удалить', callback_data = 'delete')
    keyboard.add(key)
    question = 'Действие:';
    bot.send_message(user_id, text=question, reply_markup=keyboard)

def confirm_delete(user_id):
    keyboard = types.InlineKeyboardMarkup()
    key = types.InlineKeyboardButton(text='Да', callback_data = 'truly_delete')
    keyboard.add(key)
    key = types.InlineKeyboardButton(text='Нет', callback_data = 'no_delete')
    keyboard.add(key)
    question = 'Действительно удалить актив:';
    bot.send_message(user_id, text=question, reply_markup=keyboard)

def get_stats(user_id):
    keyboard = types.InlineKeyboardMarkup()
    key = types.InlineKeyboardButton(text='Неделя', callback_data = 'stats_week')
    keyboard.add(key)
    key = types.InlineKeyboardButton(text='Месяц', callback_data = 'stats_month')
    keyboard.add(key)
    question = 'Статистика за срок:';
    bot.send_message(user_id, text=question, reply_markup=keyboard)

# bot.polling(none_stop=True)

if __name__ == '__main__':
    i = 0
    n_errors = 0
    while i<1:
        try:
            # i += 1
            bot.polling(none_stop=True)
        except Exception as e:
            n_errors += 1
            # time.sleep(5)
            print(e)
            print('> Errors total: {}'.format(n_errors))