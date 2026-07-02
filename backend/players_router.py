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
