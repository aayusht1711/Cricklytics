import pandas as pd
import streamlit as st
import os


@st.cache_data
def load_data():
    """
    Load IPL ball-by-ball data.
    Priority:
      1. data_new.csv  (converted from cricsheet YAML — most complete)
      2. data.csv      (original fallback)
    """
    for fname in ["data_new.csv", "data.csv"]:
        if os.path.exists(fname):
            df = pd.read_csv(fname, low_memory=False)
            # ensure season is string
            df["season"] = df["season"].astype(str)
            return df

    st.error("No data file found. Place data_new.csv in project root.")
    return pd.DataFrame()
