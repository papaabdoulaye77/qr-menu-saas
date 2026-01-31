from flask import Flask
import qrcode
import io
from flask import send_file

app = Flask(__name__)

BASE_URL = "https://qr-menu-saas.onrender.com"  # ⚠️ À CHANGER

@app.route("/")
def home():
    return "QR MENU SaaS is running"

@app.route("/menu/<id>")
def menu(id):
    return f"""
    <h1>Menu du restaurant {id}</h1>
    <ul>
        <li>Pizza - 10€</li>
        <li>Pasta - 9€</li>
        <li>Soda - 3€</li>
    </ul>
    """

@app.route("/qr/<id>")
def qr(id):
    url = f"{BASE_URL}/menu/{id}"
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

if __name__ == "__main__":
    app.run()








