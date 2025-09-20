import requests

BASE_URL = "http://127.0.0.1:5000"

# Регистрируем игрока
resp = requests.post(f"{BASE_URL}/register", json={"name": "Nazar"})
print("REGISTER:", resp.json())

# Обновляем рекорд
resp = requests.post(f"{BASE_URL}/update_score", json={"name": "Nazar", "score": 150})
print("UPDATE SCORE:", resp.json())

# Получаем топ игроков
resp = requests.get(f"{BASE_URL}/leaderboard")
print("LEADERBOARD:", resp.json())

