""" 
Модуль предназначен для получения актуальных цен криптовалют с платформы Deribit и 
сохранения этих данных в базе данных SQLite. 

Импортируемые библиотеки:
- asyncio: Асинхронная библиотека Python 
- aiohttp: Библиотека для асинхронного HTTP-клиента (для отправки Api запросов)
- sqlite3: Модуль Python для работы с базами данных SQLite.
- datetime: Модуль для работы со временем и датами
"""

import asyncio
import aiohttp
import sqlite3 as sq
from datetime import datetime

# устанавливаем константу с видами тикеров в формате tuple
USD = ("btc_usd", "eth_usd")
# устанавливаем константу с адресом URL для запроса данных
URL = "https://www.deribit.com/api/v2/public/get_index_price?index_name="
# устанавливаем константу названием файла базы данных
DATABASE = 'prices.db'

async def receiving_price(session, currency: str):
    """ Асинхронная функция, которая отправляет GET-запрос к API Deribit для получения текущей цены криптовалюты. 
    Функция принимает вид валюты и возвращает цену в формате JSON.
    """
    
    url = f"{URL}{currency}"
    try:
        async with session.get(url) as response:
            data = await response.json()
            return data['result']['index_price']
    except Exception as e:
        print(e)


async def save_price_db(data: float, ticker_usd:str): 
    """ Асинхронная функция сохраняет полученные данные о цене в таблицу prices базы данных SQLite. 
    База данных включает id, тикер (валюту), цену и дату со временем в формате Unix"""
    
    db = sq.connect(DATABASE)
    cur = db.cursor()
    
    # перевод текущего времени в формат Unix
    unix_timestamp = int(datetime.now().timestamp())
    cur.execute('CREATE TABLE IF NOT EXISTS prices(prices_id INTEGER PRIMARY KEY AUTOINCREMENT, ticker_usd TEXT, price DECIMAL, timestamp INTEGER)') 
    cur.execute("INSERT INTO prices(ticker_usd, price,timestamp) VALUES('{}', '{}', '{}')".format(ticker_usd,data,unix_timestamp))
    db.commit()
    db.close()  


async def main():
    """ Основная асинхронная функция которая в бесконечном цикле каждые 60 секунд получает актуальные цены по заданным данным валют,
    после чего вызывает функцию save_price_db и запысвает полученные данные в базу данных. 
    """
    
    async with aiohttp.ClientSession() as session:
        while True:
            btc_price = await receiving_price(session, USD[0])
            eth_price = await receiving_price(session, USD[1])

            await save_price_db(btc_price, USD[0])
            await save_price_db(eth_price, USD[1])

            # функция обновляется (засыпает) каждые 60 секунд
            await asyncio.sleep(60)  


if __name__ == "__main__":
    # производит запуск 
    asyncio.run(main())