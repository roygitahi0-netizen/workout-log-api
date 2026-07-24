"""
App configuration.

Sets up the Flask app, database, migrations, password hashing, RESTful
routing, and CORS (so a separately-hosted frontend can send/receive the
session cookie during local development).
"""
import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
app.json.compact = False

# Cross-origin session cookies for local dev (frontend runs on a different
# port than the API). In production, lock allow origins down and serve both
# over HTTPS so SameSite=None; Secure cookies work correctly.
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("FLASK_ENV") == "production"

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
api = Api(app)

CORS(
    app,
    supports_credentials=True,
    origins=os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000").split(","),
)
