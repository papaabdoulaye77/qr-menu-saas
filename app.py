from flask import Flask, render_template_string, request, redirect, url_for, send_file
import qrcode
from io import BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'

# Base de données en mémoire
restaurants = {}

# Dashboard central
@app.route("/admin")
def central_dashboard():
    html = "<h1>Dashboard Central</h1><ul>"
    for rid, rdata in restaurants.items():
        html += f"<li>{rid} - Plats: {len(rdata['menu'])} - Scans: {rdata['scans']} - <a href='/admin/{rid}'>Admin</a> - <a href='/menu/{rid}'>Menu</a> - <a href='/qrcode/{rid}'>QR Code</a></li>"
    html += "</ul><br>"
    html += """
    <form method="post" action="/create_resto">
        <input name="resto_id" placeholder="Nom du resto" required>
        <button>Créer nouveau resto</button>
    </form>
    """
    return html

# Créer un nouveau resto
@app.route("/create_resto", methods=["POST"])
def create_resto():
    resto_id = request.form.get("resto_id")
    if resto_id and resto_id not in restaurants:
        restaurants[resto_id] = {"menu": [], "scans": 0}
    return redirect("/admin")

# Admin pour un resto
@app.route("/admin/<resto_id>", methods=["GET","POST"])
def admin(resto_id):
    if resto_id not in restaurants:
        return "Resto inconnu"
    resto = restaurants[resto_id]
    if request.method=="POST":
        name = request.form.get("name")
        price = request.form.get("price")
        if name and price:
            resto["menu"].append({"name":name,"price":price})
        return redirect(url_for("admin", resto_id=resto_id))
    html = """
    <h1>Dashboard {{resto_id}}</h1>
    <form method="post">
        <input name="name" placeholder="Plat" required>
        <input name="price" placeholder="Prix" required>
        <button>Ajouter</button>
    </form>
    <h2>Menu actuel</h2>
    <ul>
    {% for item in resto['menu'] %}
        <li>{{item['name']}} - {{item['price']}} €</li>
    {% endfor %}
    </ul>
    <h2>Stats</h2>
    <p>Scans QR code : {{resto['scans']}}</p>
    <a href="/menu/{{resto_id}}">Voir le menu client</a><br>
    <a href="/qrcode/{{resto_id}}">QR Code du menu</a><br>
    <a href="/admin">Dashboard central</a>
    """
    return render_template_string(html, resto=resto, resto_id=resto_id)

# Menu client
@app.route("/menu/<resto_id>")
def menu_page(resto_id):
    if resto_id not in restaurants:
        return "Resto inconnu"
    restaurants[resto_id]["scans"] += 1
    resto = restaurants[resto_id]
    html = "<h1>Menu Restaurant</h1><ul>"
    for item in resto["menu"]:
        html += f"<li>{item['name']} - {item['price']} €</li>"
    html += "</ul>"
    return html

# QR code automatique
@app.route("/qrcode/<resto_id>")
def generate_qr(resto_id):
    if resto_id not in restaurants:
        return "Resto inconnu"
    qr_url = f"https://qr-menu-saas.onrender.com/menu/resto"  # METTRE TON URL RENDER
    qr = qrcode.QRCode(box_size=10,border=4)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype="image/png", download_name=f"qr_{resto_id}.png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)






