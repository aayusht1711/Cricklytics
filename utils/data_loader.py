import pandas as pd
import streamlit as st
import gdown
import os

@st.cache_data
def load_data():
    file_id = "1y2T7VTz3cjjYUc5IrHq4H9RtsIhc17M4"
    url = f"https://drive.google.com/uc?id={file_id}"
    output = "data.csv"

    # Download only if file not already present
    if not os.path.exists(output):
        gdown.download(url, output, quiet=False)

    # Load dataset
    df = pd.read_csv(output)

    return df