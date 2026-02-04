from flask import Flask, render_template, request, jsonify, send_from_directory, send_file, session
import csv, os
from datetime import datetime

app = Flask(__name__)

# مهم للسشن (حطيه في Render كمتغير بيئة SECRET_KEY)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

IMAGES_DIR = "images"
LABELS_DIR = "labels"  # مجلد نحط فيه ملفات كل شخص

os.makedirs(LABELS_DIR, exist_ok=True)


def get_sid() -> str:
    """Unique id per browser session"""
    sid = session.get("sid")
    if not sid:
        sid = os.urandom(16).hex()
        session["sid"] = sid
    return sid


def user_labels_path() -> str:
    sid = get_sid()
    return os.path.join(LABELS_DIR, f"labels_{sid}.csv")


@app.route("/")
def index():
    images = os.listdir(IMAGES_DIR)
    return render_template("index.html", images=images)


@app.route("/images/<path:name>")
def images(name):
    return send_from_directory(IMAGES_DIR, name)


@app.route("/label", methods=["POST"])
def label():
    data = request.json
    path = user_labels_path()

    with open(path, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            data["image"],
            data["label"],
            data.get("notes", ""),
            datetime.now().isoformat()
        ])
    return jsonify(ok=True)


@app.route("/export")
def export():
    path = user_labels_path()

    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return jsonify(ok=False, message="No results to export yet."), 400

    # ينزل ملف المستخدم فقط
    response = send_file(path, as_attachment=True, download_name="labels.csv")

    # يصفّر ملفه فقط بعد التصدير
    open(path, "w", encoding="utf-8").close()

    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
