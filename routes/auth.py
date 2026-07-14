from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from bson.objectid import ObjectId

from models.db import users_collection

auth_bp = Blueprint("auth", __name__)


# ---------- User class for Flask-Login ----------
class User(UserMixin):
    """Wraps a MongoDB user document so Flask-Login can use it."""
    def __init__(self, user_doc):
        self.id = str(user_doc["_id"])
        self.username = user_doc["username"]
        self.email = user_doc["email"]

    @staticmethod
    def get(user_id):
        user_doc = users_collection.find_one({"_id": ObjectId(user_id)})
        return User(user_doc) if user_doc else None


# ---------- Forms ----------
class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


# ---------- Routes ----------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing = users_collection.find_one({"email": form.email.data})
        if existing:
            flash("An account with that email already exists.", "danger")
            return redirect(url_for("auth.register"))

        hashed_pw = generate_password_hash(form.password.data)
        users_collection.insert_one({
            "username": form.username.data,
            "email": form.email.data,
            "password_hash": hashed_pw,
        })
        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_doc = users_collection.find_one({"email": form.email.data})
        if user_doc and check_password_hash(user_doc["password_hash"], form.password.data):
            login_user(User(user_doc))
            flash("Logged in successfully.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("posts.index"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))