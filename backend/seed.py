import database
from database import SessionLocal, Match, TeamStats, SessionData, BattleZone, PitchDiagnostics

db = SessionLocal()

# Clear existing data to avoid duplicates during testing
db.query(PitchDiagnostics).delete()
db.query(BattleZone).delete()
db.query(SessionData).delete()
db.query(TeamStats).delete()
db.query(Match).delete()
db.commit()

# --- 1. SEED TEST MATCH ---
test_match = Match(
    format="Test",
    tournament="Border-Gavaskar Trophy",
    team1="IND",
    team2="AUS",
    status_text="Day 4, Session 2",
    day=4,
    target=320,
    partnership="45 (98)",
    status_message="IND needs 200 runs"
)
db.add(test_match)
db.commit()
db.refresh(test_match)

db.add(TeamStats(match_id=test_match.id, team_name="IND", score_string="345 & 120/3"))
db.add(TeamStats(match_id=test_match.id, team_name="AUS", score_string="280 & 184"))

# Sessions
db.add(SessionData(match_id=test_match.id, name="Morning", score="84/2", status="Aus Dominated", status_color="red", is_live=0))
db.add(SessionData(match_id=test_match.id, name="Afternoon (Live)", score="36/1", status="Ind Rebuilding", status_color="blue", is_live=1))
db.add(SessionData(match_id=test_match.id, name="Evening", score="Upcoming", status="", status_color="gray", is_live=0))

# Battle Zone
db.add(BattleZone(
    match_id=test_match.id,
    batsman_name="V. Kohli",
    batsman_stats="Batting (45*)",
    bowler_name="P. Cummins",
    bowler_stats="Bowling (1/24)",
    aggression_level=78,
    control_level=85
))

# Pitch Diagnostics
db.add(PitchDiagnostics(
    match_id=test_match.id,
    surface_wear="75% (Cracking)",
    spin_deviation="3.2°",
    weather="Overcast (22°C)"
))


# --- 2. SEED T20 MATCH ---
t20_match = Match(
    format="T20",
    tournament="T20 World Cup",
    team1="ENG",
    team2="WI",
    status_text="18.4 Overs",
    required_rate=25.50,
    equation="34 off 8"
)
db.add(t20_match)
db.commit()
db.refresh(t20_match)

db.add(TeamStats(match_id=t20_match.id, team_name="ENG", score_string="198/4"))
db.add(TeamStats(match_id=t20_match.id, team_name="WI", score_string="165/6"))

db.commit()
db.close()

print("✅ Successfully seeded the database with mock cricket matches!")
