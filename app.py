import os
from urllib.parse import urlparse
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super-secret-key")

DATABASE_URL = os.environ.get("DATABASE_URL")

# ================= DATABASE =================

def get_db_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not set")

    result = urlparse(DATABASE_URL)

    return psycopg.connect(
        host=result.hostname,
        port=result.port or 5432,
        dbname=result.path[1:],
        user=result.username,
        password=result.password
    )

# ================= LOGIN PROTECTION =================

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "admin_user" not in session:
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated

# ================= ADMIN LOGIN =================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # 🔒 Change these in production
        if username == "admin" and password == "lunivetta123":
            session["admin_user"] = username
            flash("Connexion réussie", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Identifiants incorrects", "error")

    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))

# ================= DASHBOARD =================

@app.route("/admin")
@login_required
def admin_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = cur.fetchall()

    cur.execute("SELECT * FROM products ORDER BY id DESC")
    products = cur.fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        orders=orders,
        products=products
    )

# ================= UPDATE ORDER =================

@app.route("/admin/order/<int:order_id>/update", methods=["POST"])
@login_required
def update_order(order_id):
    statut = request.form["statut"]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE orders SET statut=%s WHERE id=%s",
        (statut, order_id)
    )
    conn.commit()
    conn.close()

    flash("Statut mis à jour", "success")
    return redirect(url_for("admin_dashboard"))

# ================= DELETE ORDER =================

@app.route("/admin/order/<int:order_id>/delete", methods=["POST"])
@login_required
def delete_order(order_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM orders WHERE id=%s", (order_id,))
    conn.commit()
    conn.close()

    flash("Commande supprimée", "success")
    return redirect(url_for("admin_dashboard"))

# ================= ADD PRODUCT =================

@app.route("/admin/product/add", methods=["POST"])
@login_required
def add_product():
    nom = request.form["nom"]
    prix = request.form["prix"]
    description = request.form.get("description", "")
    tailles = request.form.get("tailles", "")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO products (nom, prix, description, tailles, actif) VALUES (%s, %s, %s, %s, TRUE)",
        (nom, prix, description, tailles)
    )

    conn.commit()
    conn.close()

    flash("Produit ajouté", "success")
    return redirect(url_for("admin_dashboard"))

# ================= DELETE PRODUCT =================

@app.route("/admin/product/<int:product_id>/delete", methods=["POST"])
@login_required
def delete_product(product_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
    conn.commit()
    conn.close()

    flash("Produit supprimé", "success")
    return redirect(url_for("admin_dashboard"))

# ================= RUN =================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)