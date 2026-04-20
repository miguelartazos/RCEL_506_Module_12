import pandas as pd
import requests
import streamlit as st

GBFS_URL = "https://gbfs.mex.lyftbikes.com/gbfs/gbfs.json"

st.set_page_config(page_title="CDMX Bike Share Map", layout="wide")

@st.cache_data(ttl=300)
def load_station_data():
    gbfs = requests.get(GBFS_URL, timeout=20).json()

    feeds = []
    for lang_data in gbfs.get("data", {}).values():
        if isinstance(lang_data, dict) and "feeds" in lang_data:
            feeds.extend(lang_data["feeds"])

    station_info_url = next(feed["url"] for feed in feeds if "station_information" in feed["name"])
    station_status_url = next(feed["url"] for feed in feeds if "station_status" in feed["name"])

    info = requests.get(station_info_url, timeout=20).json()
    status = requests.get(station_status_url, timeout=20).json()

    df_info = pd.DataFrame(info["data"]["stations"])[["station_id", "lat", "lon", "capacity"]]
    df_status = pd.DataFrame(status["data"]["stations"])[["station_id", "num_bikes_available", "num_docks_available"]]

    df = pd.merge(df_info, df_status, on="station_id", how="left")
    df["station_id"] = df["station_id"].astype(str)
    return df

st.title("Mexico City Bike Share System")
st.caption("Created by Miguel Artazos")

df = load_station_data()

left_col, right_col = st.columns([1, 2])

with left_col:
    station_list = ["All stations"] + sorted(df["station_id"].unique().tolist())
    selected_station = st.selectbox("Choose a station", station_list)

    if selected_station != "All stations":
        filtered_df = df[df["station_id"] == selected_station]
        st.write(filtered_df)
    else:
        filtered_df = df

with right_col:
    st.subheader("Bike Share Map")
    st.map(filtered_df.rename(columns={"lon": "longitude", "lat": "latitude"})[["latitude", "longitude"]])
