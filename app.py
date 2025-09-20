from flask import Flask, request, jsonify
from flask_cors import CORS
import db
import os

app = Flask(__name__)
CORS(app)

# Инициализация базы при запуске сервера
with app.app_context():
    db.init_db()
    print("🚀 Сервер запущен и готов к работе!")

@app.route("/")
def home():
    print("📞 Получен запрос на главную страницу")
    return jsonify({
        "message": "Pepuh Leaderboard Server", 
        "status": "running",
        "version": "1.0"
    })

@app.route("/api/health")
def health():
    print("📞 Получен запрос health check")
    return jsonify({"status": "healthy", "database": "SQLite"})

@app.route("/api/register", methods=["POST"])
def register():
    try:
        print("📞 Получен запрос на регистрацию")
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        name = data.get("name")
        if not name:
            return jsonify({"error": "Name is required"}), 400
        
        db.add_player(name)
        print(f"✅ Игрок {name} зарегистрирован")
        return jsonify({"message": f"Player '{name}' registered successfully!"})
        
    except Exception as e:
        print(f"❌ Ошибка при регистрации: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/update_score", methods=["POST"])
def update_score():
    try:
        print("📞 Получен запрос на обновление счета")
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        name = data.get("name")
        score = data.get("score")
        
        if not name or score is None:
            return jsonify({"error": "Name and score are required"}), 400
        
        success = db.update_score(name, score)
        
        if success:
            print(f"✅ Счет обновлен для {name}: {score}")
            return jsonify({
                "message": f"Score updated for {name}",
                "score": score,
                "status": "success"
            })
        else:
            print(f"⚠️ Счет не обновлен для {name} (текущий счет выше)")
            return jsonify({
                "message": f"Score not updated for {name} (current score is higher)",
                "score": score,
                "status": "not_updated"
            })
            
    except Exception as e:
        print(f"❌ Ошибка при обновлении счета: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/leaderboard", methods=["GET"])
def leaderboard():
    try:
        print("📞 Получен запрос лидерборда")
        limit = request.args.get('limit', 10, type=int)
        leaders = db.get_leaderboard(limit)
        
        # Форматируем для Godot
        formatted_leaders = [[player[0], player[1]] for player in leaders]
        
        print(f"✅ Лидерборд отправлен: {len(leaders)} игроков")
        return jsonify({
            "leaders": formatted_leaders,
            "count": len(leaders),
            "status": "success"
        })
        
    except Exception as e:
        print(f"❌ Ошибка при получении лидерборда: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/player/<name>", methods=["GET"])
def get_player(name):
    try:
        print(f"📞 Получен запрос информации об игроке: {name}")
        player = db.get_player_stats(name)
        
        if player:
            print(f"✅ Информация об игроке {name} отправлена")
            return jsonify({
                "name": player[0],
                "best_score": player[1],
                "created_at": player[2],
                "updated_at": player[3],
                "status": "found"
            })
        else:
            print(f"⚠️ Игрок {name} не найден")
            return jsonify({"error": "Player not found"}), 404
            
    except Exception as e:
        print(f"❌ Ошибка при получении информации об игроке: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/test")
def test():
    print("✅ Тестовый запрос получен!")
    return jsonify({
        "status": "success", 
        "message": "Server is working!",
        "database": "SQLite"
    })

if __name__ == "__main__":
    # Получаем порт из переменной окружения (для Render)
    port = int(os.environ.get("PORT", 5000))
    
    # Инициализируем базу
    db.init_db()
    
    print(f"🚀 Запуск сервера на порту {port}")
    app.run(
        host="0.0.0.0", 
        port=port, 
        debug=False,  # На продакшене debug=False
        threaded=True
    )