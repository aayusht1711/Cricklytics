"""
Venue & Climate Database for Automated Dew & Pitch Prediction
"""

VENUE_DATABASE = {
    "wankhede-mumbai": {
        "name": "Wankhede Stadium, Mumbai",
        "country": "India",
        "coastal": True,
        "base_humidity": 78.0,
        "lat": 18.9389,
        "lon": 72.8258,
        "default_pitch": "Flat / Batting",
        "toss_bias": "Bowl First (82% win rate under lights due to heavy dew)",
        "insight": "Coastal Arabian Sea location. Dew settles heavily after 8:00 PM, reducing spin by ~40% and making red-soil pitch extremely fast in 2nd innings."
    },
    "eden-gardens-kolkata": {
        "name": "Eden Gardens, Kolkata",
        "country": "India",
        "coastal": True,
        "base_humidity": 82.0,
        "lat": 22.5647,
        "lon": 88.3433,
        "default_pitch": "Flat / Batting",
        "toss_bias": "Bowl First (Heavy evening dew)",
        "insight": "Gangetic delta region. High evening relative humidity leads to thick dew on grass starting mid-2nd innings."
    },
    "chinnaswamy-bengaluru": {
        "name": "M. Chinnaswamy Stadium, Bengaluru",
        "country": "India",
        "coastal": False,
        "base_humidity": 55.0,
        "lat": 12.9788,
        "lon": 77.5996,
        "default_pitch": "Flat / Batting",
        "toss_bias": "Chase Preference (Short boundaries + moderate dew)",
        "insight": "High altitude inland plateau (900m). Air cools quickly after sunset causing moderate dew (45-60%). Outfield is lightning fast."
    },
    "chepauk-chennai": {
        "name": "MA Chidambaram Stadium (Chepauk), Chennai",
        "country": "India",
        "coastal": True,
        "base_humidity": 75.0,
        "lat": 13.0628,
        "lon": 80.2796,
        "default_pitch": "Dry / Spin",
        "toss_bias": "Bat First in Day matches, Bowl First in Night matches",
        "insight": "Coastal Bay of Bengal venue. Red/black soil offers turn early, but heavy night dew nullifies finger spinners in the 2nd innings."
    },
    "dubai-international": {
        "name": "Dubai International Cricket Stadium",
        "country": "UAE",
        "coastal": True,
        "base_humidity": 72.0,
        "lat": 25.0456,
        "lon": 55.2185,
        "default_pitch": "Flat / Batting",
        "toss_bias": "Bowl First (Infamous dew factor venue)",
        "insight": "Persian Gulf desert climate. Rapid temperature drop after 7:30 PM creates heavy moisture condensation on the outfield."
    },
    "mcg-melbourne": {
        "name": "Melbourne Cricket Ground (MCG)",
        "country": "Australia",
        "coastal": False,
        "base_humidity": 25.0,
        "lat": -37.8199,
        "lon": 144.9834,
        "default_pitch": "Green / Seam",
        "toss_bias": "Bat First",
        "insight": "Southern temperate climate. Strong coastal winds keep atmosphere dry; dew factor is 0% throughout evening matches."
    },
    "lords-london": {
        "name": "Lord's Cricket Ground, London",
        "country": "UK",
        "coastal": False,
        "base_humidity": 30.0,
        "lat": 51.5298,
        "lon": -0.1727,
        "default_pitch": "Green / Seam",
        "toss_bias": "Bowl First (Overcast swing)",
        "insight": "Maritime climate with famous pitch slope. Overcast skies dictate swing, but ground dries quickly with 0% dew during match hours."
    },
    "gaddafi-lahore": {
        "name": "Gaddafi Stadium, Lahore",
        "country": "Pakistan",
        "coastal": False,
        "base_humidity": 85.0,
        "lat": 31.5133,
        "lon": 74.3319,
        "default_pitch": "Flat / Batting",
        "toss_bias": "Bowl First in Winter (Heavy fog/dew)",
        "insight": "Northern plains venue. Winter night matches (Oct-Feb) experience extreme dew and fog, making the ball wet from ball 1."
    }
}

def predict_dew_and_pitch(venue_key: str, timing: str, season: str = "Oct-Feb (Winter/Post-Monsoon)"):
    # Normalize key lookup
    key = venue_key.lower().strip().replace(" ", "-").replace(".", "").replace("'", "")
    
    venue = None
    for k, v in VENUE_DATABASE.items():
        if k in key or key in k:
            venue = v
            break
            
    if not venue:
        venue = VENUE_DATABASE["wankhede-mumbai"] # Default fallback
        
    base_hum = venue["base_humidity"]
    
    # Timing multiplier
    if "Night" in timing or "7:00" in timing:
        time_mult = 1.0
    elif "Day/Night" in timing or "2:00" in timing:
        time_mult = 0.70
    else: # Day match
        time_mult = 0.08
        
    # Season multiplier
    if "Oct" in season or "Winter" in season:
        season_mult = 1.12
    else:
        season_mult = 0.88
        
    dew_calc = base_hum * time_mult * season_mult
    dew_pct = round(max(0.0, min(95.0, dew_calc)), 1)
    
    return {
        "venue_name": venue["name"],
        "country": venue["country"],
        "predicted_dew_factor": dew_pct,
        "predicted_pitch_type": venue["default_pitch"],
        "toss_bias": venue["toss_bias"],
        "venue_insight": venue["insight"],
        "lat": venue["lat"],
        "lon": venue["lon"]
    }

def fetch_live_weather(venue_key: str):
    import urllib.request
    import json
    
    key = venue_key.lower().strip().replace(" ", "-").replace(".", "").replace("'", "")
    venue = None
    for k, v in VENUE_DATABASE.items():
        if k in key or key in k:
            venue = v
            break
    if not venue:
        venue = VENUE_DATABASE["wankhede-mumbai"]
        
    lat = venue["lat"]
    lon = venue["lon"]
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode())
                current = data.get("current", {})
                humidity = float(current.get("relative_humidity_2m", venue["base_humidity"]))
                temp = float(current.get("temperature_2m", 28.0))
                pressure = float(current.get("surface_pressure", 1013.2))
                wind_speed = float(current.get("wind_speed_10m", 12.0))
                
                # Dynamic live dew calculation
                live_dew = round(max(5.0, min(95.0, humidity * 0.85)), 1)
                
                return {
                    "is_live": True,
                    "venue_name": venue["name"],
                    "temperature_c": temp,
                    "humidity_pct": humidity,
                    "surface_pressure_hpa": pressure,
                    "wind_speed_kmh": wind_speed,
                    "calculated_dew_factor": live_dew,
                    "source": "Open-Meteo Live Satellite Atmospheric API"
                }
    except Exception as e:
        print(f"Weather API fallback used: {e}")
        
    return {
        "is_live": False,
        "venue_name": venue["name"],
        "temperature_c": 28.5,
        "humidity_pct": venue["base_humidity"],
        "surface_pressure_hpa": 1012.0,
        "wind_speed_kmh": 14.2,
        "calculated_dew_factor": round(venue["base_humidity"] * 0.8, 1),
        "source": "Historical Ground Climate Database (Fallback)"
    }

