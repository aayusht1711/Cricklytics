from fastapi import APIRouter, HTTPException

router = APIRouter()

MOCK_PLAYERS = [
    {
        "id": "virat-kohli",
        "name": "Virat Kohli",
        "role": "Top-order Batter",
        "team": "India",
        "image": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?q=80&w=2000",
        "test_stats": {
            "matches": 113, "runs": 8848, "average": 49.15, "100s": 29, "50s": 30,
            "defensive_solidity": 68,
            "home_average": 60.1, "away_average": 42.5,
            "session_average": "Afternoon Dom (58 avg)",
            "partnership_value": "+42.5 runs/wkt"
        },
        "odi_stats": {
            "matches": 292, "runs": 13848, "average": 58.67, "100s": 50, "strike_rate": 93.62,
            "strike_rotation": 72,
            "chase_average": 65.2,
            "phase_pacing": "Mid (94) Death (185)",
            "conversion_rate": "62.5%"
        },
        "t20_stats": {
            "matches": 117, "runs": 4008, "average": 52.73, "strike_rate": 137.96,
            "boundary_impact": 55,
            "entry_intent_sr": 115,
            "death_sr": 205,
            "matchup_dominance": "Pace (145) Spin (128)"
        },
        "technique": {
            "control_percentage": 89,
            "middle_of_bat": 82,
            "edge_percentage": 11,
            "strong_zone": "Cover Drive"
        }
    },
    {
        "id": "steve-smith",
        "name": "Steve Smith",
        "role": "Top-order Batter",
        "team": "Australia",
        "image": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?q=80&w=2000",
        "test_stats": {
            "matches": 109, "runs": 9685, "average": 56.97, "100s": 32, "50s": 41,
            "defensive_solidity": 75,
            "home_average": 62.4, "away_average": 51.3,
            "session_average": "Morning Dom (64 avg)",
            "partnership_value": "+48.2 runs/wkt"
        },
        "odi_stats": {
            "matches": 158, "runs": 5446, "average": 43.91, "100s": 12, "strike_rate": 87.55,
            "strike_rotation": 65,
            "chase_average": 48.5,
            "phase_pacing": "Mid (84) Death (145)",
            "conversion_rate": "22.6%"
        },
        "t20_stats": {
            "matches": 67, "runs": 1094, "average": 25.44, "strike_rate": 125.45,
            "boundary_impact": 42,
            "entry_intent_sr": 105,
            "death_sr": 165,
            "matchup_dominance": "Pace (130) Spin (120)"
        },
        "technique": {
            "control_percentage": 92,
            "middle_of_bat": 79,
            "edge_percentage": 8,
            "strong_zone": "Flick off pads"
        }
    },
    {
        "id": "babar-azam",
        "name": "Babar Azam",
        "role": "Top-order Batter",
        "team": "Pakistan",
        "image": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?q=80&w=2000",
        "test_stats": {
            "matches": 52, "runs": 3898, "average": 45.85, "100s": 9, "50s": 26,
            "defensive_solidity": 70,
            "home_average": 58.2, "away_average": 38.4,
            "session_average": "Afternoon Dom (51 avg)",
            "partnership_value": "+39.5 runs/wkt"
        },
        "odi_stats": {
            "matches": 117, "runs": 5729, "average": 56.72, "100s": 19, "strike_rate": 88.75,
            "strike_rotation": 69,
            "chase_average": 52.1,
            "phase_pacing": "Mid (88) Death (155)",
            "conversion_rate": "42.2%"
        },
        "t20_stats": {
            "matches": 109, "runs": 3698, "average": 41.55, "strike_rate": 129.12,
            "boundary_impact": 50,
            "entry_intent_sr": 110,
            "death_sr": 175,
            "matchup_dominance": "Pace (125) Spin (135)"
        },
        "technique": {
            "control_percentage": 87,
            "middle_of_bat": 84,
            "edge_percentage": 13,
            "strong_zone": "Cover Drive"
        }
    },
    {
        "id": "rohit-sharma",
        "name": "Rohit Sharma",
        "role": "Opening Batter",
        "team": "India",
        "image": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?q=80&w=2000",
        "test_stats": {
            "matches": 59, "runs": 4137, "average": 45.46, "100s": 12, "50s": 17,
            "defensive_solidity": 62,
            "home_average": 61.3, "away_average": 34.5,
            "session_average": "Morning Dom (54 avg)",
            "partnership_value": "+45.1 runs/wkt"
        },
        "odi_stats": {
            "matches": 262, "runs": 10709, "average": 49.12, "100s": 31, "strike_rate": 91.97,
            "strike_rotation": 60,
            "chase_average": 47.3,
            "phase_pacing": "Powerplay (92) Death (195)",
            "conversion_rate": "64.5%"
        },
        "t20_stats": {
            "matches": 151, "runs": 3974, "average": 31.79, "strike_rate": 139.97,
            "boundary_impact": 68,
            "entry_intent_sr": 135,
            "death_sr": 210,
            "matchup_dominance": "Pace (150) Spin (125)"
        },
        "technique": {
            "control_percentage": 84,
            "middle_of_bat": 88,
            "edge_percentage": 16,
            "strong_zone": "Pull Shot"
        }
    },
    {
        "id": "rashid-khan",
        "name": "Rashid Khan",
        "role": "Leg Spin Bowler",
        "team": "Afghanistan",
        "image": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?q=80&w=2000",
        "test_stats": {
            "matches": 5, "runs": 34, "average": 31.55, "100s": 0, "50s": 0,
            "defensive_solidity": 30, "home_average": 31.5, "away_average": 32.1,
            "session_average": "Morning Dom (22 avg)", "partnership_value": "-15 runs/wkt"
        },
        "odi_stats": {
            "matches": 103, "runs": 190, "average": 20.45, "100s": 0, "strike_rate": 85.0,
            "strike_rotation": 40, "chase_average": 22.1, "phase_pacing": "Mid (80)", "conversion_rate": "0%"
        },
        "t20_stats": {
            "matches": 92, "runs": 138, "average": 14.27, "strike_rate": 125.0,
            "boundary_impact": 20, "entry_intent_sr": 90, "death_sr": 135,
            "matchup_dominance": "Spin (140) Pace (110)"
        },
        "technique": {
            "control_percentage": 95,
            "middle_of_bat": 50,
            "edge_percentage": 35,
            "strong_zone": "Googly"
        }
    },
    {
        "id": "pat-cummins",
        "name": "Pat Cummins",
        "role": "Fast Bowler",
        "team": "Australia",
        "image": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?q=80&w=2000",
        "test_stats": {
            "matches": 62, "runs": 269, "average": 22.53, "100s": 0, "50s": 0,
            "defensive_solidity": 45, "home_average": 20.1, "away_average": 25.5,
            "session_average": "Evening Dom (18 avg)", "partnership_value": "-20 runs/wkt"
        },
        "odi_stats": {
            "matches": 88, "runs": 141, "average": 28.66, "100s": 0, "strike_rate": 78.0,
            "strike_rotation": 30, "chase_average": 25.1, "phase_pacing": "Powerplay (75)", "conversion_rate": "0%"
        },
        "t20_stats": {
            "matches": 57, "runs": 66, "average": 24.55, "strike_rate": 115.0,
            "boundary_impact": 25, "entry_intent_sr": 80, "death_sr": 120,
            "matchup_dominance": "Pace (130) Spin (100)"
        },
        "technique": {
            "control_percentage": 92,
            "middle_of_bat": 45,
            "edge_percentage": 40,
            "strong_zone": "Top of Off Stump"
        }
    }
]

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
