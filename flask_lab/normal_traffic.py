import requests
import time
import random

BASE_URL = "http://127.0.0.1:5000"

def generate_normal_traffic():
    urls = [
        f"{BASE_URL}/",
        f"{BASE_URL}/health",
        f"{BASE_URL}/api/data",
        f"{BASE_URL}/search?q=laptop",
        f"{BASE_URL}/search?q=phone"
    ]

    for i in range(100):
        url = random.choice(urls)

        try:
            response = requests.get(url, timeout=5)
            print(
                f"{i + 1:03d} | "
                f"{response.status_code} | "
                f"{url}"
            )
        except requests.RequestException as e:
            print(f"Request failed: {e}")

        time.sleep(random.uniform(0.2, 1.0))

if __name__ == "__main__":
    generate_normal_traffic()