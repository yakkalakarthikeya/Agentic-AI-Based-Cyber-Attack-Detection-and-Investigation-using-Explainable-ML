import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "dns_tunneling_01_packets.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "dns_tunneling_01_flows.csv"
)

if not os.path.exists(INPUT_FILE):
    print("Input file not found:")
    print(INPUT_FILE)
    raise SystemExit(1)

df = pd.read_csv(INPUT_FILE)

required_columns = [
    "timestamp",
    "src_ip",
    "dst_ip",
    "src_port",
    "dst_port",
    "frame_length",
    "udp_length"
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
    "frame_length",
    "udp_length"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

df = df.dropna(
    subset=required_columns
)

if df.empty:
    print("No valid packet records found.")
    raise SystemExit(1)

df = df.sort_values("timestamp")

start_time = df["timestamp"].min()

WINDOW_SIZE = 20

df = df.reset_index(drop=True)

df["time_window"] = (
    df.index // WINDOW_SIZE
)

df["endpoint_a"] = (
    df["src_ip"].astype(str)
    + ":"
    + df["src_port"].astype(str)
)

df["endpoint_b"] = (
    df["dst_ip"].astype(str)
    + ":"
    + df["dst_port"].astype(str)
)

df["endpoint_1"] = df[
    ["endpoint_a", "endpoint_b"]
].min(axis=1)

df["endpoint_2"] = df[
    ["endpoint_a", "endpoint_b"]
].max(axis=1)

df["flow_key"] = (
    df["endpoint_1"]
    + "-"
    + df["endpoint_2"]
    + "-"
    + df["time_window"].astype(str)
)

flows = []

for flow_id, group in df.groupby("flow_key"):

    group = group.sort_values("timestamp")

    first_src = group["src_ip"].iloc[0]

    forward = group[
        group["src_ip"] == first_src
    ]

    backward = group[
        group["src_ip"] != first_src
    ]

    duration = (
        group["timestamp"].max()
        - group["timestamp"].min()
    )

    total_packets = len(group)

    total_bytes = group[
        "frame_length"
    ].sum()

    forward_packets = len(forward)

    backward_packets = len(backward)

    forward_bytes = forward[
        "frame_length"
    ].sum()

    backward_bytes = backward[
        "frame_length"
    ].sum()

    packet_rate = (
        total_packets / duration
        if duration > 0
        else total_packets
    )

    byte_rate = (
        total_bytes / duration
        if duration > 0
        else total_bytes
    )

    flows.append({

        "flow_id": flow_id,

        "src_ip": group[
            "src_ip"
        ].iloc[0],

        "dst_ip": group[
            "dst_ip"
        ].iloc[0],

        "src_port": group[
            "src_port"
        ].iloc[0],

        "dst_port": group[
            "dst_port"
        ].iloc[0],

        "flow_duration": duration,

        "total_packets": total_packets,

        "total_bytes": total_bytes,

        "forward_packets": forward_packets,

        "backward_packets": backward_packets,

        "forward_bytes": forward_bytes,

        "backward_bytes": backward_bytes,

        "packet_rate": packet_rate,

        "byte_rate": byte_rate,

        "avg_packet_length": group[
            "frame_length"
        ].mean(),

        "min_packet_length": group[
            "frame_length"
        ].min(),

        "max_packet_length": group[
            "frame_length"
        ].max(),

        "avg_udp_length": group[
            "udp_length"
        ].mean(),

        "min_udp_length": group[
            "udp_length"
        ].min(),

        "max_udp_length": group[
            "udp_length"
        ].max(),

        "label": "DNS_TUNNELING_SIM"
    })

flow_df = pd.DataFrame(flows)

flow_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("DNS time-window flow extraction completed")
print("Packet rows:", len(df))
print("Flow rows:", len(flow_df))
print("Output:", OUTPUT_FILE)

print()

print(
    flow_df.head(10).to_string(
        index=False
    )
)