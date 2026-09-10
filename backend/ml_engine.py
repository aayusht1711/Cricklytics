import os
import sys
import json
import math
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)
from csv_loader import load_all_players

MODEL_PATH = os.path.join(backend_dir, "model.pkl")

def get_player_ml_features(player):
    name = player["name"]
    role = player["role"]
    
    # 1. Batsman Control (60 to 95)
    control = float(player["technique"]["control_percentage"])
    control = max(60.0, min(95.0, control))
    
    # 2. Batsman Power (50 to 99)
    t20_sr = float(player["t20_stats"]["strike_rate"])
    boundary_impact = float(player["t20_stats"]["boundary_impact"])
    power = (t20_sr / 2.0) + (boundary_impact * 0.4)
    power = max(50.0, min(99.0, power))
    
    # 3. Bowler Economy (5.5 to 10.5)
    base_econ = 7.2
    if "Spinner" in role or "Spin" in role:
        base_econ = 6.8
    elif "Fast" in role or "Medium" in role:
        base_econ = 7.8
        
    hash_val = sum(ord(c) for c in name) % 100
    econ_modifier = (hash_val / 100.0) * 2.0 - 1.0
    economy = base_econ + econ_modifier
    economy = max(5.5, min(10.5, economy))
    
    # 4. Bowler Strike Rate (12 to 28)
    t20_wkts = float(player["t20_stats"]["wickets"])
    t20_matches = float(player["t20_stats"]["matches"])
    
    if t20_matches > 0:
        wkt_ratio = t20_wkts / t20_matches
    else:
        wkt_ratio = 0.5
        
    base_sr = 24.0 - (wkt_ratio * 10.0)
    sr_modifier = (hash_val / 100.0) * 4.0 - 2.0
    strike_rate = base_sr + sr_modifier
    strike_rate = max(12.0, min(28.0, strike_rate))
    
    return {
        "control": control,
        "power": power,
        "economy": economy,
        "strike_rate": strike_rate
    }

def generate_dataset(num_samples=150000):
    print("Loading all database players...")
    players = load_all_players()
    
    batters = [p for p in players if "Batter" in p["role"] or "Keeper" in p["role"] or "All-Rounder" in p["role"]]
    bowlers = [p for p in players if "Bowler" in p["role"] or "All-Rounder" in p["role"]]
    
    print(f"Found {len(batters)} batters and {len(bowlers)} bowlers in database.")
    print("Generating matchup simulation records...")
    
    np.random.seed(42)
    records = []
    
    # Generate balanced matchup rows
    for _ in range(num_samples):
        batsman = np.random.choice(batters)
        bowler = np.random.choice(bowlers)
        phase = np.random.randint(0, 3) # 0=Powerplay, 1=Middle, 2=Death
        
        bat_feat = get_player_ml_features(batsman)
        bowl_feat = get_player_ml_features(bowler)
        
        # Delivery-specific features
        risk = np.random.uniform(10.0, 95.0)
        dev = np.random.uniform(0.0, 4.0)
        speed = np.random.uniform(-8.0, 8.0)
        
        ctrl = bat_feat["control"]
        pwr = bat_feat["power"]
        econ = bowl_feat["economy"]
        sr = bowl_feat["strike_rate"]
        
        # Physics rules for outcomes
        # 1. Wicket (3) - High risk, high ball movement, low batsman control
        wicket_factor = (risk * 0.35) + (dev * 8.5) + (100.0 - ctrl) * 0.3 - (28.0 - sr) * 0.4
        if phase == 2:
            wicket_factor += 10.0
            
        # 2. Boundary (2) - High power, high risk, low ball movement
        boundary_factor = (pwr * 0.25) + (risk * 0.45) - (dev * 11.0) - (econ * 1.0)
        if phase == 0:
            boundary_factor += 12.0
            
        # 3. Dot ball (0) - Low risk, high ball movement, low batsman power
        dot_factor = (100.0 - risk) * 0.38 + (dev * 7.5) - (pwr * 0.18) + (10.5 - econ) * 3.5
        
        # Assign outcome class based on dominant factor thresholds
        if wicket_factor > 56.0:
            outcome = 3 # Wicket
        elif boundary_factor > 30.0:
            outcome = 2 # Boundary
        elif dot_factor > 38.0:
            outcome = 0 # Dot ball
        else:
            outcome = 1 # Single/Two
            
        records.append({
            "batsman_control": ctrl,
            "batsman_power": pwr,
            "bowler_economy": econ,
            "bowler_strike_rate": sr,
            "match_phase": phase,
            "delivery_risk": risk,
            "delivery_deviation": dev,
            "delivery_speed_delta": speed,
            "outcome": outcome
        })
        
    df = pd.DataFrame(records)
    print(f"Generated balanced dataset with {len(df)} delivery records.")
    return df

def train_and_save_model():
    df = generate_dataset()
    
    X = df.drop("outcome", axis=1)
    y = df["outcome"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training RandomForestClassifier model...")
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        min_samples_split=4,
        random_state=42
    )
    clf.fit(X_train, y_train)
    
    print("Evaluating Model Accuracy:")
    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred))
    
    print(f"Saving model to {MODEL_PATH}...")
    joblib.dump(clf, MODEL_PATH)
    print("ML Engine Model successfully trained and saved!")

if __name__ == "__main__":
    train_and_save_model()
