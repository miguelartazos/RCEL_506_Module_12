import pandas as pd
import requests
import folium
import streamlit as st
from streamlit_folium import st_folium

GBFS_URL = "https://gbfs.mex.lyftbikes.com/gbfs/gbfs.json"

st.set_page_config(page_title="CDMX Bike Share Map", layout="wide")


@st.cache_data(ttl=300)
def load_station_data() -> pd.DataFrame:
    """Load and merge station information + live station status from the GBFS feed."""
    gbfs = requests.get(GBFS_URL, timeout=20)
    gbfs.raise_for_status()
    gbfs_data = gbfs.json()

    feeds = []
    for lang_data in gbfs_data.get("data", {}).values():
        if isinstance(lang_data, dict) and "feeds" in lang_data:
            feeds.extend(lang_data["feeds"])
