import pandas as pd
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "xss_01_packets.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "xss_01_flows.csv"
)

df = pd.read_csv(INPUT_FILE)

if df.empty:
    print("No XSS records found.")
    raise SystemExit(1)

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

df = df.dropna(
    subset=["timestamp", "src_ip", "dst_ip"]
)

df = df.sort_values("timestamp").reset_index(drop=True)

WINDOW_SIZE = 20

df["window_id"] = (
    df.index // WINDOW_SIZE
)

flows = []

for window_id, group in df.groupby("window_id"):

    duration = (
        group["timestamp"].max()
        - group["timestamp"].min()
    )

    packet_count = len(group)

    total_bytes = group[
        "frame_length"
    ].sum()

    flows.append({

        "flow_id": f"XSS_{window_id}",

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

        "total_requests": packet_count,

        "total_bytes": total_bytes,

        "request_rate": (
            packet_count / duration
            if duration > 0
            else packet_count
        ),

        "avg_uri_length": group[
            "uri_length"
        ].mean(),

        "max_uri_length": group[
            "uri_length"
        ].max(),

        "avg_query_length": group[
            "query_length"
        ].mean(),

        "avg_special_char_count": group[
            "special_char_count"
        ].mean(),

        "total_angle_bracket_count": group[
            "angle_bracket_count"
        ].sum(),

        "total_script_keyword_count": group[
            "script_keyword_count"
        ].sum(),

        "total_event_handler_count": group[
            "event_handler_count"
        ].sum(),

        "total_encoded_char_count": group[
            "encoded_char_count"
        ].sum(),

        "avg_user_agent_length": group[
            "user_agent_length"
        ].mean(),

        "avg_frame_length": group[
            "frame_length"
        ].mean(),

        "max_frame_length": group[
            "frame_length"
        ].max(),

        "label": "XSS_SIM"
    })

flow_df = pd.DataFrame(flows)

flow_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("XSS flow building completed")
print("Packet rows:", len(df))
print("Flow rows:", len(flow_df))
print("Output:", OUTPUT_FILE)

print()
print(
    flow_df.head(10).to_string(
        index=False
    )
)