from flask import Flask, render_template
import os
from urllib.parse import urlparse
import psycopg2

app = Flask(__name__)

# Récupère l'URL de connexion PostgreSQL depuis Render
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    """Crée une connexion à PostgreSQL à partir de DATABASE_URL."""
    result = urlparse(DATABASE_URL)
    username = result.username
    password = result.password
    database = result.path[1:]  # retirer le '/'
    hostname = result.hostname
    port = result.port or 5432

    conn = psycopg2.connect(
        dbname=database,
        user=username,
        password=password,
        host=hostname,
        port=port
    )
    return conn

@app.route('/')
def index():
    """Affiche toutes les tables et leur contenu de la base Lunivetta."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Récupère la liste des tables publiques
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
        ORDER BY table_name;
    """)
    tables = [t[0] for t in cur.fetchall()]

    # Récupère le contenu de chaque table (limité à 100 lignes)
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
    # Port 10000 pour Render ou 5000 localement
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
