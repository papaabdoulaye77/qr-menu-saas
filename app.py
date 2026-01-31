from flask import Flask, send_file, request, render_template_string, redirect, url_for
import qrcode
import io

app = Flask(__name__)

# Base URL de Render
BASE_URL = "https://qr-menu-saas.onrender.com"  # remplace par ton URL Render

# Données restaurants (dictionnaire)
restaurants = {
    "resto1": {
        "name": "Pizza Palace",
        "menu": [
            {"name": "Pizza Margherita", "price": 9},
            {"name": "Pizza Pepperoni", "price": 11},
            {"name": "Coca-Cola", "price": 3}
        ],
        "scans": 0
    },
    "resto2": {
        "name": "Burger House",
        "menu": [
            {"name": "Burger", "price": 10},
            {"name": "Frites", "price": 4},
            {"name": "Eau", "price": 2}
        ],
        "scans": 0
    }
}

# ================== ROUTES CLIENT ==================

@app.route("/")
def home():
    return "QR Menu SaaS is running"

@app.route("/menu/<resto_id>")
def menu(resto_id):
    if resto_id not in restaurants:
        return "Restaurant introuvable", 404
    restaurants[resto_id]["scans"] += 1
    html = f"<h1>{restaurants[resto_id]['name']}</h1>"
    for item in restaurants[resto_id]["menu"]:
        html += f"<p>{item['name']} - {item['price']}€</p>"
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
    return f"Nombre de scans pour {restaurants[resto_id]['name']} : {restaurants[resto_id]['scans']}"

# ================== ROUTES ADMIN ==================

# Page admin avec formulaire simple
@app.route("/admin", methods=["GET", "POST"])
def admin():
    message = ""
    if request.method == "POST":
        action = request.form.get("action")
        resto_id = request.form.get("resto_id")
        name = request.form.get("name")
        item_name = request.form.get("item_name")
        item_price = request.form.get("item_price")

        # Ajouter un nouveau resto
        if action == "add_resto" and resto_id and name:
            if resto_id in restaurants:
                message = f"Le resto {resto_id} existe déjà"
            else:
                restaurants[resto_id] = {"name": name, "menu": [], "scans": 0}
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

    # Page HTML très simple
    html = """
    <h1>Admin QR Menu SaaS</h1>
    <p style="color: red;">{{message}}</p>

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
        <p>Scans: {{data.scans}}</p>
    {% endfor %}
    """
    return render_template_string(html, restaurants=restaurants, message=message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)






