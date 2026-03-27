from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os, time, redis, json

app = Flask(__name__)

DB_USER = os.environ.get('POSTGRES_USER', 'pgadmin')
DB_PASS = os.environ.get('POSTGRES_PASSWORD', 'root')
DB_NAME = os.environ.get('POSTGRES_DB', 'tasks')
DB_HOST = os.environ.get('DB_HOST', 'db')
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
cache = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {"id": self.id, "title": self.title}

with app.app_context():
    for i in range(10):
        try:
            db.create_all()
            print("Connecté à la base de données !")
            break
        except Exception as e:
            print(f"⏳ DB pas encore prête, tentative {i+1}/10... ({e})")
            time.sleep(3)

@app.route("/tasks", methods=["GET"])
def get_tasks():
    cached = cache.get("tasks")
    if cached:
        print(" Données depuis le CACHE Redis")
        return jsonify(json.loads(cached))
    print(" Données depuis la BASE DE DONNÉES")
    tasks = Task.query.all()
    result = [t.to_dict() for t in tasks]
    cache.setex("tasks", 30, json.dumps(result))
    return jsonify(result)

@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"error": "Title is required"}), 400
    task = Task(title=data["title"])
    db.session.add(task)
    db.session.commit()
    cache.delete("tasks")
    return jsonify(task.to_dict()), 201

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    db.session.delete(task)
    db.session.commit()
    cache.delete("tasks")
    return jsonify({"message": "Task deleted"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)