from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import psycopg2
import os
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app) # allow S3 frontend to call this API

# Postgres Connection
conn = psycopg2.connect(
    database=os.environ.get("DB_NAME", "postgres"),
    user=os.environ.get("DB_USER", "postgres"),
    password=os.environ["DB_PW"],
    host=os.environ.get("DB_HOST", "db"),
    port=os.environ.get("DB_PORT", 5432)
)

# Create initial table if it doesn't exist
with conn:
    with conn.cursor() as cur:
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS greetings (
                        id SERIAL PRIMARY KEY,
                        message TEXT NOT NULL);
                    """)
# API Routes
@app.get("/api/greetings/latest")
def get_latest():
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT message
                FROM greetings
                ORDER BY id DESC
                LIMIT 1
            """)
            row = cur.fetchone()

    latest = row[0] if row else None
    return jsonify({"latest": latest})


@app.get("/api/greetings")
def get_all_greetings():
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, message FROM greetings ORDER BY id DESC")
            rows = cur.fetchall()

    greetings = [{"id": r[0], "message": r[1]} for r in rows]
    return jsonify(greetings)


@app.post("/api/greetings")
def create_greeting():
    data = request.get_json()
    message = data.get("message")

    if not message:
        return jsonify({"error": "message is required"}), 400

    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO greetings (message) VALUES (%s) RETURNING id",
                (message,)
            )
            new_id = cur.fetchone()[0]

    return jsonify({"id": new_id, "message": message}), 201


@app.delete("/api/greetings")
def delete_greetings():
    with conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM greetings")

    return jsonify({"status": "deleted"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
