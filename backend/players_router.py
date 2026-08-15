from fastapi import APIRouter, HTTPException

router = APIRouter()
from csv_loader import load_all_players
MOCK_PLAYERS = load_all_players()

@router.get("/")
def get_all_players():
    # Return brief info for search/list
    return {
        "players": [
            {"id": p["id"], "name": p["name"], "role": p["role"], "team": p["team"], "image": p["image"]}
            for p in MOCK_PLAYERS
        ]
    }

@router.get("/{player_id}")
def get_player(player_id: str):
    player = next((p for p in MOCK_PLAYERS if p["id"] == player_id), None)
    if not player:
        # Try to scrape if not in mock DB
        from player_scraper import get_player_stats
        scraped_player = get_player_stats(player_id.replace("-", " "))
        if "error" not in scraped_player:
            # Dynamically add to MOCK_PLAYERS so it caches
            MOCK_PLAYERS.append(scraped_player)
            return scraped_player
        raise HTTPException(status_code=404, detail="Player not found")
    return player

import random
import os
import joblib
import pandas as pd
import numpy as np

# Load ML Model
MODEL_PATH = "model.pkl"
clf = None
if os.path.exists(MODEL_PATH):
    try:
        clf = joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"Error loading model: {e}")

@router.get("/simulate/{batsman_id}/{bowler_id}")
def simulate_matchup(batsman_id: str, bowler_id: str, phase: str = "Middle Overs"):
    batsman = next((p for p in MOCK_PLAYERS if p["id"] == batsman_id), None)
    bowler = next((p for p in MOCK_PLAYERS if p["id"] == bowler_id), None)
    
    # Try scraping if not found
    from player_scraper import get_player_stats
    if not batsman:
        scraped_bat = get_player_stats(batsman_id.replace("-", " "))
        if "error" not in scraped_bat:
            MOCK_PLAYERS.append(scraped_bat)
            batsman = scraped_bat
            
    if not bowler:
        scraped_bowl = get_player_stats(bowler_id.replace("-", " "))
        if "error" not in scraped_bowl:
            MOCK_PLAYERS.append(scraped_bowl)
            bowler = scraped_bowl
            
    if not batsman or not bowler:
        raise HTTPException(status_code=404, detail="Batsman or Bowler not found")
        
    if clf:
        # --- REAL MACHINE LEARNING INFERENCE ---
        phase_map = {"Powerplay": 0, "Middle Overs": 1, "Death Overs": 2}
        p_val = phase_map.get(phase, 1)
        
        bat_control = batsman["technique"]["control_percentage"]
        bat_power = batsman["t20_stats"]["strike_rate"] / 2
        bowl_economy = bowler["t20_stats"]["average"] / 3
        bowl_sr = bowler["t20_stats"]["strike_rate"]
        
        # Simulate 1000 deliveries with realistic variance
        features = pd.DataFrame({
            'batsman_control': [bat_control] * 1000,
            'batsman_power': [bat_power] * 1000,
            'bowler_economy': [bowl_economy] * 1000,
            'bowler_strike_rate': [bowl_sr] * 1000,
            'match_phase': [p_val] * 1000
        })
        
        # Add random noise to simulate match conditions
        features['batsman_control'] += np.random.normal(0, 5, 1000)
        features['batsman_power'] += np.random.normal(0, 3, 1000)
        
        # Run inference using the trained Random Forest
        preds = clf.predict(features)
        
        # Count outcomes (0=Dot, 1=Single, 2=Boundary, 3=Wicket)
        counts = pd.Series(preds).value_counts(normalize=True) * 100
        
        dot_prob = counts.get(0, 0.0)
        single_prob = counts.get(1, 0.0)
        adj_boundary = counts.get(2, 0.0)
        adj_wicket = counts.get(3, 0.0)
        
        expected_rpo = (adj_boundary/100 * 4.5 * 6) + (single_prob/100 * 1.5 * 6)
        sim_type = "Machine Learning (RandomForestClassifier)"
    else:
        # Fallback to Math
        bat_control = batsman["technique"]["control_percentage"]
        bowl_control = bowler["technique"]["control_percentage"]
        control_delta = bat_control - bowl_control
        
        base_boundary_prob = batsman["t20_stats"]["boundary_impact"] / 2.5
        base_wicket_prob = 100 - bat_control
        
        adj_boundary = max(5, base_boundary_prob + (control_delta * 0.2))
        adj_wicket = max(2, base_wicket_prob - (control_delta * 0.3))
        
        if phase == "Death Overs":
            adj_boundary *= 1.5
            adj_wicket *= 1.5
        elif phase == "Powerplay":
            adj_boundary *= 1.2
            adj_wicket *= 1.2
            
        dot_prob = max(10, 100 - adj_boundary - adj_wicket - 30)
        expected_rpo = (adj_boundary/100 * 4.5 * 6) + (30/100 * 1.5 * 6)
        sim_type = "Mathematical Model"

    return {
        "batsman": batsman["name"],
        "bowler": bowler["name"],
        "phase": phase,
        "simulations": 1000,
        "engine": sim_type,
        "results": {
            "wicket_probability": round(float(adj_wicket), 1),
            "boundary_probability": round(float(adj_boundary), 1),
            "dot_ball_probability": round(float(dot_prob), 1),
            "expected_runs_per_over": round(float(expected_rpo), 2)
        },
        "insight": f"Analysis powered by {sim_type}. {batsman['name']}'s {batsman['technique']['strong_zone']} vs {bowler['name']}."
    }
