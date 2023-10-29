import os, time
import schedule
import requests
import asyncio
from datetime import datetime

from crypto_bot import notification


market_list = ['BTCUSDT','ETHUSDT','BNBUSDT','XRPUSDT','SOLUSDT','ADAUSDT','DOGEUSDT','TRXUSDT','LTCUSDT','DOTUSDT']

def get_changes(market_list,tick_interval):
    
    tick_limit = '2'
    
    changes = {} #словарь в который попадают скачки или падения цены    
    
    for market in market_list:
        # https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=2
        url = 'https://api.binance.com/api/v3/klines?symbol='+market+'&interval='+tick_interval+'&limit='+tick_limit
        data = requests.get(url).json()
        #получем данные о свечах, начальную цену и конечную
        ratio = float(data[0][4]) / float(data[0][1]) #если больше 1, то цена выросла, если меньше то упала. например 1,003 значит что цена выросла на 0,3%
        ratio_percent = round(((ratio - 1)*100),1)
        if ratio_percent >= 0.5 or ratio_percent <= -0.5: #тут указываем какой процент считать скачком (парог включения в уведомления)
            changes[market] = ratio_percent

    if changes != {}:
        #print(changes)
        asyncio.run(notification(changes, tick_interval))
    else:
        #print('nooo')
        pass
          
        
        
    
    #print('============='+ str(datetime.now()) +'================')
    


      
       

schedule.every(5).minutes.do(get_changes, market_list = market_list, tick_interval='5m')
schedule.every(15).minutes.do(get_changes, market_list = market_list, tick_interval='15m')
schedule.every(30).minutes.do(get_changes, market_list = market_list, tick_interval='30m')
schedule.every(1).hour.do(get_changes, market_list = market_list, tick_interval='1h')
#schedule.every(4).hour.do(get_changes, market_list = market_list, tick_interval='4h')
#schedule.every(15).seconds.do(get_changes, market_list = market_list, tick_interval='6h')
#schedule.every(12).hour.do(get_changes, market_list = market_list, tick_interval='12h')
#schedule.every(15).day.do(get_changes, market_list = market_list, tick_interval='1d')

'''
schedule.every(5).seconds.do(base_downloader)
schedule.every(10).minutes.do(job)
schedule.every().hour.do(job)
schedule.every().day.at("10:30").do(job)
schedule.every().monday.do(job)
schedule.every().wednesday.at("13:15").do(job)
'''


while True:
    schedule.run_pending()
    time.sleep(1)

      
