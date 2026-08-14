from flask import Flask

app = Flask(__name__)

request_count = 0

@app.route("/")
def home():
    global request_count
    request_count += 1

    return {
        "status": "ok",
        "request_count": request_count
    }


@app.route("/test")
def test():
    return {
        "status": "test"
    }


if __name__ == "__main__":
    print("Controlled HTTP_FLOOD target running")
    print("Target: http://127.0.0.1:5052")
    app.run(
        host="127.0.0.1",
        port=5052,
        debug=False
    )