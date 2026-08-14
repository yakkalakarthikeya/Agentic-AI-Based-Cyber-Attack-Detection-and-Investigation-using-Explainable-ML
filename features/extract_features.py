import os
import subprocess
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE = os.path.join(
    BASE_DIR,
    "capture",
    "http_flood_01.pcapng"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "http_flood_01_packets.csv"
)

TSHARK = r"C:\Program Files\Wireshark\tshark.exe"

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

display_filter = "tcp.dstport == 5052"

fields = [
    "frame.time_epoch",
    "ip.src",
    "ip.dst",
    "tcp.srcport",
    "tcp.dstport",
    "tcp.flags",
    "frame.len",
    "tcp.len"
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

    timestamp, src_ip, dst_ip, src_port, dst_port, tcp_flags, frame_length, tcp_length = parts

    if not src_ip or not dst_ip or not src_port or not dst_port:
        continue

    rows.append({
        "timestamp": timestamp,
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "src_port": src_port,
        "dst_port": dst_port,
        "tcp_flags": tcp_flags,
        "frame_length": frame_length,
        "tcp_length": tcp_length,
        "label": "HTTP_FLOOD"
    })

df = pd.DataFrame(rows)

if df.empty:
    print("No matching packets found.")
    print("Check that the PCAP contains traffic on TCP port 5051.")
    raise SystemExit(1)

numeric_columns = [
    "timestamp",
    "src_port",
    "dst_port",
    "tcp_flags",
    "frame_length",
    "tcp_length"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(
    subset=[
        "timestamp",
        "src_ip",
        "dst_ip",
        "src_port",
        "dst_port"
    ]
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Extraction completed")
print("PCAP:", INPUT_FILE)
print("Rows:", len(df))
print("Output:", OUTPUT_FILE)

print()
print(df.head(10).to_string(index=False))