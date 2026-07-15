import time
import re
import urllib.request
import xml.etree.ElementTree as ET
from sqlalchemy.orm import Session
from database import SessionLocal, Match, TeamStats

RSS_URL = 'http://static.cricinfo.com/rss/livescores.xml'

def extract_team_and_score(raw_string):
    
    match = re.search(r'^(.*?) ([\d/& *]+)$', raw_string.strip())
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return raw_string.strip(), ""

def fetch_and_update():
    db = SessionLocal()
    try:
        req = urllib.request.Request(RSS_URL, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        xml_data = response.read()
        root = ET.fromstring(xml_data)
        
        matches_found = []
        for item in root.findall('.//item'):
            title = item.find('title').text
            if " v " in title:
                parts = title.split(" v ")
                if len(parts) == 2:
                    t1_name, t1_score = extract_team_and_score(parts[0])
                    t2_name, t2_score = extract_team_and_score(parts[1])
                    matches_found.append({
                        "t1_name": t1_name, "t1_score": t1_score,
                        "t2_name": t2_name, "t2_score": t2_score,
                        "title": title
                    })
        
        if len(matches_found) >= 2:
            # Update Test Match (Match ID = 1)
            match1_data = matches_found[0]
            match1 = db.query(Match).filter(Match.id == 1).first()
            if match1:
                match1.team1 = match1_data['t1_name'][:15]
                match1.team2 = match1_data['t2_name'][:15]
                match1.status_text = "Live Scraped"
                match1.tournament = "Global Cricket"
                match1.target = "N/A"
                match1.partnership = "Live"
                match1.status_message = "Data provided by Web Scraper"
                
                if match1.team1_stats:
                    match1.team1_stats.score_string = match1_data['t1_score'] if match1_data['t1_score'] else "Yet to bat"
                    match1.team1_stats.team_name = match1.team1
                if match1.team2_stats:
                    match1.team2_stats.score_string = match1_data['t2_score'] if match1_data['t2_score'] else "Yet to bat"
                    match1.team2_stats.team_name = match1.team2
            
            # Update T20 Match (Match ID = 2)
            match2_data = matches_found[1]
            match2 = db.query(Match).filter(Match.id == 2).first()
            if match2:
                match2.team1 = match2_data['t1_name'][:15]
                match2.team2 = match2_data['t2_name'][:15]
                match2.status_text = "Live Scraped"
                match2.tournament = "Global Cricket"
                
                if match2.team1_stats:
                    match2.team1_stats.score_string = match2_data['t1_score'] if match2_data['t1_score'] else "Yet to bat"
                    match2.team1_stats.team_name = match2.team1
                if match2.team2_stats:
                    match2.team2_stats.score_string = match2_data['t2_score'] if match2_data['t2_score'] else "Yet to bat"
                    match2.team2_stats.team_name = match2.team2
            
            db.commit()
            print(f"Successfully scraped and updated database with {match1_data['title']} and {match2_data['title']}")
            
            try:
                urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8001/api/internal/notify_update", method="POST"))
            except Exception as e:
                pass
                
    except Exception as e:
        print(f"Error fetching data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting Cricklytics Web Scraper...")
    while True:
        fetch_and_update()
        time.sleep(10) # Scrape every 10 seconds
