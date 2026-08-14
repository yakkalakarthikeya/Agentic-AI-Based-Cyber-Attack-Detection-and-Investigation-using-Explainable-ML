import socket

HOST = "127.0.0.1"
PORT = 5354

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))

print("Controlled DNS_TUNNELING_SIM target running")
print("Target: 127.0.0.1:5353")
print("Press CTRL+C to stop")

while True:
    data, address = server.recvfrom(4096)

    if len(data) >= 12:
        transaction_id = data[:2]

        response = (
            transaction_id +
            b"\x81\x83" +
            data[4:6] +
            b"\x00\x00" +
            b"\x00\x00" +
            b"\x00\x00"
        )

        server.sendto(response, address)