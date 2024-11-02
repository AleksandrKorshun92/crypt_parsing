""" Модуль реализует API с использованием фреймворка FastAPI для взаимодействия с базой данных SQLite. 
API — предоставление информации о данных валют в разных временных интервалах. 

Импортированные модули:
- fastapi: Основной фреймворк для создания API.
- Query: Используется для аннотаций параметров запроса.
- sqlite3: Стандартный модуль Python для работы с базами данных SQLite.
- uvicorn: Веб-сервер ASGI, необходимый для запуска приложения FastAPI.
- logging: Модуль для логирования. 
"""


from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
import sqlite3 as sq
import uvicorn
import logging

# устанавливаем константу названием файла базы данных
DATABASE = 'prices.db'

# Настройка логгирования. Данные хранятся в файле api.log с уровнем логирования INFO. 
logging.basicConfig(
    filename='api.log',  
    level=logging.INFO,  
    format='%(asctime)s - %(levelname)s - %(message)s', 
)


# Создание экземпляра приложения FastAPI
app = FastAPI()

async def create_connection_db():
    """ Функция устанавливает соединение с базой данных. 
    sq.Row позволяет обращаться к полям базы данных по имени."""
   
    db = sq.connect(DATABASE)
    db.row_factory = sq.Row
    return db
 
# Маршрут /prices - вид тикер (валюты) 
@app.get("/prices")
async def get_all_prices(ticker: str = Query(...)):
    """ Метод GET возвращает все данные по валюте в виде списка словарей, 
    содержащих id, тикер, цену и временную метку."""
        
    try:
        logging.info("connection_db ")
        db = await create_connection_db() # подключение к базе данных
        cur = db.cursor()
        prices = cur.execute("SELECT * FROM prices WHERE ticker_usd == '{}' ".format(ticker)).fetchall()
        db.close()
        if prices:
            return [{"id": price['prices_id'], "ticker_usd": price['ticker_usd'], "price": price['price'],\
                "timestamp": price['timestamp']} for price in prices]
        else:
            logging.warning('Error entering currency name')
            return JSONResponse(
            content={"message": "Error entering currency name"},
            )
    except HTTPException as e:
        logging.warning(e)
        return JSONResponse(
            status_code=404,
            content={"message": "Resource not found"},
        )
    
# Маршрут /prices/latest - вид тикер (валюты) 
@app.get("/prices/latest")
async def get_latest_price(ticker: str = Query(...)):
    """ Метод GET возвращает последние данные по валюте"""
    
    try:
        logging.info("connection_db ")
        db = await create_connection_db() # подключение к базе данных
        cur = db.cursor()
        
        prices = cur.execute("SELECT * FROM prices WHERE ticker_usd == '{}' \
            ORDER BY timestamp DESC LIMIT 1".format(ticker)).fetchone()
        db.close()
        if prices:    
            return {"id": prices['prices_id'],"ticker_usd": prices['ticker_usd'], "price": prices['price'], \
                "timestamp": prices['timestamp']} if prices else {}
        else:
            logging.warning('Error entering currency name')
            return JSONResponse(
            content={"message": "Error entering currency name"},
            )
    except HTTPException as e:
        logging.warning(e)
        return JSONResponse(
            status_code=404,
            content={"message": "Resource not found"},
        )
          
        
# Маршрут /prices/date - вид тикер (валюты), начальная дата и конечная дата. Дата в формате Unix
@app.get("/prices/date")
async def get_price_by_date(ticker: str = Query(...), start_date: int = Query(...), end_date: int = Query(...)):
    """ Метод GET возвращает все данные по валюте за определенный промежуток времени 
    в виде списка словарей, содержащих id, тикер, цену и временную метку."""
    
    try:
        logging.info("connection_db ")
        db = await create_connection_db() # подключение к базе данных
        cur = db.cursor()

        prices = cur.execute(
        "SELECT * FROM prices WHERE ticker_usd == '{}' AND timestamp BETWEEN '{}' AND '{}' \
        ".format(ticker, start_date, end_date)).fetchall()
        db.close()
        if prices:
            return [{"id": price['prices_id'], "ticker_usd": price['ticker_usd'], "price": price['price'], \
                "timestamp": price['timestamp']} for price in prices]
        else:
            logging.warning('Error entering currency name or date')
            return JSONResponse( 
                content={"message": "Error entering currency name or date (format - Unix)"},
                )
    except HTTPException as e:
        logging.warning(e)
        return JSONResponse(
            status_code=404,
            content={"message": "Resource not found"},
        )
    
    
if __name__ == "__main__":
    
    # запуск API с через порт 5000
    uvicorn.run(app, host="127.0.0.1", port=5000) 
    