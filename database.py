import json
import logging
import os
import sqlite3

import redis

import config

class Cache(redis.StrictRedis):
    def __init__(self, host, port, password,
                 charset="utf-8",
                 decode_responses=True):
        super(Cache, self).__init__(host, port,
                                    password=password,
                                    charset=charset,
                                    decode_responses=decode_responses)
        logging.info("Redis start")

    def jset(self, name, value, ex=0):
        """функция конвертирует python-объект в Json и сохранит"""
        r = self.get(name)
        if r is None:
            return r
        return json.loads(r)

    def jget(self, name):
        """функция возвращает Json и конвертирует в python-объект"""
        return json.loads(self.get(name))
        
class Database:
    """ Класс работы с базой данных """
    def __init__(self, name):
        self.name = name
        self._conn = self.connection()
        logging.info("Database connection established")

    def create_db(self):
        connection = sqlite3.connect(f"{self.name}.db")
        logging.info("Database created")
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE users 
                          (id INTEGER PRIMARY KEY,
                           wallets VARCHAR NOT NULL);''')
        connection.commit()
        cursor.close()

    def connection(self):
        db_path = os.path.join(os.getcwd(), f"{self.name}.db")
        if not os.path.exists(db_path):
            self.create_db()
        return sqlite3.connect(f"{self.name}.db")

    def _execute_query(self, query, select=False):
        cursor = self._conn.cursor()
        cursor.execute(query)
        if select:
            records = cursor.fetchone()
            cursor.close()
            return records
        else:
            self._conn.commit()
        cursor.close()

    async def insert_users(self, user_id: int, wallets: str):
        insert_query = f"""INSERT INTO users (id, wallets)
                                       VALUES ({user_id}, "{wallets}")"""
        self._execute_query(insert_query)
        logging.info(f"Leagues for user {user_id} added")

    async def select_users(self, user_id: int):
        select_query = f"""SELECT wallets from wallets 
                           where id = {user_id}"""
        record = self._execute_query(select_query, select=True)
        return record

    async def update_users(self, user_id: int, wallets: str):
        update_query = f"""Update wallets 
                              set wallets = "{wallets}" where id = {user_id}"""
        self._execute_query(update_query)
        logging.info(f"Leagues for user {user_id} updated")

    async def delete_users(self, user_id: int):
        delete_query = f"""DELETE FROM users WHERE id = {user_id}"""
        self._execute_query(delete_query)
        logging.info(f"User {user_id} deleted")

cache = Cache(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    password=config.REDIS_PASSWORD
)
database = Database(config.BOT_DB_NAME)