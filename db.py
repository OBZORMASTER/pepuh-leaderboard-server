import sqlite3
import os

DB_NAME = "players.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    """Ініціалізує базу даних"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            best_score INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Перевіряємо існування стовпця updated_at і додаємо якщо потрібно
        cursor.execute("PRAGMA table_info(players)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'updated_at' not in columns:
            cursor.execute("ALTER TABLE players ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
            print("Доданий стовпець updated_at")
        
        conn.commit()
        print("База даних ініціалізована")
        
    except Exception as e:
        print(f"Помилка ініціалізації БД: {e}")
    finally:
        conn.close()

def add_player(name):
    """Додає нового гравця"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO players (name) VALUES (?)", (name,))
        conn.commit()
        print(f"Гравця {name} додано")
        
    except sqlite3.IntegrityError:
        print(f"Гравець {name} вже існує")
    except Exception as e:
        print(f"Помилка додавання гравця: {e}")
    finally:
        conn.close()

def update_score(name, score):
    """Оновлює рахунок гравця"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Спочатку перевіряємо існування гравця
        cursor.execute("SELECT id, best_score FROM players WHERE name = ?", (name,))
        player = cursor.fetchone()
        
        if player:
            player_id, current_score = player
            if score > current_score:
                # Оновлюємо рахунок
                cursor.execute("""
                    UPDATE players 
                    SET best_score = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE name = ?
                """, (score, name))
                conn.commit()
                print(f"Рахунок для {name} оновлено: {score} (було: {current_score})")
                return True
            else:
                print(f"Рахунок {name} не оновлено (текущий {current_score} > нового {score})")
                return False
        else:
            # Добавляем нового игрока
            cursor.execute("INSERT INTO players (name, best_score) VALUES (?, ?)", (name, score))
            conn.commit()
            print(f"Новий гравець {name} додано з рахунком: {score}")
            return True
                
    except Exception as e:
        print(f"Помилка під час оновлення рахунку: {e}")
        return False
    finally:
        conn.close()

def get_leaderboard(limit=10):
    """Повертає топ гравців"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, best_score 
            FROM players 
            ORDER BY best_score DESC 
            LIMIT ?
        """, (limit,))
        
        leaders = cursor.fetchall()
        return leaders
        
    except Exception as e:
        print(f"Помилка при отриманні лідерборду: {e}")
        return []
    finally:
        conn.close()

def get_player_stats(name):
    """Повертає статистику гравця"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, best_score, created_at, updated_at
            FROM players 
            WHERE name = ?
        """, (name,))
        
        player = cursor.fetchone()
        return player
        
    except Exception as e:
        print(f"Помилка при отриманні статистики: {e}")
        return None
    finally:
        conn.close()