from flask import Flask, render_template
import os
from urllib.parse import urlparse
import psycopg

app = Flask(__name__)

# Récupère l'URL de connexion PostgreSQL depuis Render
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    """Crée une connexion à PostgreSQL à partir de DATABASE_URL avec psycopg v3."""
    result = urlparse(DATABASE_URL)
    conn = psycopg.connect(
        host=result.hostname,
        port=result.port or 5432,
        dbname=result.path[1:],  # retire le '/'
        user=result.username,
        password=result.password
    )
    return conn

@app.route('/')
def index():
    """Affiche toutes les tables et leur contenu de la base Lunivetta."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Liste des tables publiques
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
        ORDER BY table_name;
    """)
    tables = [t[0] for t in cur.fetchall()]

    # Contenu de chaque table (limité à 100 lignes)
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
    # Port fourni par Render ou 5000 en local
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
