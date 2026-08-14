import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "icmp_ping_01_packets.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "icmp_ping_01_flows.csv"
)

df = pd.read_csv(INPUT_FILE)

required_columns = [
    "timestamp",
    "src_ip",
    "dst_ip",
    "icmp_type",
    "icmp_code",
    "frame_length",
    "ttl"
]

missing = [
    col for col in required_columns
    if col not in df.columns
]

if missing:
    print("Missing columns:", missing)
    raise SystemExit(1)

numeric_columns = [
    "timestamp",
    "icmp_type",
    "icmp_code",
    "frame_length",
    "ttl"
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
        "icmp_type",
        "frame_length"
    ]
)

df = df.sort_values("timestamp").reset_index(drop=True)

if df.empty:
    print("No valid ICMP records found.")
    raise SystemExit(1)

WINDOW_SIZE = 1.0

start_time = df["timestamp"].min()

df["window_id"] = (
    (df["timestamp"] - start_time)
    // WINDOW_SIZE
).astype(int)

flows = []

for window_id, group in df.groupby("window_id"):

    group = group.sort_values("timestamp")

    start = group["timestamp"].min()
    end = group["timestamp"].max()

    duration = end - start

    packet_count = len(group)

    total_bytes = group[
        "frame_length"
    ].sum()

    request_count = (
        group["icmp_type"] == 8
    ).sum()

    reply_count = (
        group["icmp_type"] == 0
    ).sum()

    other_icmp_count = (
        ~group["icmp_type"].isin([0, 8])
    ).sum()

    avg_packet_length = (
        group["frame_length"].mean()
    )

    min_packet_length = (
        group["frame_length"].min()
    )

    max_packet_length = (
        group["frame_length"].max()
    )

    avg_ttl = group["ttl"].mean()

    packet_rate = (
        packet_count / WINDOW_SIZE
    )

    byte_rate = (
        total_bytes / WINDOW_SIZE
    )

    request_reply_ratio = (
        request_count / reply_count
        if reply_count > 0
        else request_count
    )

    flows.append({

        "flow_id": f"ICMP_{window_id}",

        "src_ip": group[
            "src_ip"
        ].mode().iloc[0],

        "dst_ip": group[
            "dst_ip"
        ].mode().iloc[0],

        "flow_duration": duration,

        "total_packets": packet_count,

        "total_bytes": total_bytes,

        "icmp_request_count": request_count,

        "icmp_reply_count": reply_count,

        "icmp_other_count": other_icmp_count,

        "request_reply_ratio": request_reply_ratio,

        "packet_rate": packet_rate,

        "byte_rate": byte_rate,

        "avg_packet_length": avg_packet_length,

        "min_packet_length": min_packet_length,

        "max_packet_length": max_packet_length,

        "avg_ttl": avg_ttl,

        "label": "ICMP_TRAFFIC"
    })


flow_df = pd.DataFrame(flows)

flow_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("ICMP flow extraction completed")
print("Packet rows:", len(df))
print("Flow rows:", len(flow_df))
print("Output:", OUTPUT_FILE)

print()
print(
    flow_df.head(10).to_string(
        index=False
    )
)