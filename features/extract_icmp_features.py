import os
import subprocess
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE = os.path.join(
    BASE_DIR,
    "capture",
    "icmp_ping_01.pcapng"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "icmp_ping_01_packets.csv"
)

TSHARK = r"C:\Program Files\Wireshark\tshark.exe"

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

display_filter = "icmp && ip.addr == 127.0.0.1"

fields = [
    "frame.time_epoch",
    "ip.src",
    "ip.dst",
    "icmp.type",
    "icmp.code",
    "frame.len",
    "ip.ttl"
]

command = [
    TSHARK,
    "-r",
    INPUT_FILE,
    "-Y",
    display_filter,
    "-T",
    "fields"
]

for field in fields:
    command.extend(["-e", field])

command.extend([
    "-E", "separator=\t",
    "-E", "quote=n",
    "-E", "header=n"
])

result = subprocess.run(
    command,
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace"
)

if result.returncode != 0:
    print("TShark error:")
    print(result.stderr)
    raise SystemExit(1)

rows = []

for line in result.stdout.splitlines():

    parts = line.split("\t")

    if len(parts) < len(fields):
        continue

    timestamp, src_ip, dst_ip, icmp_type, icmp_code, frame_length, ttl = parts

    if not src_ip or not dst_ip:
        continue

    rows.append({
        "timestamp": timestamp,
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "icmp_type": icmp_type,
        "icmp_code": icmp_code,
        "frame_length": frame_length,
        "ttl": ttl,
        "label": "ICMP_TRAFFIC"
    })

df = pd.DataFrame(rows)

numeric_columns = [
    "timestamp",
    "icmp_type",
    "icmp_code",
    "frame_length",
    "ttl"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(
    subset=[
        "timestamp",
        "src_ip",
        "dst_ip",
        "icmp_type",
        "frame_length"
    ]
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("ICMP extraction completed")
print("PCAP:", INPUT_FILE)
print("Rows:", len(df))
print("Output:", OUTPUT_FILE)

print()
print(df.head(10).to_string(index=False))