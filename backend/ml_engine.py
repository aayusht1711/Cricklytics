import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

MODEL_PATH = "model.pkl"

def generate_synthetic_data(num_rows=50000):
    print(f"Synthesizing {num_rows} historical delivery records...")
    
  
    np.random.seed(42)
    
    # Batsman stats
    batsman_control = np.random.uniform(60, 95, num_rows) # percentage
    batsman_power = np.random.uniform(50, 99, num_rows)
    
    # Bowler stats
    bowler_economy = np.random.uniform(5.5, 10.5, num_rows) # RPO
    bowler_strike_rate = np.random.uniform(12, 28, num_rows) # balls per wicket
    
    # Match context (0 = Powerplay, 1 = Middle, 2 = Death)
    match_phase = np.random.randint(0, 3, num_rows)
    
    # Base probabilities for outcome (0=Dot, 1=Single/Two, 2=Boundary, 3=Wicket)
    # We will compute a weighted score to determine the outcome.
    
    outcomes = []
    for i in range(num_rows):
        control = batsman_control[i]
        power = batsman_power[i]
        economy = bowler_economy[i]
        sr = bowler_strike_rate[i]
        phase = match_phase[i]
        
        # Calculate risk factor
        risk = (100 - control) * 0.4 + (power * 0.3) + (economy * 2) - (sr * 1.5)
        
        # Adjust for phase
        if phase == 0: # Powerplay
            risk += 15
        elif phase == 2: # Death
            risk += 30
            
        # Add random noise
        risk += np.random.normal(0, 10)
        
        # Determine outcome based on calculated risk thresholds
        if risk > 80:
            outcome = 3 # Wicket (High risk taken, or bowler dominance)
        elif risk > 50:
            outcome = 2 # Boundary (Risk paid off)
        elif risk > 10:
            outcome = 1 # Single/Two (Safe rotation)
        else:
            outcome = 0 # Dot (Bowler tight, batsman defensive)
            
        # Some random normalization to ensure all classes exist
        if np.random.random() < 0.1:
            outcome = np.random.randint(0, 4)
            
        outcomes.append(outcome)
        
    df = pd.DataFrame({
        'batsman_control': batsman_control,
        'batsman_power': batsman_power,
        'bowler_economy': bowler_economy,
        'bowler_strike_rate': bowler_strike_rate,
        'match_phase': match_phase,
        'outcome': outcomes
    })
    
    return df

def train_and_save_model():
    df = generate_synthetic_data()
    
    X = df.drop('outcome', axis=1)
    y = df['outcome']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training RandomForestClassifier...")
    clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    clf.fit(X_train, y_train)
    
    print("Evaluating Model...")
    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred))
    
    print(f"Saving model to {MODEL_PATH}...")
    joblib.dump(clf, MODEL_PATH)
    print("ML Engine Ready.")

if __name__ == "__main__":
    train_and_save_model()
