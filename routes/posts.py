#posts.py
from datetime import datetime, timezone

from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from bson.objectid import ObjectId

from models.db import posts_collection

posts_bp = Blueprint("posts", __name__)


# ---------- Form ----------
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=120)])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Save")


# ---------- Routes ----------
@posts_bp.route("/")
def index():
    all_posts = list(posts_collection.find().sort("created_at", -1))
    return render_template("index.html", posts=all_posts)


@posts_bp.route("/post/<post_id>")
def view_post(post_id):
    post = posts_collection.find_one({"_id": ObjectId(post_id)})
    if not post:
        abort(404)
    return render_template("post.html", post=post)


@posts_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        posts_collection.insert_one({
            "title": form.title.data,
            "content": form.content.data,
            "user_id": current_user.id,          # reference to the users collection
            "author": current_user.username,       # denormalized for easy display
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        })
        flash("Post created!", "success")
        return redirect(url_for("posts.index"))

    return render_template("create_post.html", form=form)


@posts_bp.route("/post/<post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = posts_collection.find_one({"_id": ObjectId(post_id)})
    if not post:
        abort(404)
    if post["user_id"] != current_user.id:
        flash("You can only edit your own posts.", "danger")
        return redirect(url_for("posts.index"))

    form = PostForm(data={"title": post["title"], "content": post["content"]})
    if form.validate_on_submit():
        posts_collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {
                "title": form.title.data,
                "content": form.content.data,
                "updated_at": datetime.now(timezone.utc),
            }}
        )
        flash("Post updated!", "success")
        return redirect(url_for("posts.view_post", post_id=post_id))

    return render_template("create_post.html", form=form, editing=True)


@posts_bp.route("/post/<post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = posts_collection.find_one({"_id": ObjectId(post_id)})
    if not post:
        abort(404)
    if post["user_id"] != current_user.id:
        flash("You can only delete your own posts.", "danger")
        return redirect(url_for("posts.index"))

    posts_collection.delete_one({"_id": ObjectId(post_id)})
    flash("Post deleted.", "info")
    return redirect(url_for("posts.index"))