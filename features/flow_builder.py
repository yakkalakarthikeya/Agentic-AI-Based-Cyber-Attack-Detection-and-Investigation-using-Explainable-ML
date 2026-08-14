import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "http_flood_01_packets.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "http_flood_01_flows.csv"
)

if not os.path.exists(INPUT_FILE):
    print("Input file not found:")
    print(INPUT_FILE)
    raise SystemExit(1)

df = pd.read_csv(INPUT_FILE)

if df.empty:
    print("Input CSV is empty.")
    raise SystemExit(1)

required_columns = [
    "timestamp",
    "src_ip",
    "dst_ip",
    "src_port",
    "dst_port",
    "tcp_flags",
    "frame_length",
    "tcp_length"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    print("Missing columns:")
    print(missing_columns)
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
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

df = df.dropna(
    subset=[
        "timestamp",
        "src_ip",
        "dst_ip",
        "src_port",
        "dst_port"
    ]
)

if df.empty:
    print("No valid packet records after cleaning.")
    raise SystemExit(1)

df["flow_id"] = (
    df["src_ip"].astype(str)
    + "-"
    + df["dst_ip"].astype(str)
    + "-"
    + df["src_port"].astype(str)
    + "-"
    + df["dst_port"].astype(str)
)

flows = []

for flow_id, group in df.groupby("flow_id"):

    group = group.sort_values("timestamp")

    duration = (
        group["timestamp"].max()
        - group["timestamp"].min()
    )

    packet_count = len(group)

    total_bytes = group["frame_length"].sum()

    first_src = group["src_ip"].iloc[0]

    forward = group[
        group["src_ip"] == first_src
    ]

    backward = group[
        group["src_ip"] != first_src
    ]

    forward_packets = len(forward)
    backward_packets = len(backward)

    forward_bytes = forward["frame_length"].sum()
    backward_bytes = backward["frame_length"].sum()

    packet_rate = (
        packet_count / duration
        if duration > 0
        else 0
    )

    byte_rate = (
        total_bytes / duration
        if duration > 0
        else 0
    )

    tcp_flags = group["tcp_flags"].fillna(0).astype(int)

    flows.append({
        "flow_id": flow_id,

        "src_ip": group["src_ip"].iloc[0],
        "dst_ip": group["dst_ip"].iloc[0],

        "src_port": group["src_port"].iloc[0],
        "dst_port": group["dst_port"].iloc[0],

        "flow_duration": duration,

        "total_packets": packet_count,
        "total_bytes": total_bytes,

        "forward_packets": forward_packets,
        "backward_packets": backward_packets,

        "forward_bytes": forward_bytes,
        "backward_bytes": backward_bytes,

        "packet_rate": packet_rate,
        "byte_rate": byte_rate,

        "avg_packet_length": group["frame_length"].mean(),
        "min_packet_length": group["frame_length"].min(),
        "max_packet_length": group["frame_length"].max(),

        "tcp_syn_count": (
            (tcp_flags & 0x0002) != 0
        ).sum(),

        "tcp_fin_count": (
            (tcp_flags & 0x0001) != 0
        ).sum(),

        "tcp_ack_count": (
            (tcp_flags & 0x0010) != 0
        ).sum(),

        "label": "HTTP_FLOOD"
    })

flow_df = pd.DataFrame(flows)

flow_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Flow extraction completed")
print("Packet rows:", len(df))
print("Flow rows:", len(flow_df))
print("Output:", OUTPUT_FILE)

print()
print(flow_df.head(10).to_string(index=False))