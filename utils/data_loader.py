import pandas as pd
import streamlit as st
import os


@st.cache_data
def load_data(format_name="IPL"):
    """
    Load ball-by-ball data based on selected format.
    Priority:
      1. data/{format_name}.csv
      2. data_new.csv      (original fallback)
    """
    # Base dir for data
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    file_options = [
        os.path.join(base_dir, "data", f"{format_name}.csv"),
        os.path.join(base_dir, "data_new.csv"),
        os.path.join(base_dir, "data.csv")
    ]
    
    for fname in file_options:
        if os.path.exists(fname):
            df = pd.read_csv(fname, low_memory=False)
            # ensure season is string
            if "season" in df.columns:
                df["season"] = df["season"].astype(str)
            return df

    st.error(f"No data file found for {format_name}. Run scripts/download_cricsheet.py first.")
    return pd.DataFrame()
