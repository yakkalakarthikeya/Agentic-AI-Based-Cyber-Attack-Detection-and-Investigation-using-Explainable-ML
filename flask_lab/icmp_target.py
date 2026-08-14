import socket
import threading

HOST = "127.0.0.1"
PORT = 5053

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    server.bind((HOST, PORT))
except PermissionError:
    print("Port 5053 is already in use or blocked.")
    raise SystemExit(1)

print("ICMP_PING_SWEEP controlled lab target running")
print("Listening on:", HOST, PORT)

while True:
    try:
        data, address = server.recvfrom(1024)
        server.sendto(b"ACK", address)
    except KeyboardInterrupt:
        break

server.close()
