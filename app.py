import os
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv

from routes.auth import auth_bp, User
from routes.posts import posts_bp

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

# ---------- Flask-Login setup ----------
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# ---------- Register blueprints ----------
app.register_blueprint(auth_bp)
app.register_blueprint(posts_bp)


if __name__ == "__main__":
    app.run(debug=True)