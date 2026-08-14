import socket
import random
import string
import struct
import time

SERVER = ("127.0.0.1", 5354)

def random_label(length):
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))

def encode_domain(domain):
    result = b""

    for part in domain.split("."):
        result += bytes([len(part)])
        result += part.encode()

    return result + b"\x00"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for i in range(2000):
    transaction_id = random.randint(0, 65535)

    domain = (
        random_label(random.randint(25, 45))
        + "."
        + random_label(random.randint(15, 30))
        + ".lab"
    )

    header = struct.pack(
        "!HHHHHH",
        transaction_id,
        0x0100,
        1,
        0,
        0,
        0
    )

    question = (
        encode_domain(domain)
        + struct.pack("!HH", 1, 1)
    )

    packet = header + question

    sock.sendto(packet, SERVER)

    time.sleep(0.002)

sock.close()

print("DNS_TUNNELING_SIM traffic generation completed")