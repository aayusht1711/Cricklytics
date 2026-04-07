def player_stats(data, player):
    df = data[data['batter'] == player]
    runs = df['runs_batter'].sum()
    balls = df['balls_faced'].sum()
    sr = (runs/balls)*100 if balls>0 else 0
    return runs, sr

def player_trend(data, player):
    return data[data['batter']==player].groupby('match_id')['runs_batter'].sum()

def team_performance(data):
    return data.groupby('batting_team')['runs_batter'].sum().sort_values(ascending=False)

def top_players(data):
    return data.groupby('batter')['runs_batter'].sum().sort_values(ascending=False).head(10)