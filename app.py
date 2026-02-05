from flask import Flask, request, jsonify, redirect
import psycopg2
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()

app = Flask(__name__)

# Postgres Connection
conn = psycopg2.connect(
    database="postgres",
    user="postgres",
    password=os.environ["DB_PW"],
    host="localhost",
    port=5432
)

# Create initial table if it doesn't exist
with conn:
    with conn.cursor() as cur:
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS greetings (
                        id SERIAL PRIMARY KEY,
                        message TEXT NOT NULL);
                    """)

@app.route("/")
def index():
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT message 
                        FROM greetings
                        ORDER BY id DESC
                        LIMIT 1                        
                        """)
            row = cur.fetchone()
            if row:
                latest = row[0]
            else:
                latest = "No greetings yet!"
            
    return f"""
        <h1>{latest}</h1> 
        
        <form action="/submit" method="POST"> 
            <input type="text" name="greeting" placeholder="Type something..." required> 
            <button type="submit">Submit</button> 
        </form> 



        <!--
            <form action="/delete" method="POST"> 
                <button type="submit">Clear</button> 
            </form> 
        -->
        
        <button id="deleteBtn">Delete</button>

        <script>
        document.getElementById('deleteBtn')
        .addEventListener('click', async () => {{
            await fetch('/delete', {{ method: 'DELETE' }});
            window.location.reload();
        }});
        </script>
    """

@app.get('/greetings')
def get_all_greetings():
        with conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("SELECT * FROM greetings")
                    rows = cur.fetchall()
                    return jsonify(rows), 200
                except Exception as e:
                    logging.error(f"Error retrieving rows: {e}")
                    return jsonify({ "mssage": "Failed to retrieve rows."}), 500

# Posts the new greetings to the database
@app.route("/submit", methods=["POST"])
def submit():
    text = request.form["greeting"] # grabs user input from html
    with conn:
        with conn.cursor() as cur:
            try:
                cur.execute("""
                            INSERT INTO greetings (message) 
                            VALUES (%s)""", (text,))
                logging.info("Successfully updated database.")
                return redirect("/") # sends user back to homepage
            except Exception as e:
                logging.error(f"Error updating database {e}")
                return jsonify({"message": "Failed to update database."})

# Deletes greetings from database
@app.route("/delete", methods=["DELETE"])
def delete():
    with conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM greetings;")
            logging.info("Deleted all messages from database")
    # return redirect("/")
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)