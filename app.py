from flask import Flask, request, jsonify
from flask_cors import CORS
import db

app = Flask(__name__)
CORS(app)  # разрешаем запросы с игры (Godot)

# Инициализация базы при старте сервера
db.init_db()

@app.route("/")
def home():
    return "Server is running! ✅"

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    name = data.get("name")
    if not name:
        return jsonify({"error": "Name is required"}), 400
    
    db.add_player(name)
    return jsonify({"message": f"Player '{name}' registered!"})

@app.route("/update_score", methods=["POST"])
def update_score():
    data = request.json
    name = data.get("name")
    score = data.get("score")
    if not name or score is None:
        return jsonify({"error": "Name and score are required"}), 400
    
    db.update_score(name, score)
    return jsonify({"message": f"Score updated for {name}", "score": score})

@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    leaders = db.get_leaderboard()
    return jsonify(leaders)

if __name__ == "__main__":
    app.run(debug=True)
