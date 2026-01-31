from flask import Flask, send_file
import qrcode
import io

app = Flask(__name__)

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

BASE_URL = "https://qr-menu-saas.onrender.com"  # remplace par ton URL Render

@app.route("/")
def home():
    return "QR Menu SaaS is running"

@app.route("/menu/<resto_id>")
def menu(resto_id):
    if resto_id not in restaurants:
        return "Restaurant introuvable", 404

    restaurants[resto_id]["scans"] += 1  # compte le scan

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)




