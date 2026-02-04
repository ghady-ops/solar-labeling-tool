from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
import csv, os
from datetime import datetime

app = Flask(__name__)

IMAGES_DIR = "images"
LABELS = "labels.csv"


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
    with open(LABELS, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            data["image"],
            data["label"],
            data.get("notes", ""),
            datetime.now().isoformat()
        ])
    return jsonify(ok=True)


@app.route("/export")
def export():
    return send_file(LABELS, as_attachment=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
