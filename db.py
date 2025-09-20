import sqlite3
import os

DB_NAME = "players.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    """Инициализирует базу данных"""
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
        
        # Проверяем существование столбца updated_at и добавляем если нужно
        cursor.execute("PRAGMA table_info(players)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'updated_at' not in columns:
            cursor.execute("ALTER TABLE players ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
            print("✅ Добавлен столбец updated_at")
        
        conn.commit()
        print("✅ База данных инициализирована")
        
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
    finally:
        conn.close()

def add_player(name):
    """Добавляет нового игрока"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO players (name) VALUES (?)", (name,))
        conn.commit()
        print(f"✅ Игрок {name} добавлен")
        
    except sqlite3.IntegrityError:
        print(f"⚠️ Игрок {name} уже существует")
    except Exception as e:
        print(f"❌ Ошибка добавления игрока: {e}")
    finally:
        conn.close()

def update_score(name, score):
    """Обновляет счет игрока"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Сначала проверяем существование игрока
        cursor.execute("SELECT id, best_score FROM players WHERE name = ?", (name,))
        player = cursor.fetchone()
        
        if player:
            player_id, current_score = player
            if score > current_score:
                # Обновляем счет
                cursor.execute("""
                    UPDATE players 
                    SET best_score = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE name = ?
                """, (score, name))
                conn.commit()
                print(f"✅ Счет для {name} обновлен: {score} (было: {current_score})")
                return True
            else:
                print(f"⚠️ Счет для {name} не обновлен (текущий {current_score} > нового {score})")
                return False
        else:
            # Добавляем нового игрока
            cursor.execute("INSERT INTO players (name, best_score) VALUES (?, ?)", (name, score))
            conn.commit()
            print(f"✅ Новый игрок {name} добавлен со счетом: {score}")
            return True
                
    except Exception as e:
        print(f"❌ Ошибка при обновлении счета: {e}")
        return False
    finally:
        conn.close()

def get_leaderboard(limit=10):
    """Возвращает топ игроков"""
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
        print(f"❌ Ошибка при получении лидерборда: {e}")
        return []
    finally:
        conn.close()

def get_player_stats(name):
    """Возвращает статистику игрока"""
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
        print(f"❌ Ошибка при получении статистики: {e}")
        return None
    finally:
        conn.close()