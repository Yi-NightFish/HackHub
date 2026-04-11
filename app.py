from flask import Flask
from auth.login import login_bp
from auth.register import register_bp
app = Flask(__name__)
app.secret_key ="hackhubsecretkey"
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
@app.route("/")
def home():
    return "Welcome to HackHub!"
if __name__ == "__main__":
    app.run(debug=True)