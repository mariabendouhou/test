from flask import Flask, render_template
import psycopg2
import os

app = Flask(__name__)

# Connexion PostgreSQL
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "lunivetta")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "")

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
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

    # Contenu de chaque table
    data = {}
    for table in tables:
        cur.execute(f"SELECT * FROM {table} LIMIT 100")  # Limite à 100 lignes
        colnames = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        data[table] = {"columns": colnames, "rows": rows}

    cur.close()
    conn.close()
    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)
