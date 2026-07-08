import sqlite3

DB_NAME = "chasevault.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_cards_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            game TEXT,
            set_name TEXT,
            card_number TEXT,
            condition TEXT,
            quantity INTEGER,
            purchase_price REAL,
            current_value REAL
        )
    """)

    conn.commit()
    conn.close()


def add_card(name, game, set_name, card_number, condition, quantity, purchase_price, current_value):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cards (
            name,
            game,
            set_name,
            card_number,
            condition,
            quantity,
            purchase_price,
            current_value
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        game,
        set_name,
        card_number,
        condition,
        quantity,
        purchase_price,
        current_value
    ))

    conn.commit()
    conn.close()


def get_all_cards():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, game, set_name, card_number, condition,
               quantity, purchase_price, current_value
        FROM cards
    """)

    cards = cursor.fetchall()
    conn.close()

    return cards


def delete_card(card_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM cards WHERE id = ?", (card_id,))

    conn.commit()
    conn.close()
