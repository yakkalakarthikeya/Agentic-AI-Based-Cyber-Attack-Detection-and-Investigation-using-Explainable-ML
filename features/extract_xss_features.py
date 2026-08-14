import os
import subprocess
import pandas as pd
import re
from urllib.parse import unquote

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

INPUT_FILE = os.path.join(
    BASE_DIR,
    "capture",
    "xss_01.pcapng"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "xss_01_packets.csv"
)

TSHARK = r"C:\Program Files\Wireshark\tshark.exe"

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

fields = [
    "frame.time_epoch",
    "ip.src",
    "ip.dst",
    "tcp.srcport",
    "tcp.dstport",
    "http.request.method",
    "http.request.uri",
    "http.request.full_uri",
    "http.request.version",
    "http.user_agent",
    "http.request_in",
    "frame.len"
]

command = [
    TSHARK,
    "-r",
    INPUT_FILE,
    "-Y",
    "http.request && tcp.dstport == 5052",
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
        parts += [""] * (len(fields) - len(parts))

    (
        timestamp,
        src_ip,
        dst_ip,
        src_port,
        dst_port,
        method,
        uri,
        full_uri,
        version,
        user_agent,
        request_in,
        frame_length
    ) = parts[:len(fields)]

    if not src_ip or not dst_ip:
        continue

    try:
        decoded_uri = unquote(uri)
    except Exception:
        decoded_uri = uri

    rows.append({
        "timestamp": timestamp,
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "src_port": src_port,
        "dst_port": dst_port,

        "http_method": method,

        "uri_length": len(uri),

        "decoded_uri_length": len(decoded_uri),

        "query_length": (
            len(uri.split("?", 1)[1])
            if "?" in uri
            else 0
        ),

        "special_char_count": len(
            re.findall(
                r"[<>'\"();=]",
                decoded_uri
            )
        ),

        "angle_bracket_count": (
            decoded_uri.count("<")
            + decoded_uri.count(">")
        ),

        "script_keyword_count": (
            decoded_uri.lower().count("script")
        ),

        "event_handler_count": len(
            re.findall(
                r"\bon\w+\s*=",
                decoded_uri.lower()
            )
        ),

        "encoded_char_count": len(
            re.findall(
                r"%[0-9a-fA-F]{2}",
                uri
            )
        ),

        "http_version": version,

        "user_agent_length": len(
            user_agent
        ),

        "frame_length": frame_length,

        "label": "XSS_SIM"
    })


df = pd.DataFrame(rows)

numeric_columns = [
    "timestamp",
    "src_port",
    "dst_port",
    "uri_length",
    "decoded_uri_length",
    "query_length",
    "special_char_count",
    "angle_bracket_count",
    "script_keyword_count",
    "event_handler_count",
    "encoded_char_count",
    "user_agent_length",
    "frame_length"
]

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("XSS feature extraction completed")
print("PCAP:", INPUT_FILE)
print("Rows:", len(df))
print("Output:", OUTPUT_FILE)

print()

if len(df) > 0:
    print(
        df.head(10).to_string(
            index=False
        )
    )
else:
    print("WARNING: No HTTP requests found.")