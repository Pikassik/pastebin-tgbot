import sqlite3


with sqlite3.connect('links') as connect:
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE links (chat_id INTEGER,
                                          filename TEXT,
                                          tag TEXT,
                                          comment TEXT,
                                          date DATE,
                                          link TEXT);""")
    cursor.execute("""CREATE TABLE users (chat_id INTEGER,
                                          current_tag TEXT,
                                          current_expire_date TEXT,
                                          current_paste_format TEXT,
                                          current_pricate INTEGER);""")
