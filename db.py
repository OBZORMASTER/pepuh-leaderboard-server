import sqlite3

DB_NAME = "players.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        best_score INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

def add_player(name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO players (name) VALUES (?)", (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # имя уже есть, не добавляем
    conn.close()

def update_score(name, score):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Сначала проверяем существует ли игрок
    cursor.execute("SELECT id, best_score FROM players WHERE name = ?", (name,))
    player = cursor.fetchone()
    
    if player is None:
        # Если игрока нет - создаем его
        cursor.execute("INSERT INTO players (name, best_score) VALUES (?, ?)", (name, score))
        print(f"Добавлен новый игрок: {name} с счетом: {score}")
    else:
        # Если игрок есть - обновляем счет только если новый счет больше
        current_score = player[1]
        if score > current_score:
            cursor.execute("UPDATE players SET best_score = ? WHERE name = ?", (score, name))
            print(f"Обновлен счет для {name}: {current_score} -> {score}")
        else:
            print(f"Счет не обновлен для {name}: текущий {current_score}, новый {score} (меньше)")
    
    conn.commit()
    conn.close()

def get_leaderboard(limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, best_score FROM players ORDER BY best_score DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows