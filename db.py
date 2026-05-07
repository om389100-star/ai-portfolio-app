import sqlite3

def init_db():
    conn = sqlite3.connect("portfolio.db")
    c = conn.cursor()

    # Users table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # Portfolio table (linked to user)
    c.execute("""
    CREATE TABLE IF NOT EXISTS portfolios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        tickers TEXT,
        risk TEXT,
        expected_return REAL,
        sharpe REAL
    )
    """)

    conn.commit()
    conn.close()


def create_user(username, password):
    conn = sqlite3.connect("portfolio.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def login_user(username, password):
    conn = sqlite3.connect("portfolio.db")
    c = conn.cursor()

    c.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    return user


def save_portfolio(user_id, tickers, risk, expected_return, sharpe):
    conn = sqlite3.connect("portfolio.db")
    c = conn.cursor()

    c.execute("""
        INSERT INTO portfolios (user_id, tickers, risk, expected_return, sharpe)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, ",".join(tickers), risk, expected_return, sharpe))

    conn.commit()
    conn.close()


def get_portfolios(user_id):
    conn = sqlite3.connect("portfolio.db")
    c = conn.cursor()

    c.execute("""
        SELECT id, tickers, risk, expected_return, sharpe
        FROM portfolios WHERE user_id=?
    """, (user_id,))

    data = c.fetchall()
    conn.close()

    return data