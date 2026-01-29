from flask import Flask, render_template_string, request, redirect, url_for, send_file
import qrcode
from io import BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'

# Multi-restaurants stocké en mémoire (remplacer par DB pour réel)
restaurants = {}

# Page admin pour un resto
@app.route("/admin/<resto_id>", methods=["GET", "POST"])
def admin(resto_id):
    if resto_id not in restaurants:
        restaurants[resto_id] = {"menu": [], "scans": 0}
    resto = restaurants[resto_id]

    if request.method == "POST":
        name = request.form.get("name")
        price = request.form.get("price")
        if name and price:
            resto["menu"].append({"name": name, "price": price})
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
    <a href="/qrcode/{{resto_id}}">QR Code du menu</a>
    """
    return render_template_string(html, resto=resto, resto_id=resto_id)

# Page client pour voir le menu
@app.route("/menu/<resto_id>")
def menu_page(resto_id):
    if resto_id not in restaurants:
        return "Restaurant inconnu"
    restaurants[resto_id]["scans"] += 1
    resto = restaurants[resto_id]
    html = "<h1>Menu Restaurant</h1><ul>"
    for item in resto["menu"]:
        html += f"<li>{item['name']} - {item['price']} €</li>"
    html += "</ul>"
    return html

# Générer QR code unique par resto
@app.route("/qrcode/<resto_id>")
def generate_qr(resto_id):
    if resto_id not in restaurants:
        return "Restaurant inconnu"
    qr_url = f"https://qr-menu-saas.onrender.com/menu/{resto_id}"  # remplacer par ton URL Render
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype="image/png", download_name=f"qr_{resto_id}.png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)





