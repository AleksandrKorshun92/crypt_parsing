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
import logging


# Настройка логгирования. Данные хранятся в файле api.log с уровнем логирования INFO. 
logging.basicConfig(
    filename = 'client.log',  
    level = logging.INFO,  
    format = '%(asctime)s - %(levelname)s - %(message)s', 
)


# устанавливаем константу с видами тикеров в формате tuple
USD = ("btc_usd", "eth_usd")
# устанавливаем константу с адресом URL для запроса данных
URL = "https://www.deribit.com/api/v2/public/get_index_price?index_name="
# устанавливаем константу названием файла базы данных
DATABASE = 'prices.db'


# Создаем соединение с БД
db = sq.connect(DATABASE)
cur = db.cursor()

# Создаем таблицы 
cur.execute('''
    CREATE TABLE IF NOT EXISTS prices (
        prices_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker_usd TEXT,
        price DECIMAL,
        timestamp INTEGER)
    ''')
db.commit()


async def receiving_price(session, currency: str):
    """ Асинхронная функция, которая отправляет GET-запрос к API Deribit для получения текущей цены криптовалюты. 
    Функция принимает вид валюты и возвращает цену.
    
    :param currency: Название валюты (тикер).
    :return: данные по валюте.
    """
    
    url = f"{URL}{currency}"
    try:
        async with session.get(url) as response:
            price = await response.json()
            return price['result']['index_price']
    except aiohttp.ClientError as e:
        logging.error(f"Ошибка при получении цены для {currency}: {e}")


async def save_price_db(price: float, ticker_usd:str): 
    """ Асинхронная функция сохраняет полученные данные о цене в таблицу prices базы данных SQLite. 
    База данных включает id, тикер (валюту), цену и дату со временем в формате Unix
    
    :param price: данные по цене валюты.
    :param ticker_usd: Название валюты (тикер).
    :return: сохраняет в базе данных данные по фалюте
    """
    
    
    try:
        # перевод текущего времени в формат Unix
        unix_timestamp = int(datetime.now().timestamp())
        cur.execute("INSERT INTO prices(ticker_usd, price,timestamp) VALUES(?, ?, ?)",(ticker_usd,price,unix_timestamp))
        db.commit()
    except sq.OperationalError as e:
        logging.warning(f"Операционная ошибка базы данных: {e}")
    except Exception as e:
        logging.exception(f"Произошла непредвиденная ошибка: {e}")


async def main():
    """ Основная асинхронная функция которая в бесконечном цикле каждые 60 секунд получает 
    актуальные цены по заданным данным валют, после чего вызывает функцию save_price_db и 
    запысвает полученные данные в базу данных. 
    """
    
    async with aiohttp.ClientSession() as session:
        while True:
            logging.info("start parsing")
            btc_price = await receiving_price(session, USD[0])
            eth_price = await receiving_price(session, USD[1])

            await save_price_db(btc_price, USD[0])
            await save_price_db(eth_price, USD[1])

            # функция обновляется (засыпает) каждые 60 секунд
            await asyncio.sleep(60)  
    
    
    # закрываем базу данных
    db.close()


if __name__ == "__main__":
    
    # производит запуск 
    asyncio.run(main())
