import datetime
import os
import sqlite3
from typing import Any

from src.tgbot.misc.my_dataclasses import AccessCodeInfo


class DataBase:
    def __init__(self, db_name: str):
        self.DB_NAME = db_name

    def __execute_query(self, query: str, values: tuple = ()) -> list[Any]:
        db_path = os.path.join(os.getcwd(), self.DB_NAME)
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(query, values)
        result = cur.fetchall()
        conn.commit()
        conn.close()
        return result

    def add_wallet(self, chat_id: int, wallet_id: str, wallet_name: str, wallet_type: str, last_event_id):
        self.__execute_query(
            'INSERT INTO wallets (user_id, wallet_id, wallet_name, wallet_type, last_event_id) VALUES (?, ?, ?, ?, ?)',
            (chat_id, wallet_id, wallet_name, wallet_type, last_event_id)
        )

    def delete_user_wallet(self, wallet_id: str, chat_id: int):
        self.__execute_query('DELETE FROM wallets WHERE user_id=? AND wallet_id=?', (chat_id, wallet_id))

    def get_unique_wallets(self):
        return self.__execute_query('SELECT DISTINCT wallet_id, last_event_id FROM wallets')

    def get_send_info(self, wallet_id: str):
        return self.__execute_query(
            'SELECT chat_id, wallet_name FROM users INNER JOIN wallets ON users.chat_id = wallets.user_id WHERE wallet_id = ?',
            (wallet_id,))

    def update_wallet_last_event_id(self, wallet_id: str, last_event_id: str):
        self.__execute_query(
            'UPDATE wallets SET last_event_id = ? WHERE wallet_id = ?', (last_event_id, wallet_id)
        )

    def get_existing_wallet_last_event_id(self, wallet_id: str):
        return self.__execute_query('SELECT last_event_id FROM wallets WHERE wallet_id=?', (wallet_id,))

    def get_user_wallet(self, wallet_id: str, chat_id: int):
        return self.__execute_query(
            'SELECT wallet_id FROM wallets WHERE wallet_id=? AND chat_id=?',
            (wallet_id, chat_id)
        )

    def get_user_wallets(self, chat_id: int):
        return self.__execute_query('SELECT wallet_id, wallet_name FROM wallets WHERE user_id=?', (chat_id,))

    def add_user(self, chat_id: int, username: str, status: str, time_of_expiry: int):
        self.__execute_query(
            'INSERT INTO users (chat_id, username, status, time_of_expiry) VALUES (?, ?, ?, ?)',
            (chat_id, username, status, time_of_expiry)
        )

    def get_users(self):
        return self.__execute_query('SELECT chat_id, username, status FROM users')

    def delete_user(self, chat_id: str | int):
        self.__execute_query('DELETE FROM users WHERE chat_id = ?', (chat_id,))

    def get_users_id(self):
        timestamp = int(datetime.datetime.now().timestamp())

        users_id = self.__execute_query(
            'SELECT chat_id FROM users WHERE (status = "buyer" or status = "admin") AND time_of_expiry > ?',
            (timestamp,)
        )

        return [chat_id[0] for chat_id in users_id]

    def get_admins_id(self):
        timestamp = int(datetime.datetime.now().timestamp())

        admins_id = self.__execute_query(
            'SELECT chat_id FROM users WHERE status = "admin" AND time_of_expiry > ?',
            (timestamp,)
        )
        return [admin_id[0] for admin_id in admins_id]

    def check_user(self, chat_id: int) -> bool:
        user = self.__execute_query('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
        return bool(user)

    def user_is_admin(self, chat_id: int) -> bool:
        if self.check_user(chat_id):
            status = self.__execute_query('SELECT status FROM users WHERE chat_id = ?', (chat_id,))[0][0]

            return True if status == 'admin' else False
        else:
            return False

    def get_status_user_by_access_key(self, access_key: str) -> str:
        return self.__execute_query(
            'SELECT status FROM access_keys WHERE access_key = ?',
            (access_key,)
        )[0][0]

    def add_access_key(self, access_key: str, date_of_expiry: str, status: str = 'buyer'):
        self.__execute_query(
            'INSERT INTO access_keys (access_key, status, date_of_expiry) VALUES (?, ?, ?)',
            (access_key, status, date_of_expiry)
        )

    def check_access_key(self, access_key: str):
        key_info = self.__execute_query(
            'SELECT is_use, date_of_expiry FROM access_keys WHERE access_key = ?',
            (access_key,)
        )

        if not key_info:
            return AccessCodeInfo(status=False, is_use=False)
        else:
            if not bool(int(key_info[0][0])):
                return AccessCodeInfo(status=True, is_use=False, date_of_expiry=key_info[0][1])
            else:
                return AccessCodeInfo(status=False, is_use=True)

    def update_status_access_key(self, access_key: str, is_use: int):
        self.__execute_query(
            'UPDATE access_keys SET is_use = ? WHERE access_key = ?',
            (is_use, access_key)
        )
