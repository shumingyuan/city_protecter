import os
import uuid
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import qrcode

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
REWARDS_DIR = os.path.join(BASE_DIR, "static", "rewards")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REWARDS_DIR, exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

db = SQLAlchemy(app)


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    image_filename = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


def is_allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "").strip()
    file = request.files.get("photo")

    if not name:
        flash("请填写您的名字。", "error")
        return redirect(url_for("index"))

    if not file or file.filename == "":
        flash("请上传一张图片。", "error")
        return redirect(url_for("index"))

    if not is_allowed_file(file.filename):
        flash("仅支持 png/jpg/jpeg/gif/webp 图片格式。", "error")
        return redirect(url_for("index"))

    # Persist image
    extension = file.filename.rsplit(".", 1)[1].lower()
    image_filename = f"{uuid.uuid4().hex}.{extension}"
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
    file.save(image_path)

    # Create a unique token and QR code pointing to the reward page
    token = uuid.uuid4().hex
    reward_url = url_for("reward", token=token, _external=True)

    qr_img = qrcode.make(reward_url)
    qr_filename = f"qr_{token}.png"
    qr_path = os.path.join(REWARDS_DIR, qr_filename)
    qr_img.save(qr_path)

    # Save to DB
    submission = Submission(name=name, image_filename=image_filename, token=token)
    db.session.add(submission)
    db.session.commit()

    return redirect(url_for("success", token=token))


@app.route("/success/<token>")
def success(token: str):
    submission = Submission.query.filter_by(token=token).first_or_404()
    qr_filename = f"qr_{submission.token}.png"
    return render_template("success.html", submission=submission, qr_file=qr_filename)


@app.route("/reward/<token>")
def reward(token: str):
    submission = Submission.query.filter_by(token=token).first_or_404()
    return render_template("reward.html", submission=submission)


@app.route("/wall")
def wall():
    submissions = Submission.query.order_by(Submission.created_at.desc()).all()
    return render_template("wall.html", submissions=submissions)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename: str):
    return send_from_directory(UPLOAD_DIR, filename)


@app.cli.command("init-db")
def init_db_command():
    """Initialize the database tables."""
    db.create_all()
    print("Initialized the database.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)