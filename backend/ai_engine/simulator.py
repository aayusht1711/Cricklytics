import math
import random
from typing import Dict, Any

def run_tactical_simulation(
    batsman: str,
    bowler: str,
    format_type: str = "T20",
    pitch: str = "Green Top",
    phase: str = "Death Overs",
    dew: float = 35.0
) -> Dict[str, Any]:
    """
    Calculates physical probabilities, spin/seam penalties, and over sequences.
    """
    b_name = batsman.title()
    bw_name = bowler.title()

    # Base physics modifiers
    pitch_modifier = 1.25 if "Green Top" in pitch else (1.15 if "Rank Turner" in pitch else 0.90)
    phase_modifier = 1.35 if "Death Overs" in phase else (1.10 if "Powerplay" in phase else 0.85)
    dew_spin_penalty = round(min(65.0, dew * 0.85), 1)

    # Calculate probabilities
    base_wicket = 16.5 * pitch_modifier * (1.0 - (dew * 0.003))
    wicket_prob = round(min(85.0, max(5.0, base_wicket)), 1)

    base_boundary = 32.0 * phase_modifier * (1.0 + (dew * 0.004)) / pitch_modifier
    boundary_prob = round(min(90.0, max(10.0, base_boundary)), 1)

    dot_prob = round(max(5.0, 100.0 - (wicket_prob + boundary_prob + 25.0)), 1)
    expected_rpo = round(max(3.5, (boundary_prob * 0.14) + (phase_modifier * 4.2)), 2)

    # Determine matchup winner
    if wicket_prob > boundary_prob * 0.65:
        winner = bw_name
        margin = f"High Wicket Threat ({wicket_prob}% chance to dismiss {b_name})"
    else:
        winner = b_name
        margin = f"Boundary Dominance ({boundary_prob}% chance to hit boundary)"

    # Toss analytics
    if dew >= 40.0:
        toss_rec = f"WIN TOSS & BOWL FIRST (Heavy dew factor of {dew}% reduces spin grip by {dew_spin_penalty}%)"
    else:
        toss_rec = f"WIN TOSS & BAT FIRST (Low dew factor of {dew}%. Pitch holds firm in 1st innings)"

    # 6-ball over blueprint
    over_sequence = [
        {
            "ball_number": 1,
            "delivery_type": "Wide Yorker (144 km/h)",
            "target_zone": "Wide Off-Stump Guideline",
            "wicket_probability": round(wicket_prob * 0.8, 1),
            "boundary_probability": round(boundary_prob * 0.5, 1),
            "tactical_note": "Nullifies boundary risk. Forces single to deep cover."
        },
        {
            "ball_number": 2,
            "delivery_type": "In-swinging Seam (142 km/h)",
            "target_zone": "Middle & Leg Base",
            "wicket_probability": round(wicket_prob * 1.3, 1),
            "boundary_probability": round(boundary_prob * 0.7, 1),
            "tactical_note": "Targets pad-bat separation gap on front foot stride."
        },
        {
            "ball_number": 3,
            "delivery_type": "Off-Cutter Slow Ball (124 km/h)",
            "target_zone": "Short of Length Outside Off",
            "wicket_probability": round(wicket_prob * 1.1, 1),
            "boundary_probability": round(boundary_prob * 0.6, 1),
            "tactical_note": "Deceive batsman's bat speed into deep mid-wicket."
        },
        {
            "ball_number": 4,
            "delivery_type": "Defensive Yorker (145 km/h)",
            "target_zone": "Base of Off stump",
            "wicket_probability": round(wicket_prob * 0.9, 1),
            "boundary_probability": round(boundary_prob * 0.4, 1),
            "tactical_note": "Reset momentum and restrict run rate."
        },
        {
            "ball_number": 5,
            "delivery_type": "Surprise Bouncer (146 km/h)",
            "target_zone": "Shoulder / Helmet Height",
            "wicket_probability": round(wicket_prob * 1.4, 1),
            "boundary_probability": round(boundary_prob * 1.1, 1),
            "tactical_note": "Exploit back-foot weight shift. Deep fine leg ready."
        },
        {
            "ball_number": 6,
            "delivery_type": "Attacking Full Out-Swinger (141 km/h)",
            "target_zone": "4th Stump Channel",
            "wicket_probability": round(wicket_prob * 1.6, 1),
            "boundary_probability": round(boundary_prob * 1.2, 1),
            "tactical_note": f"Induce drive off off-axis head tilt into slip gully."
        }
    ]

    return {
        "batsman_name": b_name,
        "bowler_name": bw_name,
        "format": format_type,
        "pitch_condition": pitch,
        "match_phase": phase,
        "dew_factor": dew,
        "wicket_probability": wicket_prob,
        "boundary_probability": boundary_prob,
        "dot_ball_probability": dot_prob,
        "expected_runs_per_over": expected_rpo,
        "dominant_winner": winner,
        "win_margin": margin,
        "toss_recommendation": toss_rec,
        "over_sequence": over_sequence
    }
