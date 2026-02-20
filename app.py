import os
from urllib.parse import urlparse
from flask import Flask, render_template
import psycopg

# Chemin absolu du dossier contenant app.py
base_dir = os.path.dirname(os.path.abspath(__file__))

# Crée l'app Flask et force le template_folder
app = Flask(__name__, template_folder=base_dir)

# Récupère l'URL de la DB depuis Render
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    """Connexion à PostgreSQL via psycopg."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL n'est pas défini dans les variables d'environnement")

    result = urlparse(DATABASE_URL)
    conn = psycopg.connect(
        host=result.hostname,
        port=result.port or 5432,
        dbname=result.path[1:],  # enlève le '/' du début
        user=result.username,
        password=result.password
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

    # Rendu de la page index.html
    return render_template("index.html", data=data)

if __name__ == "__main__":
    # Port 10000 pour Render ou 5000 localement
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
