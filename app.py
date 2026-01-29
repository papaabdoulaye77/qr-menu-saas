from flask import Flask, render_template_string, request, redirect, url_for, send_file
import qrcode
from io import BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'

# Menu stocké en mémoire
menu = []

# Page principale pour ajouter des plats
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        menu.append({"name": name, "price": price})
        return redirect(url_for("home"))
    html = """
    <h1>Dashboard Restaurant</h1>
    <form method="post">
        <input name="name" placeholder="Plat" required>
        <input name="price" placeholder="Prix" required>
        <button>Ajouter</button>
    </form>
    <h2>Menu actuel</h2>
    <ul>
    {% for item in menu %}
        <li>{{item['name']}} - {{item['price']}} €</li>
    {% endfor %}
    </ul>
    <a href="/menu">Voir le menu client</a><br>
    <a href="/qrcode">QR Code du menu</a>
    """
    return render_template_string(html, menu=menu)

# Page client pour voir le menu
@app.route("/menu")
def menu_page():
    html = "<h1>Menu Restaurant</h1><ul>"
    for item in menu:
        html += f"<li>{item['name']} - {item['price']} €</li>"
    html += "</ul>"
    return html

# Générer QR code du menu
@app.route("/qrcode")
def generate_qr():
    qr_url = "http://qr-menu-saas.onrender.com/menu"
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype="image/png", download_name="qr_menu.png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)




