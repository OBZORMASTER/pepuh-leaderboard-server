from flask import Flask, request, jsonify
from flask_cors import CORS
import db
import os

app = Flask(__name__)
CORS(app)

# запуск сервера
with app.app_context():
    db.init_db()
    print("Сервер готовий")

@app.route("/")
def home():
    print("Отримано запит на головну сторінку")
    return jsonify({
        "message": "Pepuh Leaderboard Server", 
        "status": "running",
        "version": "1.0"
    })

@app.route("/api/health")
def health():
    print("Отримано запит health check")
    return jsonify({"status": "healthy", "database": "SQLite"})

@app.route("/api/register", methods=["POST"])
def register():
    try:
        print("Отримано запит на реєстрацію")
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        name = data.get("name")
        if not name:
            return jsonify({"error": "Name is required"}), 400
        
        db.add_player(name)
        print(f"Гравець {name} зареєстрований")
        return jsonify({"message": f"Player '{name}' registered successfully!"})
        
    except Exception as e:
        print(f"Помилка під час реєстрації: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/update_score", methods=["POST"])
def update_score():
    try:
        print("Отримано запит на оновлення рахунку")
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        name = data.get("name")
        score = data.get("score")
        
        if not name or score is None:
            return jsonify({"error": "Name and score are required"}), 400
        
        success = db.update_score(name, score)
        
        if success:
            print(f"Рахунок оновлено для {name}: {score}")
            return jsonify({
                "message": f"Score updated for {name}",
                "score": score,
                "status": "success"
            })
        else:
            print(f"Рахунок не оновлено для {name} (текущий счет выше)")
            return jsonify({
                "message": f"Score not updated for {name} (current score is higher)",
                "score": score,
                "status": "not_updated"
            })
            
    except Exception as e:
        print(f"Помилка під час оновлення рахунку: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/leaderboard", methods=["GET"])
def leaderboard():
    try:
        print("Отриманий запит лідерборда")
        limit = request.args.get('limit', 10, type=int)
        leaders = db.get_leaderboard(limit)
        
        # Форматируем для Godot
        formatted_leaders = [[player[0], player[1]] for player in leaders]
        
        print(f"Лідерборд відправлено: {len(leaders)} гравців")
        return jsonify({
            "leaders": formatted_leaders,
            "count": len(leaders),
            "status": "success"
        })
        
    except Exception as e:
        print(f"Помилка при отриманні лідерборду: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/player/<name>", methods=["GET"])
def get_player(name):
    try:
        print(f"Отриманий запит інформації про гравця: {name}")
        player = db.get_player_stats(name)
        
        if player:
            print(f"Інформація про гравця {name} відправлена")
            return jsonify({
                "name": player[0],
                "best_score": player[1],
                "created_at": player[2],
                "updated_at": player[3],
                "status": "found"
            })
        else:
            print(f"⚠️ Гравця {name} не знайдено")
            return jsonify({"error": "Player not found"}), 404
            
    except Exception as e:
        print(f"Помилка при отриманні інформації про гравця: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/test")
def test():
    print("Тестовий запит отримано!")
    return jsonify({
        "status": "success", 
        "message": "Server is working!",
        "database": "SQLite"
    })

if __name__ == "__main__":
    # Отримуємо порт із змінної оточення (для Render)
    port = int(os.environ.get("PORT", 5000))
    
    # Ініціалізуємо базу
    db.init_db()
    
    print(f"Запуск сервера на порту {port}")
    app.run(
        host="0.0.0.0", 
        port=port, 
        debug=False,  # На продакшені debug = False
        threaded=True
    )