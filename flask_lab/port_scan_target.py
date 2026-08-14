import socket
import threading

HOST = "127.0.0.1"

PORTS = [p for p in range(5001, 5051) if p != 5040]

def listen_on_port(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, port))
    server.listen(5)

    print(f"Listening on {HOST}:{port}")

    while True:
        try:
            conn, addr = server.accept()
            conn.close()
        except Exception:
            break

threads = []

for port in PORTS:
    thread = threading.Thread(
        target=listen_on_port,
        args=(port,),
        daemon=True
    )
    thread.start()
    threads.append(thread)

print("\nControlled PORT_SCAN target running.")
print("Ports: 5001-5050")
print("Press CTRL+C to stop.")

try:
    while True:
        pass
except KeyboardInterrupt:
    print("\nTarget stopped.")