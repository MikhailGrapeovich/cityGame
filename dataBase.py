import sqlite3


def connection_db(func):
    def wrap(*args, **kwargs):
        try:
            con = sqlite3.connect("cities_db.db")
            cur = con.cursor()
            r = func(*args, **kwargs, cur=cur)
            con.commit()
            con.close()
            return r
        except sqlite3.Error as e:
            con.close()
            print(f"ошибка базы данных - {e}")

    return wrap


@connection_db
def start():
    cur.execute("CREATE TABLE IF NOT EXISTS users(chat_id INT PRIMARY KEY, score INT, cities TEXT)")


@connection_db
def add_db(chat_id, score, cities, cur):
    cur.execute(f"INSERT INTO users(chat_id, score, cities)  VALUES({chat_id}, {score}, '{cities}')")


@connection_db
def get_all_db(cur):
    cur.execute(f"SELECT * FROM users")
    return cur.fetchall()


@connection_db
def get_db(chat_id, cur):
    cur.execute(f"SELECT * FROM users WHERE chat_id={chat_id}")
    return cur.fetchone()


@connection_db
def update_db(chat_id, score, cities, cur):
    cur.execute(f"UPDATE users SET score={score}, cities='{cities}' WHERE chat_id={chat_id}")


@connection_db
def delete(chat_id, cur):
    cur.execute(f"DELETE FROM users WHERE chat_id = {chat_id}")


start()