from flask import Flask, send_file, request, render_template_string, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import qrcode
import io
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "CHANGE_TO_A_SECRET_KEY"  # indispensable pour login

# SQLite pour stocker restaurants et stats
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qrmenu.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

BASE_URL = "https://qr-menu-saas.onrender.com"  # ton URL Render

# ================= MODELES =================
class Restaurant(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    scans = db.relationship("Scan", backref="restaurant", lazy=True)
    items = db.relationship("MenuItem", backref="restaurant", lazy=True)

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    restaurant_id = db.Column(db.String, db.ForeignKey("restaurant.id"), nullable=False)

class Scan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now)
    restaurant_id = db.Column(db.String, db.ForeignKey("restaurant.id"), nullable=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String)

# ================= INIT DB =================
@app.before_first_request
def create_tables():
    db.create_all()
    if not Admin.query.filter_by(username="admin").first():
        db.session.add(Admin(username="admin", password_hash=generate_password_hash("admin123")))
        db.session.commit()

# ================= CLIENT =================
@app.route("/")
def home():
    return "<h1>QR Menu SaaS</h1><p>Accède aux menus via /menu/resto_id ou QR code /qrcode/resto_id</p>"

@app.route("/menu/<resto_id>")
def menu(resto_id):
    resto = Restaurant.query.get(resto_id)
    if not resto:
        return "Restaurant introuvable", 404
    db.session.add(Scan(restaurant=resto))
    db.session.commit()
    
    html = f"""
    <html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <style>
    body{{font-family:Arial;margin:20px;background:#f9f9f9;}}
    h1{{color:#333;}}
    .menu-item{{padding:10px;border-bottom:1px solid #ddd;}}
    </style></head><body>
    <h1>{resto.name}</h1>
    """
    for item in resto.items:
        html += f"<div class='menu-item'>{item.name} - {item.price}€</div>"
    html += "</body></html>"
    return html

@app.route("/qrcode/<resto_id>")
def qrcode_menu(resto_id):
    url = f"{BASE_URL}/menu/{resto_id}"
    img = qrcode.make(url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype="image/png")

@app.route("/stats/<resto_id>")
def stats(resto_id):
    resto = Restaurant.query.get(resto_id)
    if not resto:
        return "Restaurant introuvable", 404
    total = len(resto.scans)
    return f"<h1>Stats {resto.name}</h1><p>Total scans : {total}</p>"

# ================= LOGIN =================
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            session["admin"] = username
            return redirect("/admin")
        return "Login failed"
    return """
    <form method='post'>
    Username: <input name='username'><br>
    Password: <input name='password' type='password'><br>
    <button>Login</button>
    </form>
    """

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/login")

# ================= ADMIN =================
@app.route("/admin", methods=["GET","POST"])
def admin():
    if "admin" not in session:
        return redirect("/login")
    message=""
    if request.method=="POST":
        action=request.form.get("action")
        resto_id=request.form.get("resto_id")
        name=request.form.get("name")
        item_name=request.form.get("item_name")
        item_price=request.form.get("item_price")
        resto=Restaurant.query.get(resto_id)

        # Ajouter un resto
        if action=="add_resto" and resto_id and name:
            if resto:
                message=f"Resto {resto_id} existe déjà"
            else:
                db.session.add(Restaurant(id=resto_id,name=name))
                db.session.commit()
                message=f"Resto {name} ajouté"

        # Ajouter plat
        if action=="add_item" and resto and item_name and item_price:
            try:
                price=float(item_price)
                db.session.add(MenuItem(name=item_name,price=price,restaurant=resto))
                db.session.commit()
                message=f"Plat {item_name} ajouté"
            except:
                message="Prix invalide"

        # Supprimer plat
        if action=="delete_item" and resto and item_name:
            item=MenuItem.query.filter_by(name=item_name,restaurant=resto).first()
            if item:
                db.session.delete(item)
                db.session.commit()
                message=f"Plat {item_name} supprimé"

    restos=Restaurant.query.all()
    html="<h1>Admin QR Menu SaaS</h1>"
    html+="<p style='color:red'>{}</p>".format(message)
    html+="<p><a href='/logout'>Logout</a></p>"
    # Formulaires simples
    html+="""<h2>Ajouter un resto</h2>
    <form method='post'>ID: <input name='resto_id'> Nom: <input name='name'>
    <button name='action' value='add_resto'>Ajouter</button></form>"""

    html+="""<h2>Ajouter un plat</h2>
    <form method='post'>Resto ID: <input name='resto_id'> Nom Plat: <input name='item_name'> Prix: <input name='item_price'>
    <button name='action' value='add_item'>Ajouter</button></form>"""

    html+="""<h2>Supprimer un plat</h2>
    <form method='post'>Resto ID: <input name='resto_id'> Nom Plat: <input name='item_name'>
    <button name='action' value='delete_item'>Supprimer</button></form>"""

    # Liste des restos
    for r in restos:
        html+="<h3>{} - {}</h3>".format(r.id,r.name)
        html+="<ul>"
        for i in r.items:
            html+="<li>{} - {}€</li>".format(i.name,i.price)
        html+="</ul>"
        html+="<p>Total scans: {}</p>".format(len(r.scans))
        html+="<p>QR: <a href='{}/qrcode/{}' target='_blank'>{}/qrcode/{}</a></p>".format(BASE_URL,r.id,BASE_URL,r.id)

    return html

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000)










