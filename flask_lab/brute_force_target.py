from flask import Flask, request, jsonify
import time

app = Flask(__name__)

USERNAME = "admin"
PASSWORD = "correct_password"

attempt_count = 0

@app.route("/login", methods=["POST"])
def login():
    global attempt_count

    attempt_count += 1

    username = request.form.get("username", "")
    password = request.form.get("password", "")

    if username == USERNAME and password == PASSWORD:
        return jsonify({
            "status": "success",
            "message": "Login successful"
        })

    return jsonify({
        "status": "failed",
        "attempt": attempt_count
    }), 401


@app.route("/")
def home():
    return "Controlled Authentication Test Server"


if __name__ == "__main__":
    print("Controlled BRUTE_FORCE target running")
    print("Target: http://127.0.0.1:5051/login")
    app.run(host="127.0.0.1", port=5051, debug=False)