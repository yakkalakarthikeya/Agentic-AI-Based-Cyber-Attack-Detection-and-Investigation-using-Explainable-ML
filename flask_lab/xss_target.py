from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    return "XSS controlled lab target"

@app.route("/search")
def search():
    query = request.args.get("q", "")
    return f"Search received: {query}"

@app.route("/comment", methods=["GET", "POST"])
def comment():
    if request.method == "POST":
        comment = request.form.get("comment", "")
        return f"Comment received: {comment}"

    return "Comment endpoint"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        return f"Login attempt for: {username}"

    return "Login page"

if __name__ == "__main__":
    print("XSS controlled lab target running")
    print("URL: http://127.0.0.1:5052")
    app.run(host="127.0.0.1", port=5052)