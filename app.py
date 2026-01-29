from flask import Flask, send_file
import qrcode
import io

app = Flask(__name__)

menus = {
    "resto1": [
        {"name": "Pizza Margherita", "price": 9},
        {"name": "Pizza Pepperoni", "price": 11},
        {"name": "Coca-Cola", "price": 3}
    ],
    "resto2": [
        {"name": "Burger", "price": 10},
        {"name": "Frites", "price": 4},
        {"name": "Eau", "price": 2}
    ]
}

@app.route("/")
def home():
    return "QR Menu SaaS is running"

@app.route("/menu/<resto_id>")
def menu(resto_id):
    if resto_id not in menus:
        return "Restaurant introuvable", 404

    html = f"<h1>Menu {resto_id}</h1>"
    for item in menus[resto_id]:
        html += f"<p>{item['name']} - {item['price']}€</p>"
    return html

@app.route("/qrcode/<resto_id>")
def qrcode_menu(resto_id):
    url = f"http://127.0.0.1:5000/menu/{resto_id}"

    img = qrcode.make(url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return send_file(buffer, mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


