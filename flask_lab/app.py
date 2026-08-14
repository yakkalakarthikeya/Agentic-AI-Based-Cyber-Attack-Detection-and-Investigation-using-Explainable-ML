from flask import Flask, jsonify, request, render_template_string
from flask import render_template_string
import random
import time

app = Flask(__name__)

@app.route("/")
def home():
    return "Cyber Attack Investigation Laboratory"

@app.route("/health")
def health():
    return jsonify({
        "server": "running",
        "status": "healthy"
    })

@app.route("/api/data")
def api_data():
    return jsonify({
        "temperature": random.randint(20, 35),
        "users": random.randint(10, 100),
        "status": "active"
    })

@app.route("/search")
def search():
    query = request.args.get("q", "laptop")

    return jsonify({
        "query": query,
        "results": random.randint(1, 20)
    })

@app.route("/login")
def login():
    return jsonify({
        "message": "Login page",
        "status": "available"
    })

@app.route("/normal-test")
def normal_test():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Normal Traffic Generator</title>
    </head>
    <body>
        <h2>Normal Traffic Generator</h2>
        <button onclick="startTraffic()">Start Normal Traffic</button>
        <p id="status">Ready</p>

        <script>
        async function startTraffic() {

            const totalRequests = 5000;

            const endpoints = [
                "/",
                "/health",
                "/api/data",
                "/search?q=laptop",
                "/search?q=phone",
                "/search?q=computer",
                "/search?q=book",
                "/login"
            ];

            for (let i = 1; i <= totalRequests; i++) {

                const endpoint =
                    endpoints[Math.floor(Math.random() * endpoints.length)];

                try {
                    await fetch(endpoint, {
                        method: "GET",
                        cache: "no-store"
                    });

                    document.getElementById("status").innerText =
                        "Normal requests sent: " + i + " / " + totalRequests;

                } catch (error) {
                    console.log(error);
                }

                await new Promise(resolve =>
                    setTimeout(resolve, 100 + Math.random() * 900)
                );
            }

            document.getElementById("status").innerText =
                "Completed 5000 normal requests";
        }
        </script>
    </body>
    </html>
    """

    return render_template_string(html)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )