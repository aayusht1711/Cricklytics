import os
import pandas as pd
import hashlib

# 1. Define the 13 hand-crafted high-quality players
HAND_CRAFTED = [
    {
        "id": "virat-kohli",
        "name": "Virat Kohli",
        "role": "Top-order Batter",
        "team": "India",
        "image": "/player_photos/2.png",
        "test_stats": {
            "matches": 113, "runs": 8848, "average": 49.15, "100s": 29, "50s": 30,
            "defensive_solidity": 68,
            "home_average": 60.1, "away_average": 42.5,
            "session_average": "Afternoon Dom (58 avg)",
            "partnership_value": "+42.5 runs/wkt", "wickets": 4, "bowling_average": 84.0
        },
        "odi_stats": {
            "matches": 292, "runs": 13848, "average": 58.67, "100s": 50, "strike_rate": 93.62,
            "strike_rotation": 72,
            "chase_average": 65.2,
            "phase_pacing": "Mid (94) Death (185)",
            "conversion_rate": "62.5%", "wickets": 5
        },
        "t20_stats": {
            "matches": 117, "runs": 4008, "average": 52.73, "strike_rate": 137.96,
            "boundary_impact": 55,
            "entry_intent_sr": 115,
            "death_sr": 205,
            "matchup_dominance": "Pace (145) Spin (128)", "wickets": 4
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
        "image": "/player_photos/steve-smith.png",
        "test_stats": {
            "matches": 109, "runs": 9685, "average": 56.97, "100s": 32, "50s": 41,
            "defensive_solidity": 75,
            "home_average": 62.4, "away_average": 51.3,
            "session_average": "Morning Dom (64 avg)",
            "partnership_value": "+48.2 runs/wkt", "wickets": 19, "bowling_average": 52.3
        },
        "odi_stats": {
            "matches": 158, "runs": 5446, "average": 43.91, "100s": 12, "strike_rate": 87.55,
            "strike_rotation": 65,
            "chase_average": 48.5,
            "phase_pacing": "Mid (84) Death (145)",
            "conversion_rate": "22.6%", "wickets": 28
        },
        "t20_stats": {
            "matches": 67, "runs": 1094, "average": 25.44, "strike_rate": 125.45,
            "boundary_impact": 42,
            "entry_intent_sr": 105,
            "death_sr": 165,
            "matchup_dominance": "Pace (130) Spin (120)", "wickets": 17
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
        "image": "/player_photos/babar-azam.png",
        "test_stats": {
            "matches": 52, "runs": 3898, "average": 45.85, "100s": 9, "50s": 26,
            "defensive_solidity": 70,
            "home_average": 58.2, "away_average": 38.4,
            "session_average": "Afternoon Dom (51 avg)",
            "partnership_value": "+39.5 runs/wkt", "wickets": 2, "bowling_average": 62.0
        },
        "odi_stats": {
            "matches": 117, "runs": 5729, "average": 56.72, "100s": 19, "strike_rate": 88.75,
            "strike_rotation": 69,
            "chase_average": 52.1,
            "phase_pacing": "Mid (88) Death (155)",
            "conversion_rate": "42.2%", "wickets": 0
        },
        "t20_stats": {
            "matches": 109, "runs": 3698, "average": 41.55, "strike_rate": 129.12,
            "boundary_impact": 50,
            "entry_intent_sr": 110,
            "death_sr": 175,
            "matchup_dominance": "Pace (125) Spin (135)", "wickets": 0
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
        "image": "/player_photos/6.png",
        "test_stats": {
            "matches": 59, "runs": 4137, "average": 45.46, "100s": 12, "50s": 17,
            "defensive_solidity": 62,
            "home_average": 61.3, "away_average": 34.5,
            "session_average": "Morning Dom (54 avg)",
            "partnership_value": "+45.1 runs/wkt", "wickets": 2, "bowling_average": 90.0
        },
        "odi_stats": {
            "matches": 262, "runs": 10709, "average": 49.12, "100s": 31, "strike_rate": 91.97,
            "strike_rotation": 60,
            "chase_average": 47.3,
            "phase_pacing": "Powerplay (92) Death (195)",
            "conversion_rate": "64.5%", "wickets": 8
        },
        "t20_stats": {
            "matches": 151, "runs": 3974, "average": 31.79, "strike_rate": 139.97,
            "boundary_impact": 68,
            "entry_intent_sr": 135,
            "death_sr": 210,
            "matchup_dominance": "Pace (150) Spin (125)", "wickets": 1
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
        "image": "/player_photos/218.png",
        "test_stats": {
            "matches": 5, "runs": 34, "average": 31.55, "100s": 0, "50s": 0,
            "defensive_solidity": 30, "home_average": 31.5, "away_average": 32.1,
            "session_average": "Morning Dom (22 avg)", "partnership_value": "-15 runs/wkt", "wickets": 34, "bowling_average": 22.3
        },
        "odi_stats": {
            "matches": 103, "runs": 190, "average": 20.45, "100s": 0, "strike_rate": 85.0,
            "strike_rotation": 40, "chase_average": 22.1, "phase_pacing": "Mid (80)", "conversion_rate": "0%", "wickets": 182
        },
        "t20_stats": {
            "matches": 92, "runs": 138, "average": 14.27, "strike_rate": 125.0,
            "boundary_impact": 20, "entry_intent_sr": 90, "death_sr": 135,
            "matchup_dominance": "Spin (140) Pace (110)", "wickets": 152
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
        "image": "/player_photos/3575.png",
        "test_stats": {
            "matches": 62, "runs": 269, "average": 22.53, "100s": 0, "50s": 0,
            "defensive_solidity": 45, "home_average": 20.1, "away_average": 25.5,
            "session_average": "Evening Dom (18 avg)", "partnership_value": "-20 runs/wkt", "wickets": 269, "bowling_average": 22.53
        },
        "odi_stats": {
            "matches": 88, "runs": 141, "average": 28.66, "100s": 0, "strike_rate": 78.0,
            "strike_rotation": 30, "chase_average": 25.1, "phase_pacing": "Powerplay (75)", "conversion_rate": "0%", "wickets": 141
        },
        "t20_stats": {
            "matches": 57, "runs": 66, "average": 24.55, "strike_rate": 115.0,
            "boundary_impact": 25, "entry_intent_sr": 80, "death_sr": 120,
            "matchup_dominance": "Pace (130) Spin (100)", "wickets": 66
        },
        "technique": {
            "control_percentage": 92,
            "middle_of_bat": 45,
            "edge_percentage": 40,
            "strong_zone": "Top of Off Stump"
        }
    },
    {
        "id": "rishabh-pant",
        "name": "Rishabh Pant",
        "role": "Wicket-Keeper Batter",
        "team": "India",
        "image": "/player_photos/18.png",
        "test_stats": {
            "matches": 34, "runs": 2271, "average": 43.67, "100s": 6, "50s": 11,
            "defensive_solidity": 55, "home_average": 45.2, "away_average": 42.1,
            "session_average": "Evening Dom (50 avg)", "partnership_value": "+35.2 runs/wkt", "wickets": 0, "bowling_average": 0
        },
        "odi_stats": {
            "matches": 30, "runs": 865, "average": 34.6, "100s": 1, "strike_rate": 106.65,
            "strike_rotation": 62, "chase_average": 38.2, "phase_pacing": "Mid (98) Death (165)", "conversion_rate": "25%", "wickets": 0
        },
        "t20_stats": {
            "matches": 66, "runs": 987, "average": 22.43, "strike_rate": 126.37,
            "boundary_impact": 58, "entry_intent_sr": 120, "death_sr": 185,
            "matchup_dominance": "Pace (130) Spin (120)", "wickets": 0
        },
        "technique": {
            "control_percentage": 78, "middle_of_bat": 84, "edge_percentage": 18, "strong_zone": "One-handed Six"
        }
    },
    {
        "id": "travis-head",
        "name": "Travis Head",
        "role": "Top-order Batter",
        "team": "Australia",
        "image": "/player_photos/37.png",
        "test_stats": {
            "matches": 49, "runs": 3173, "average": 41.75, "100s": 7, "50s": 15,
            "defensive_solidity": 50, "home_average": 52.3, "away_average": 31.2,
            "session_average": "Morning Dom (48 avg)", "partnership_value": "+38.4 runs/wkt", "wickets": 0, "bowling_average": 0
        },
        "odi_stats": {
            "matches": 64, "runs": 2393, "average": 42.73, "100s": 3, "strike_rate": 105.5,
            "strike_rotation": 55, "chase_average": 45.1, "phase_pacing": "Powerplay (115)", "conversion_rate": "20%", "wickets": 0
        },
        "t20_stats": {
            "matches": 33, "runs": 932, "average": 32.13, "strike_rate": 147.2,
            "boundary_impact": 72, "entry_intent_sr": 140, "death_sr": 190,
            "matchup_dominance": "Pace (150) Spin (130)", "wickets": 0
        },
        "technique": {
            "control_percentage": 76, "middle_of_bat": 86, "edge_percentage": 24, "strong_zone": "Slash over point"
        }
    },
    {
        "id": "hardik-pandya",
        "name": "Hardik Pandya",
        "role": "All-Rounder",
        "team": "India",
        "image": "/player_photos/3107.png",
        "test_stats": {
            "matches": 11, "runs": 532, "average": 31.29, "100s": 1, "50s": 4,
            "defensive_solidity": 48, "home_average": 35.1, "away_average": 28.5,
            "session_average": "Afternoon Dom (33 avg)", "partnership_value": "+25.4 runs/wkt", "wickets": 17, "bowling_average": 31.05
        },
        "odi_stats": {
            "matches": 86, "runs": 1769, "average": 34.01, "100s": 0, "strike_rate": 110.35,
            "strike_rotation": 64, "chase_average": 36.5, "phase_pacing": "Mid (95) Death (175)", "conversion_rate": "0%", "wickets": 84
        },
        "t20_stats": {
            "matches": 102, "runs": 1523, "average": 25.38, "strike_rate": 139.55,
            "boundary_impact": 60, "entry_intent_sr": 118, "death_sr": 195,
            "matchup_dominance": "Pace (145) Spin (125)", "wickets": 86
        },
        "technique": {
            "control_percentage": 82, "middle_of_bat": 80, "edge_percentage": 14, "strong_zone": "Helicopter Shot"
        }
    },
    {
        "id": "glenn-maxwell",
        "name": "Glenn Maxwell",
        "role": "All-Rounder",
        "team": "Australia",
        "image": "/player_photos/glenn-maxwell.png",
        "test_stats": {
            "matches": 7, "runs": 339, "average": 26.07, "100s": 1, "50s": 0,
            "defensive_solidity": 40, "home_average": 22.4, "away_average": 28.2,
            "session_average": "Afternoon Dom (30 avg)", "partnership_value": "+20.1 runs/wkt", "wickets": 8, "bowling_average": 42.6
        },
        "odi_stats": {
            "matches": 142, "runs": 3895, "average": 35.4, "100s": 4, "strike_rate": 126.91,
            "strike_rotation": 58, "chase_average": 39.5, "phase_pacing": "Mid (110) Death (210)", "conversion_rate": "22%", "wickets": 64
        },
        "t20_stats": {
            "matches": 106, "runs": 2468, "average": 30.09, "strike_rate": 155.5,
            "boundary_impact": 75, "entry_intent_sr": 135, "death_sr": 215,
            "matchup_dominance": "Spin (165) Pace (140)", "wickets": 40
        },
        "technique": {
            "control_percentage": 75,
            "middle_of_bat": 88,
            "edge_percentage": 20,
            "strong_zone": "Reverse Sweep"
        }
    },
    {
        "id": "jasprit-bumrah",
        "name": "Jasprit Bumrah",
        "role": "Fast Bowler",
        "team": "India",
        "image": "/player_photos/9.png",
        "test_stats": {
            "matches": 36, "runs": 212, "average": 10.6, "100s": 0, "50s": 0,
            "defensive_solidity": 35, "home_average": 9.4, "away_average": 11.2,
            "session_average": "Evening Dom (12 avg)", "partnership_value": "-5 runs/wkt", "wickets": 159, "bowling_average": 20.69
        },
        "odi_stats": {
            "matches": 89, "runs": 79, "average": 7.9, "100s": 0, "strike_rate": 62.4,
            "strike_rotation": 32, "chase_average": 8.1, "phase_pacing": "Powerplay (55)", "conversion_rate": "0%", "wickets": 149
        },
        "t20_stats": {
            "matches": 62, "runs": 19, "average": 6.33, "strike_rate": 78.5,
            "boundary_impact": 10, "entry_intent_sr": 60, "death_sr": 95,
            "matchup_dominance": "Pace (90) Spin (60)", "wickets": 89
        },
        "technique": {
            "control_percentage": 98, "middle_of_bat": 35, "edge_percentage": 45, "strong_zone": "Toe-crushing Yorker"
        }
    },
    {
        "id": "mitchell-starc",
        "name": "Mitchell Starc",
        "role": "Fast Bowler",
        "team": "Australia",
        "image": "/player_photos/31.png",
        "test_stats": {
            "matches": 89, "runs": 2012, "average": 21.86, "100s": 0, "50s": 10,
            "defensive_solidity": 42, "home_average": 24.1, "away_average": 19.3,
            "session_average": "Evening Dom (18 avg)", "partnership_value": "-12 runs/wkt", "wickets": 358, "bowling_average": 27.7
        },
        "odi_stats": {
            "matches": 121, "runs": 539, "average": 14.17, "100s": 0, "strike_rate": 88.5,
            "strike_rotation": 42, "chase_average": 15.2, "phase_pacing": "Powerplay (80)", "conversion_rate": "0%", "wickets": 236
        },
        "t20_stats": {
            "matches": 60, "runs": 98, "average": 9.8, "strike_rate": 102.5,
            "boundary_impact": 15, "entry_intent_sr": 75, "death_sr": 110,
            "matchup_dominance": "Pace (100) Spin (80)", "wickets": 74
        },
        "technique": {
            "control_percentage": 92,
            "middle_of_bat": 42,
            "edge_percentage": 40,
            "strong_zone": "Inswinging Yorker"
        }
    },
    {
        "id": "kuldeep-yadav",
        "name": "Kuldeep Yadav",
        "role": "Left-arm Wrist Spinner",
        "team": "India",
        "image": "/player_photos/14.png",
        "test_stats": {
            "matches": 12, "runs": 154, "average": 14.0, "100s": 0, "50s": 0,
            "defensive_solidity": 38, "home_average": 15.4, "away_average": 12.1,
            "session_average": "Evening Dom (10 avg)", "partnership_value": "-8 runs/wkt", "wickets": 53, "bowling_average": 22.0
        },
        "odi_stats": {
            "matches": 103, "runs": 198, "average": 11.64, "100s": 0, "strike_rate": 68.5,
            "strike_rotation": 38, "chase_average": 12.5, "phase_pacing": "Mid (70)", "conversion_rate": "0%", "wickets": 168
        },
        "t20_stats": {
            "matches": 40, "runs": 54, "average": 9.0, "strike_rate": 84.5,
            "boundary_impact": 12, "entry_intent_sr": 70, "death_sr": 98,
            "matchup_dominance": "Spin (95) Pace (70)", "wickets": 59
        },
        "technique": {
            "control_percentage": 96, "middle_of_bat": 38, "edge_percentage": 42, "strong_zone": "Chinaman Delivery"
        }
    }
]

# 2. Helper to get deterministic hash value
def get_hash_number(name: str, min_val: float, max_val: float, is_int: bool = False) -> float:
    h = hashlib.md5(name.encode('utf-8')).hexdigest()
    val = int(h[:8], 16) / 4294967295.0
    res = min_val + (max_val - min_val) * val
    return int(res) if is_int else round(res, 2)

# 3. Main loader function
def load_all_players():
    players_list = list(HAND_CRAFTED)
    hand_crafted_ids = {p["id"] for p in HAND_CRAFTED}

    # Resolve CSV Path relative to this loader
    csv_path = os.path.join(os.path.dirname(__file__), "..", "player_profiles_2026.csv")
    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} not found. Using handcrafted players only.")
        return players_list

    try:
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            name = str(row["name"]).strip()
            # Clean name for ID
            pid_str = name.lower().replace(" ", "-").replace(".", "").replace("'", "")
            
            # Skip if already in handcrafted list
            if pid_str in hand_crafted_ids:
                continue

            role = str(row["role"]).strip()
            team_country = str(row["nationality"]).strip()
            
            # Resolve player photo path
            photo_raw = row.get("photo_id")
            try:
                p_num = str(int(float(photo_raw)))
                image_path = f"/player_photos/{p_num}.png"
            except Exception:
                image_path = "/player_photos/default.png"

            # Parse auction price to weight statistics
            price = float(row.get("auction_price_cr", 0.0))
            perf_modifier = price * 1.2
            
            # Determine batting/bowling parameters based on role
            is_batter = "Batter" in role or "Keeper" in role or "All-Rounder" in role
            is_bowler = "Bowler" in role or "All-Rounder" in role

            # Generate stats deterministically
            test_matches = get_hash_number(name, 5, 80, is_int=True)
            odi_matches = get_hash_number(name, 10, 150, is_int=True)
            t20_matches = get_hash_number(name, 15, 200, is_int=True)

            # Batting stats
            if is_batter:
                bat_avg = get_hash_number(name, 32.0 + perf_modifier, min(52.0, 42.0 + perf_modifier))
                test_runs = int(test_matches * bat_avg * 0.9)
                odi_runs = int(odi_matches * bat_avg * 0.8)
                t20_runs = int(t20_matches * (bat_avg - 10) * 0.7)
                test_100s = max(0, int(test_runs / 700))
                test_50s = max(0, int(test_runs / 300) - test_100s)
                odi_100s = max(0, int(odi_runs / 900))
                odi_sr = get_hash_number(name, 82.0, 110.0)
                t20_sr = get_hash_number(name, 125.0, 155.0)
                def_sol = get_hash_number(name, 55, 82, is_int=True)
                rotation = get_hash_number(name, 50, 72, is_int=True)
                strong_zone = get_hash_number(name, 0, 4, is_int=True)
                sz = ["Cover Drive", "Pull Shot", "Slog Sweep", "Straight Drive", "Flick"][strong_zone]
            else:
                bat_avg = get_hash_number(name, 5.0, 18.0)
                test_runs = int(test_matches * bat_avg)
                odi_runs = int(odi_matches * bat_avg)
                t20_runs = int(t20_matches * (bat_avg - 3))
                test_100s = 0
                test_50s = 0
                odi_100s = 0
                odi_sr = get_hash_number(name, 55.0, 75.0)
                t20_sr = get_hash_number(name, 85.0, 115.0)
                def_sol = get_hash_number(name, 25, 45, is_int=True)
                rotation = get_hash_number(name, 25, 45, is_int=True)
                sz = "Tail-end slog"

            # Bowling stats
            if is_bowler:
                test_wkts = get_hash_number(name, int(test_matches * 1.5), int(test_matches * 3.5), is_int=True)
                odi_wkts = get_hash_number(name, int(odi_matches * 0.9), int(odi_matches * 1.8), is_int=True)
                t20_wkts = get_hash_number(name, int(t20_matches * 0.8), int(t20_matches * 1.4), is_int=True)
                test_bowl_avg = get_hash_number(name, 21.0, 31.0)
                bowl_sr = get_hash_number(name, 48, 65, is_int=True)
                strong_ball = get_hash_number(name, 0, 3, is_int=True)
                sz = ["Inswinging Yorker", "Outswinger", "Slower Ball", "Off-break"][strong_ball] if not is_batter else sz
            else:
                test_wkts = 0
                odi_wkts = 0
                t20_wkts = 0
                test_bowl_avg = 0.0
                bowl_sr = 0

            player_profile = {
                "id": pid_str,
                "name": name,
                "role": role,
                "team": team_country,
                "image": image_path,
                "test_stats": {
                    "matches": test_matches, "runs": test_runs, "average": bat_avg,
                    "100s": test_100s, "50s": test_50s, "defensive_solidity": def_sol,
                    "home_average": round(bat_avg + 3.2, 2), "away_average": round(max(5.0, bat_avg - 4.1), 2),
                    "session_average": f"Afternoon Dom ({int(bat_avg + 1)} avg)" if get_hash_number(name, 0, 1) > 0.5 else f"Morning Dom ({int(bat_avg + 2)} avg)",
                    "partnership_value": f"+{round(bat_avg * 0.8, 1)} runs/wkt",
                    "wickets": test_wkts, "bowling_average": test_bowl_avg
                },
                "odi_stats": {
                    "matches": odi_matches, "runs": odi_runs, "average": bat_avg,
                    "100s": odi_100s, "strike_rate": odi_sr, "strike_rotation": rotation,
                    "chase_average": round(bat_avg + 1.5, 2),
                    "phase_pacing": "Powerplay (95)" if is_batter else "Powerplay (75)",
                    "conversion_rate": f"{int(get_hash_number(name, 20, 50))}%",
                    "wickets": odi_wkts
                },
                "t20_stats": {
                    "matches": t20_matches, "runs": t20_runs, "average": bat_avg,
                    "strike_rate": t20_sr, "boundary_impact": get_hash_number(name, 35, 68, is_int=True) if is_batter else 15,
                    "entry_intent_sr": int(t20_sr - 10), "death_sr": int(t20_sr + 35),
                    "matchup_dominance": f"Pace ({int(t20_sr + 5)}) Spin ({int(t20_sr - 5)})",
                    "wickets": t20_wkts
                },
                "technique": {
                    "control_percentage": get_hash_number(name, 72, 91, is_int=True) if is_batter else 60,
                    "middle_of_bat": get_hash_number(name, 68, 88, is_int=True) if is_batter else 45,
                    "edge_percentage": get_hash_number(name, 10, 22, is_int=True) if is_batter else 35,
                    "strong_zone": sz
                }
            }
            players_list.append(player_profile)
    except Exception as e:
        print(f"Error loading CSV players: {e}")

    return players_list
