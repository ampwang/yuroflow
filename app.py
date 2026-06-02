import os
from flask import Flask, render_template, jsonify, request
import google_client
import image_scanner
import image_processor

COWORK_DIR = os.path.expanduser("~/Downloads/CoWork")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
SPREADSHEET_ID = "16h9zxHXVz0CxznKGe-SSjD8OVrFZLElv2dmBuKnuh10"
SHEET_NAME = "Sheet1"

app = Flask(__name__)

os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/auth")
def auth():
    try:
        google_client.run_auth_flow()
        return jsonify({"ok": True, "message": "Authenticated successfully."})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/test-sheets")
def test_sheets():
    result = google_client.test_sheets_connection(SPREADSHEET_ID)
    status = 200 if result["ok"] else 500
    return jsonify(result), status



@app.route("/api/sheet-rows")
def sheet_rows():
    result = google_client.fetch_sheet_rows(SPREADSHEET_ID, SHEET_NAME)
    status = 200 if result["ok"] else 500
    return jsonify(result), status


@app.route("/api/images")
def images():
    result = image_scanner.scan(COWORK_DIR)
    return jsonify(result)


@app.route("/api/process", methods=["POST"])
def process_images():
    pairs = request.json
    results = []
    for pair in pairs:
        source = os.path.join(COWORK_DIR, pair["image"])
        output = os.path.join(OUTPUT_DIR, pair["date"] + ".jpg")
        try:
            image_processor.process(source, output, pair["line1"], pair["line2"])
            results.append({"date": pair["date"], "ok": True})
        except Exception as e:
            results.append({"date": pair["date"], "ok": False, "error": str(e)})
    return jsonify({"results": results})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
