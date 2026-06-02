import os
from flask import Flask, render_template

COWORK_DIR = os.path.expanduser("~/Downloads/CoWork")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

app = Flask(__name__)

os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
