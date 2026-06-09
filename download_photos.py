"""
Run this ONCE from your project root:
    python download_photos.py

Downloads all IPL 2026 player photos to static/player_photos/
Works because your browser can fetch these — this script mimics a browser.
"""
import requests, os, time, pandas as pd
from pathlib import Path

os.makedirs("static/player_photos", exist_ok=True)

df = pd.read_csv("player_profiles_2026.csv")
df = df[df["photo_id"].notna() & (df["photo_id"] != "")]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.iplt20.com/",
    "Origin":  "https://www.iplt20.com",
}

ok, fail = 0, 0
for _, row in df.iterrows():
    try:
        pid = str(int(float(row["photo_id"])))
    except Exception:
        pid = str(row["photo_id"]).strip()
    
    if not pid or pid.lower() == 'nan':
        continue

    url  = f"https://documents.iplt20.com/ipl/IPLHeadshot2026/{pid}.png"
    dest = f"static/player_photos/{pid}.png"

    if os.path.exists(dest):
        ok += 1
        continue

    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code == 200 and len(r.content) > 1000:
            with open(dest, "wb") as f:
                f.write(r.content)
            print(f"  OK  {row['name']} ({pid})")
            ok += 1
        else:
            print(f"  --  {row['name']} ({r.status_code})")
            fail += 1
        time.sleep(0.3)   # be polite to their server
    except Exception as e:
        print(f"  ERR {row['name']}: {e}")
        fail += 1

print(f"\nDone: {ok} saved, {fail} failed")
print(f"Photos in: static/player_photos/")
