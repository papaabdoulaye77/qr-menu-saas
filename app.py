from flask import Flask, send_file, request, render_template_string, redirect, url_for
import qrcode
import io
from datetime import datetime

app = Flask(__name__)

BASE_URL = "https://qr-menu-saas.onrender.com"  # METS ICI TON URL RENDER

# Dictionnaire pour stocker les restaurants, menus et stats
restaurants = {
    "resto1": {
        "name": "Pizza Palace",
        "menu": [
            {"name": "Pizza Margherita", "price": 9},
            {"name": "Pizza Pepperoni", "price": 11},
            {"name": "Coca-Cola", "price": 3}
        ],
        "scans": [],
    },
    "resto2": {
        "name": "Burger House",
        "menu": [
            {"name": "Burger", "price": 10},
            {"name": "Frites", "price": 4},
            {"name": "Eau", "price": 2}
        ],
        "scans": [],
    }
}

# ================= CLIENT =================
@app.route("/")
def home():
    return "<h1>QR Menu SaaS is running</h1><p>Ajoute /menu/resto_id ou /qrcode/resto_id</p>"

@app.route("/menu/<resto_id>")
def menu(resto_id):
    if resto_id not in restaurants:
        return "Restaurant introuvable", 404
    # Ajouter un scan avec date
    restaurants[resto_id]["scans"].append(datetime.now())
    
    html = f"<h1>{restaurants[resto_id]['name']}</h1><ul>"
    for item in restaurants[resto_id]["menu"]:
        html += f"<li>{item['name']} - {item['price']}€</li>"
    html += "</ul>"
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
    if resto_id not in restaurants:
        return "Restaurant introuvable", 404
    total = len(restaurants[resto_id]["scans"])
    return f"<h1>Stats pour {restaurants[resto_id]['name']}</h1><p>Total scans : {total}</p>"

# ================= ADMIN =================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    message = ""
    if request.method == "POST":
        action = request.form.get("action")
        resto_id = request.form.get("resto_id")
        name = request.form.get("name")
        item_name = request.form.get("item_name")
        item_price = request.form.get("item_price")

        # Ajouter un restaurant
        if action == "add_resto" and resto_id and name:
            if resto_id in restaurants:
                message = f"Le resto {resto_id} existe déjà"
            else:
                restaurants[resto_id] = {"name": name, "menu": [], "scans": []}
                message = f"Resto {name} ajouté"

        # Ajouter un plat
        if action == "add_item" and resto_id in restaurants and item_name and item_price:
            try:
                price = float(item_price)
                restaurants[resto_id]["menu"].append({"name": item_name, "price": price})
                message = f"Plat {item_name} ajouté à {restaurants[resto_id]['name']}"
            except:
                message = "Prix invalide"

        # Supprimer un plat
        if action == "delete_item" and resto_id in restaurants and item_name:
            menu = restaurants[resto_id]["menu"]
            restaurants[resto_id]["menu"] = [i for i in menu if i["name"] != item_name]
            message = f"Plat {item_name} supprimé de {restaurants[resto_id]['name']}"

    html = """
    <h1>Admin QR Menu SaaS</h1>
    <p style="color:red">{{message}}</p>

    <h2>Ajouter un restaurant</h2>
    <form method="post">
        ID Resto: <input name="resto_id">
        Nom Resto: <input name="name">
        <button name="action" value="add_resto">Ajouter Resto</button>
    </form>

    <h2>Ajouter un plat</h2>
    <form method="post">
        Resto ID: <input name="resto_id">
        Nom Plat: <input name="item_name">
        Prix: <input name="item_price">
        <button name="action" value="add_item">Ajouter Plat</button>
    </form>

    <h2>Supprimer un plat</h2>
    <form method="post">
        Resto ID: <input name="resto_id">
        Nom Plat: <input name="item_name">
        <button name="action" value="delete_item">Supprimer Plat</button>
    </form>

    <h2>Restaurants existants</h2>
    {% for rid, data in restaurants.items() %}
        <h3>{{rid}} - {{data.name}}</h3>
        <p>Menu:</p>
        <ul>
        {% for item in data.menu %}
            <li>{{item.name}} - {{item.price}}€</li>
        {% endfor %}
        </ul>
        <p>Total scans: {{data.scans|length}}</p>
        <p>QR Code: <a href="{{base_url}}/qrcode/{{rid}}" target="_blank">{{base_url}}/qrcode/{{rid}}</a></p>
    {% endfor %}
    """
    return render_template_string(html, restaurants=restaurants, message=message, base_url=BASE_URL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)








