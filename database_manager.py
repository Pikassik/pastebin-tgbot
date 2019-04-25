import sqlite3
import traceback


class DBManager:
    @staticmethod
    def get_links_by_tag(chat_id, tag=''):
        with sqlite3.connect('links') as connect:
            cursor = connect.cursor()
            cursor.execute(
                """SELECT * FROM links WHERE chat_id == ? AND tag == ?;""",
                (chat_id, tag))
            return cursor.fetchall()

    @staticmethod
    def get_link(chat_id, link):
        with sqlite3.connect('links') as connect:
            cursor = connect.cursor()
            cursor.execute(
                """SELECT * FROM links WHERE chat_id == ? AND link == ?;""",
                (chat_id, link))
            return cursor.fetchall()
    
    @staticmethod
    def insert_link(chat_id, file_name, tag, comment, date, link):
        with sqlite3.connect('links') as connect:
            cursor = connect.cursor()
            cursor.execute("""INSERT INTO links
                                VALUES (?, ?, ?, ?, ?, ?);""",
                           (chat_id, file_name, tag,
                            comment, date, link))
            connect.commit()

    @staticmethod
    def update_paste_format(chat_id, paste_format):
        with sqlite3.connect('links') as connect:
            cursor = connect.cursor()
            cursor.execute("""UPDATE users
                              SET current_paste_format = ?
                              WHERE chat_id = ?""",
                           (paste_format, chat_id))

    @staticmethod
    def get_links(chat_id):
        with sqlite3.connect('links') as connect:
            cursor = connect.cursor()
            cursor.execute("""SELECT * FROM links WHERE chat_id == ?;""",
                           [chat_id])
            return cursor.fetchall()


    @staticmethod
    def delete_link(chat_id, link):
        with sqlite3.connect('links') as connect:
            cursor = connect.cursor()
            cursor.execute(
                """DELETE FROM links WHERE chat_id == ? AND link == ?""",
                (chat_id, link))

    @staticmethod
    def get_user_info(chat_id):
        with sqlite3.connect('links') as connect:
            cursor = connect.cursor()
            cursor.execute("""SELECT * FROM users WHERE chat_id == ?;""",
                           [chat_id])
            return cursor.fetchall()
        
    @staticmethod
    def insert_user(chat_id):
        with sqlite3.connect('links') as connect:
            cursor = connect.cursor()
            cursor.execute("""INSERT INTO users
                              VALUES (?, ?, ?, ?, ?);""",
                           (chat_id, '', 'N', 'text', 0))

    @staticmethod
    def update_tag(chat_id, tag):
        with sqlite3.connect('links') as connect:
            cursor = connect.cursor()
            cursor.execute("""UPDATE users
                              SET current_tag = ?
                              WHERE chat_id = ?""",
                           (tag, chat_id))

    @staticmethod
    def update_expire_date(chat_id, expire_date):
        with sqlite3.connect('links') as connect:
            cursor = connect.cursor()
            cursor.execute("""UPDATE users
                              SET current_expire_date = ?
                              WHERE chat_id = ?""",
                           (expire_date, chat_id))

    @staticmethod
    def update_private(chat_id, private):
            with sqlite3.connect('links') as connect:
                cursor = connect.cursor()
                cursor.execute("""UPDATE users
                                  SET current_private = ?
                                  WHERE chat_id = ?""",
                               (private, chat_id))


def db_exception_keeper(function):
    def wrapped(*args, **kwargs):
        try:
            return function(*args, *kwargs)
        except sqlite3.Error:
            traceback.print_exc()
    wrapped.__name__ = function.__name__
    wrapped.__doc__ = function.__doc__
    wrapped.__module__ = function.__module__
    return wrapped
