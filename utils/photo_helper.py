import pandas as pd
import streamlit as st
import os
import base64
@st.cache_data
def load_profiles():
    paths = [
        "player_profiles_2026.csv",
        "data/player_profiles_2026.csv",
        "cricklytics/player_profiles_2026.csv",
        "cricklytics/data/player_profiles_2026.csv"
    ]
    for path in paths:
        if os.path.exists(path):
            try:
                return pd.read_csv(path)
            except Exception as e:
                pass
    return pd.DataFrame()
def get_player_info(player_name):
    profiles = load_profiles()
    if profiles.empty or not player_name:
        return None
    
    # Exact match
    match = profiles[profiles["name"] == player_name]
    if match.empty:
        # Case-insensitive match
        match = profiles[profiles["name"].str.lower() == player_name.lower()]
    
    if match.empty:
        # Try partial match (e.g. "V Kohli" matches "Virat Kohli" or "MS Dhoni" matches "Mahendra Singh Dhoni")
        # Split names to find matches
        player_words = set(player_name.lower().replace(".", " ").split())
        best_match = None
        max_overlap = 0
        for _, row in profiles.iterrows():
            row_words = set(row["name"].lower().split())
            overlap = len(player_words.intersection(row_words))
            if overlap > max_overlap:
                max_overlap = overlap
                best_match = row
        
        if max_overlap >= 1:
            return best_match
        return None
        
    return match.iloc[0]
def get_photo_b64(photo_id):
    if not photo_id or pd.isna(photo_id):
        return None
    
    try:
        pid = str(int(float(photo_id)))
    except Exception:
        pid = str(photo_id)
        
    paths = [
        f"static/player_photos/{pid}.png",
        f"cricklytics/static/player_photos/{pid}.png"
    ]
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception:
                pass
    return None
def get_player_avatar_html(player_name, team_color="#00FFFF", size=72, display_margin=True):
    initials = "".join([p[0] for p in str(player_name).split()[:2]]).upper() if player_name else "??"
    margin_style = "margin:0 auto 8px;" if display_margin else "margin:0;"
    
    fallback = (
        f"<div style='width:{size}px;height:{size}px;border-radius:50%;"
        f"background:{team_color}22;color:{team_color};"
        f"display:flex;align-items:center;justify-content:center;"
        f"font-size:{size//3}px;font-weight:800;{margin_style}"
        f"border:2px solid {team_color};'>"
        f"{initials}</div>"
    )
    
    info = get_player_info(player_name)
    if info is not None:
        photo_id = info.get("photo_id")
        if photo_id and not pd.isna(photo_id):
            b64 = get_photo_b64(photo_id)
            if b64:
                return (
                    f"<img src='data:image/png;base64,{b64}' "
                    f"style='width:{size}px;height:{size}px;border-radius:50%;"
                    f"object-fit:cover;border:2px solid {team_color};"
                    f"display:block;{margin_style}'>"
                )
    return fallback