import os
from urllib.parse import urlparse
from flask import Flask, render_template
import psycopg

app = Flask(__name__, template_folder=".")

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    result = urlparse(DATABASE_URL)
    conn = psycopg.connect(
        host=result.hostname,
        port=result.port or 5432,
        dbname=result.path[1:],
        user=result.username,
        password=result.password
    )
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    # Liste des tables
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
        ORDER BY table_name;
    """)
    tables = [t[0] for t in cur.fetchall()]

    # Contenu des tables
    data = {}
    for table in tables:
        cur.execute(f"SELECT * FROM {table} LIMIT 100")
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        data[table] = {"columns": columns, "rows": rows}

    cur.close()
    conn.close()
    return render_template("index.html", data=data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
