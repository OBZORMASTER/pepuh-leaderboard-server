import os
from supabase import create_client
from flask import Flask
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ініціалізація Flask додатку
app = Flask(__name__)

# Підключення до Supabase
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

# Додатковий вивід для відладки (можна прибрати після налаштування)
logger.info(f"SUPABASE_URL: {supabase_url}")
logger.info(f"SUPABASE_KEY присутній: {bool(supabase_key)}")

# Перевіряємо наявність змінних оточення
if not supabase_url or not supabase_key:
    logger.error("ПОМИЛКА: Не знайдено змінні оточення Supabase!")
    logger.error("Будь ласка, додайте SUPABASE_URL та SUPABASE_KEY в Render Environment Variables")
    supabase_client = None
else:
    try:
        supabase_client = create_client(supabase_url, supabase_key)
        logger.info("Успішне підключення до Supabase!")
    except Exception as e:
        logger.error(f"Помилка підключення до Supabase: {e}")
        supabase_client = None

def init_db():
    """Функція ініціалізації бази даних (залишена для сумісності)"""
    logger.info("База даних Supabase готова до роботи!")
    return True

def add_player(name):
    """Додає нового гравця до бази даних"""
    if supabase_client is None:
        logger.error("Supabase не підключено")
        return False
        
    try:
        result = supabase_client.table("players").insert({
            "name": name,
            "best_score": 0
        }).execute()
        
        logger.info(f"Гравець {name} успішно доданий до Supabase")
        return True
        
    except Exception as e:
        logger.error(f"Помилка додавання гравця {name}: {e}")
        return False

def update_score(name, score):
    """Оновлює найкращий рахунок гравця"""
    if supabase_client is None:
        logger.error("Supabase не підключено")
        return False
        
    try:
        # 1. Знаходимо гравця в базі даних
        response = supabase_client.table("players").select("*").eq("name", name).execute()
        
        # 2. Якщо гравець існує
        if response.data:
            current_score = response.data[0]["best_score"]
            
            # 3. Перевіряємо чи новий рахунок кращий за поточний
            if score > current_score:
                result = supabase_client.table("players").update({
                    "best_score": score,
                    "updated_at": "now()"
                }).eq("name", name).execute()
                
                logger.info(f"Рахунок оновлено: {name} -> {score}")
                return True
            else:
                logger.info(f"Рахунок не оновлено: у {name} вже є кращий результат {current_score}")
                return False
                
        # 4. Якщо гравця не існує - створюємо нового
        else:
            result = supabase_client.table("players").insert({
                "name": name,
                "best_score": score
            }).execute()
            
            logger.info(f"Створено нового гравця: {name} -> {score}")
            return True
            
    except Exception as e:
        logger.error(f"Помилка оновлення рахунку: {e}")
        return False

def get_leaderboard(limit=10):
    """Повертає топ гравців за рахунком"""
    if supabase_client is None:
        logger.error("Supabase не підключено")
        return []
        
    try:
        response = supabase_client.table("players").select(
            "name, best_score"
        ).order("best_score", desc=True).limit(limit).execute()
        
        leaders = []
        for player in response.data:
            leaders.append((player["name"], player["best_score"]))
        
        logger.info(f"Отримано {len(leaders)} гравців з таблиці лідерів")
        return leaders
        
    except Exception as e:
        logger.error(f"Помилка отримання таблиці лідерів: {e}")
        return []

def get_player_stats(name):
    """Повертає статистику гравця"""
    if supabase_client is None:
        logger.error("Supabase не підключено")
        return None
        
    try:
        response = supabase_client.table("players").select(
            "name, best_score, created_at, updated_at"
        ).eq("name", name).execute()
        
        if response.data:
            player = response.data[0]
            return (player["name"], player["best_score"], player["created_at"], player["updated_at"])
        else:
            return None
            
    except Exception as e:
        logger.error(f"Помилка отримання статистики гравця: {e}")
        return None

def delete_player(name):
    """Видаляє гравця з бази даних"""
    if supabase_client is None:
        logger.error("Supabase не підключено")
        return False
        
    try:
        result = supabase_client.table("players").delete().eq("name", name).execute()
        
        if len(result.data) > 0:
            logger.info(f"Гравець {name} успішно видалений")
            return True
        else:
            logger.warning(f"Гравець {name} не знайдений в базі даних")
            return False
            
    except Exception as e:
        logger.error(f"Помилка видалення гравця: {e}")
        return False