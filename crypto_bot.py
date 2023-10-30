import logging
import asyncio
import requests
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types, filters 
from aiogram.dispatcher.filters.state import State, StatesGroup
from time import sleep
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton

from pymongo_get_database import get_database
from secret import COLLECTION_NAME_SECRET, BOT_TOKEN_SECRET

dbname = get_database()
collection_name = dbname[COLLECTION_NAME_SECRET]


#import nest_asyncio
#nest_asyncio.apply()

logging.basicConfig(level=logging.INFO)
bot = Bot(token = BOT_TOKEN_SECRET)
storage = MemoryStorage()
dp = Dispatcher(bot, storage = storage)

'''
class UserState(StatesGroup):
    ADDED = State()
    DELETED = State()
'''
# list https://api.coingecko.com/api/v3/coins/list/
COINS = ['bitcoin', 'ethereum', 'binancecoin', 'ripple', 'solana', 'cardano', 'dogecoin', 'tron', 'litecoin', 'polkadot']
#COINS = ['bitcoin', 'ethereum']


async def notification(changes,tick_interval):
    string = f'<b>За последние {tick_interval}</b> \n'
    for i in changes:
        tiker = i.replace('USDT','')#получаем например тикер BTC из пары BTCUSDT
        if changes[i] >= 0:
            string = string + f'{tiker} рост {changes[i]}% \n'
        else:
            string = string + f'{tiker} падение {changes[i]}% \n'
    docs = collection_name.find()
    for i in docs:
        await bot.send_message(i['chat_id'],string,parse_mode='HTML')

@dp.message_handler(commands=['course'])   
async def course (message: types.Message):
    url_start = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids='
    url_mid = '' #переменная для списка криптовалют в строке адреса
    url_end = '&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=1h%2C24h%2C7d&locale=en'
    for coin in COINS:
        url_mid += coin + '%2C'
    url = url_start + url_mid + url_end
    #url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin%2Cethereum&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=1h%2C24h%2C7d&locale=en'
    course_now = requests.get(url).json()

    
    course_2d_list = []
    string = '<b>Тикер | Цена | Час | День | Неделя</b>\n'
    #string = '**Тикер Цена Час День Неделя**\n'
    
    
    
    for i in range(len(COINS)):
        course_2d_list.append([])
        tiker = course_now[i]['symbol']
        tiker = tiker.upper() #перевод в заглавные буквы
        course_2d_list[i].append(tiker)
        price = str(course_now[i]['current_price'])
        price = price[:6]   #оставляем от цены первые 6 символов
        course_2d_list[i].append(price)
        day = round(course_now[i]['price_change_percentage_1h_in_currency'],2) #округляем процент изменения цены до двух знаков после запятой
        hour = round(course_now[i]['price_change_percentage_24h_in_currency'],2)
        week = round(course_now[i]['price_change_percentage_7d_in_currency'],2)
        if day >= 0:
            day = '+' + str(day)
        if hour >= 0:
            hour = '+' + str(hour)
        if week >= 0:
            week = '+' + str(week)
        course_2d_list[i].append(day)
        course_2d_list[i].append(hour)
        course_2d_list[i].append(week)
        
        
        
        string = string + '<b>' + str(course_2d_list[i][0]) + '</b>   ' + str(course_2d_list[i][1]) + '$    ' + str(course_2d_list[i][2]) + '% | ' + str(course_2d_list[i][3]) + '% | ' + str(course_2d_list[i][4]) + '%\n'
    
    
    
    #string = str(a1) + ' ' + str(a2) + ' ' + str(a3) + ' ' + str(a4) + ' ' + str(a5) + '\n' + str(b1) + ' ' + str(b2) + ' ' + str(b3) + ' ' + str(b4) + ' ' + str(b5) + '\n'
    await message.answer(string, parse_mode='HTML')

#---------------------------------SUBSCRIBE----------------------------------------------
@dp.message_handler(commands = ['subscribe'])
async def subscribe(message: types.Message):
    msg = 'Уверены, что хотите подписаться на уведомления?'
 
    markup = InlineKeyboardMarkup(row_width = 2)
    markup.add(InlineKeyboardButton('YES',callback_data='YES_SUBSCRIBE'))
    markup.add(InlineKeyboardButton('NO',callback_data='NO_SUBSCRIBE'))    
    await message.answer(msg, reply_markup = markup)
    
  
    #chat_id = message.chat.id
    #msg = f'''YOU SUBSCRIBE {data} ADDED!!! CHAT_ID = {chat_id}'''
             
    #await message.answer(msg)


@dp.callback_query_handler(text = 'YES_SUBSCRIBE')
async def callback_inline(callback: types.CallbackQuery):
    
    
    
    #тут код занесения записи о подписке в базу данных 
    
    doc_in_base = {
    "chat_id" : callback.message.chat.id
    }
    already_in_base = collection_name.find_one(doc_in_base)
    if already_in_base != None:
        await callback.message.answer('Вы ранее уже подписались')
    else:
        collection_name.insert_one(doc_in_base)
        await callback.message.answer('Вы успешно подписаны!')
    #await callback.answer('подписанны', show_alert = True)

@dp.callback_query_handler(text = 'NO_SUBSCRIBE')
async def callback_inline(callback: types.CallbackQuery):
    doc_in_base = {
    "chat_id" : callback.message.chat.id
    }
    already_in_base = collection_name.find_one(doc_in_base)
    if already_in_base != None:
        await callback.message.answer('конечно нет, Вы же ранее уже подписались')
    else:
        await callback.message.answer('очень жаль :(')


#---------------------------------UNSUBSCRIBE----------------------------------------------
@dp.message_handler(commands = ['unsubscribe'])
async def subscribe(message: types.Message):
    msg = 'Уверены, что хотите отписаться от уведомлений?'
 
    markup = InlineKeyboardMarkup(row_width = 2)
    markup.add(InlineKeyboardButton('YES',callback_data='YES_UNSUBSCRIBE'))
    markup.add(InlineKeyboardButton('NO',callback_data='NO_UNSUBSCRIBE'))    
    await message.answer(msg, reply_markup = markup)
    

@dp.callback_query_handler(text = 'YES_UNSUBSCRIBE')
async def callback_inline(callback: types.CallbackQuery):
        
    #тут код удаления записи о подписке из базы данных 
    
    doc_in_base = {
    "chat_id" : callback.message.chat.id
    }
    already_in_base = collection_name.find_one(doc_in_base)
    if already_in_base != None:
        collection_name.delete_one(doc_in_base)
        await callback.message.answer('подписка отменена!')
    else:
        await callback.message.answer('А вы и так не подписаны')

@dp.callback_query_handler(text = 'NO_UNSUBSCRIBE')
async def callback_inline(callback: types.CallbackQuery):
    doc_in_base = {
    "chat_id" : callback.message.chat.id
    }
    already_in_base = collection_name.find_one(doc_in_base)
    if already_in_base != None:
        await callback.message.answer('рад что Вы одумались :)')
    else:
        await callback.message.answer('А вы и так не подписаны')
#------------------------------------------------------------------------------    

@dp.message_handler(commands=['help'])
async def help (message: types.Message):
    await message.answer(
        text = '''
            Что может бот:
        /course - узнать цены криптовалют в данный момент и изменения цен за час, день и неделю
        /subscribe - включить уведомления о сильных изменениях цен криптовалют
        /unsubscribe - выключить уведомления
        В данный момент бот работает с криптовалютами: Bitcoin, Ethereum, Binancecoin, Ripple, Solana, Cardano, Dogecoin, Tron, Litecoin, Polkadot
            
        '''
        
        
          )

@dp.message_handler(commands=['start'])
async def help (message: types.Message):
    await message.answer(
        text = '''
            Что может бот:
        /course - узнать цены криптовалют в данный момент и изменения цен за час, день и неделю
        /subscribe - включить уведомления о сильных изменениях цен криптовалют
        /unsubscribe - выключить уведомления
        В данный момент бот работает с криптовалютами: Bitcoin, Ethereum, Binancecoin, Ripple, Solana, Cardano, Dogecoin, Tron, Litecoin, Polkadot
            
        '''
        
        
          )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)