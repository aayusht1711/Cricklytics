import streamlit as st
import pandas as pd
import random


@st.cache_data
def _build_questions(data):
    """Build 10 quiz questions from real dataset stats."""
    questions = []

    # Q1: Most sixes all time
    sixes = data[data["runs_batter"] == 6].groupby("batter").size().sort_values(ascending=False)
    correct = sixes.index[0]
    options = list(sixes.index[:4])
    random.shuffle(options)
    questions.append({
        "question": "Who has hit the most sixes in IPL history?",
        "options":  options,
        "answer":   correct,
        "fact":     f"{correct} smashed {sixes.iloc[0]} sixes across their IPL career.",
        "emoji":    "💥",
    })

    # Q2: 2016 Orange Cap
    s2016 = data[data["season"].astype(str) == "2016"].groupby("batter")["runs_batter"].sum().sort_values(ascending=False)
    if not s2016.empty:
        correct = s2016.index[0]
        options = list(s2016.index[:4])
        random.shuffle(options)
        questions.append({
            "question": "Who won the Orange Cap in IPL 2016?",
            "options":  options,
            "answer":   correct,
            "fact":     f"{correct} scored {s2016.iloc[0]} runs in 2016 — a record that still stands.",
            "emoji":    "🟠",
        })

    # Q3: Most match wins team
    wins = data.drop_duplicates("match_id").groupby("match_won_by").size().sort_values(ascending=False)
    correct = wins.index[0]
    options = list(wins.index[:4])
    random.shuffle(options)
    questions.append({
        "question": "Which team has won the most IPL matches?",
        "options":  options,
        "answer":   correct,
        "fact":     f"{correct} have won {wins.iloc[0]} IPL matches — more than any other franchise.",
        "emoji":    "🏆",
    })

    # Q4: Highest individual score
    match_scores = data.groupby(["match_id", "batter"])["runs_batter"].sum().sort_values(ascending=False)
    correct_batter = match_scores.index[0][1]
    correct_score  = int(match_scores.iloc[0])
    all_batters    = data["batter"].value_counts().index[:20].tolist()
    options        = [correct_batter] + [b for b in all_batters if b != correct_batter][:3]
    random.shuffle(options)
    questions.append({
        "question": f"Who holds the record for the highest individual score ({correct_score} runs) in IPL?",
        "options":  options,
        "answer":   correct_batter,
        "fact":     f"{correct_batter} scored {correct_score} runs in a single match — the highest ever in IPL.",
        "emoji":    "🏏",
    })

    # Q5: Most wickets
    wickets = data.groupby("bowler")["bowler_wicket"].sum().sort_values(ascending=False)
    correct = wickets.index[0]
    options = list(wickets.index[:4])
    random.shuffle(options)
    questions.append({
        "question": "Who has taken the most wickets in IPL history?",
        "options":  options,
        "answer":   correct,
        "fact":     f"{correct} has taken {int(wickets.iloc[0])} wickets — the most in IPL history.",
        "emoji":    "🎯",
    })

    # Q6: Most Player of Match
    pom = data.drop_duplicates("match_id").groupby("player_of_match").size().sort_values(ascending=False)
    correct = pom.index[0]
    options = list(pom.index[:4])
    random.shuffle(options)
    questions.append({
        "question": "Who has won the Player of the Match award most times in IPL?",
        "options":  options,
        "answer":   correct,
        "fact":     f"{correct} has won Player of the Match {pom.iloc[0]} times — more than anyone else.",
        "emoji":    "🌟",
    })

    # Q7: Most dot balls bowled
    dots = data[data["runs_batter"] == 0].groupby("bowler").size().sort_values(ascending=False)
    correct = dots.index[0]
    options = list(dots.index[:4])
    random.shuffle(options)
    questions.append({
        "question": "Which bowler has bowled the most dot balls in IPL?",
        "options":  options,
        "answer":   correct,
        "fact":     f"{correct} has bowled {dots.iloc[0]} dot balls — the most pressure deliveries in IPL.",
        "emoji":    "🔴",
    })

    # Q8: Total sixes in IPL
    total_sixes = int((data["runs_batter"] == 6).sum())
    opts = [str(total_sixes), str(total_sixes - 2000), str(total_sixes + 3000), str(total_sixes - 5000)]
    random.shuffle(opts)
    questions.append({
        "question": "How many sixes have been hit in IPL history (across all seasons)?",
        "options":  opts,
        "answer":   str(total_sixes),
        "fact":     f"A staggering {total_sixes:,} sixes have been hit in IPL — that is one six roughly every 19 balls.",
        "emoji":    "🚀",
    })

    # Q9: Best bowling economy (min 300 balls)
    bowl_stats = data.groupby("bowler").agg(runs=("runs_total","sum"), balls=("valid_ball","sum"))
    bowl_stats = bowl_stats[bowl_stats["balls"] >= 300]
    bowl_stats["econ"] = (bowl_stats["runs"] / bowl_stats["balls"] * 6).round(2)
    best_econ = bowl_stats.sort_values("econ").iloc[0]
    correct   = bowl_stats.sort_values("econ").index[0]
    options   = list(bowl_stats.sort_values("econ").index[:4])
    random.shuffle(options)
    questions.append({
        "question": "Which bowler has the best economy rate in IPL (min 300 balls)?",
        "options":  options,
        "answer":   correct,
        "fact":     f"{correct} has an economy of {best_econ['econ']} — the tightest in IPL history.",
        "emoji":    "💨",
    })

    # Q10: Most matches played by team
    matches = data.drop_duplicates("match_id").groupby("batting_team").size().sort_values(ascending=False)
    correct = matches.index[0]
    options = list(matches.index[:4])
    random.shuffle(options)
    questions.append({
        "question": "Which team has played the most IPL matches?",
        "options":  options,
        "answer":   correct,
        "fact":     f"{correct} have played {matches.iloc[0]} IPL matches — the most of any franchise.",
        "emoji":    "📊",
    })

    return questions


def show_quiz_view(data):
    st.markdown("<h2>IPL Trivia Quiz</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:rgba(255,255,255,0.5);margin-bottom:20px;'>"
        "10 questions — all answers come from real IPL data. "
        "How well do you know your cricket?</p>",
        unsafe_allow_html=True,
    )

    # Session state init
    if "quiz_started"   not in st.session_state: st.session_state.quiz_started   = False
    if "quiz_questions" not in st.session_state: st.session_state.quiz_questions = []
    if "quiz_index"     not in st.session_state: st.session_state.quiz_index     = 0
    if "quiz_score"     not in st.session_state: st.session_state.quiz_score     = 0
    if "quiz_answers"   not in st.session_state: st.session_state.quiz_answers   = {}
    if "quiz_done"      not in st.session_state: st.session_state.quiz_done      = False
    if "last_answered"  not in st.session_state: st.session_state.last_answered  = None

    # Start screen
    if not st.session_state.quiz_started:
        st.markdown(
            "<div class='card' style='border-left: 5px solid #00e5ff; padding: 24px; text-align: center;'>"
            "<div style='font-size: 48px; margin-bottom: 12px;'>🏆</div>"
            "<h3 style='color:#00e5ff; font-size: 26px; font-weight:800; margin-bottom:10px;'>Ready to test your IPL knowledge?</h3>"
            "<p style='font-size: 16px; color:white;'>10 questions generated dynamically from real IPL data</p>"
            "<p style='color:rgba(255,255,255,0.6); font-size: 13px; margin-top: 5px;'>"
            "Questions cover all-time records, Orange/Purple Caps, most sixes, dot ball statistics, and team matches.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button("Start Quiz", use_container_width=True):
            questions = _build_questions(data)
            random.shuffle(questions)
            st.session_state.quiz_questions = questions[:10]
            st.session_state.quiz_started   = True
            st.session_state.quiz_index     = 0
            st.session_state.quiz_score     = 0
            st.session_state.quiz_answers   = {}
            st.session_state.quiz_done      = False
            st.session_state.last_answered  = None
            st.rerun()
        return

    # Results screen
    if st.session_state.quiz_done:
        score = st.session_state.quiz_score
        total = len(st.session_state.quiz_questions)
        pct   = round(score / total * 100)

        if pct == 100:   grade, color, msg = "Perfect Score!", "#FFE66D", "You are an IPL encyclopedia!"
        elif pct >= 80:  grade, color, msg = "Excellent Job!", "#4ECDC4", "You really know your cricket inside out."
        elif pct >= 60:  grade, color, msg = "Good Effort!", "#00FFFF", "Solid cricket knowledge. Well played!"
        elif pct >= 40:  grade, color, msg = "Not Bad!", "#F7700E", "Room to improve. Try another run!"
        else:            grade, color, msg = "Keep Learning!", "#FF6B6B", "Brush up on your IPL history and try again."

        st.markdown(
            f"<div class='card' style='border-left: 5px solid {color}; text-align: center; padding: 30px 20px; margin-bottom: 24px;'>"
            f"  <div style='font-size: 56px; margin-bottom: 10px;'>🏆</div>"
            f"  <h3 style='color:{color}; font-size: 30px; font-weight:800; margin-bottom:4px;'>{grade}</h3>"
            f"  <div style='font-size: 40px; font-weight: 800; color: white; margin: 10px 0;'>{score} / {total}</div>"
            f"  <div style='background:rgba(255,255,255,0.06); display:inline-block; padding: 4px 16px; border-radius:99px; font-weight: 700; color:{color}; margin-bottom: 12px;'>{pct}% Accuracy</div>"
            f"  <p style='color:rgba(255,255,255,0.8); font-size: 15px; max-width: 500px; margin: 0 auto;'>{msg}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # Answer review
        st.markdown("<h3 style='margin: 30px 0 16px; font-family:\"Rajdhani\", sans-serif; font-weight:700;'>Answer Review</h3>", unsafe_allow_html=True)
        for i, q in enumerate(st.session_state.quiz_questions):
            user_ans = st.session_state.quiz_answers.get(i, "Not answered")
            correct  = q["answer"]
            is_right = user_ans == correct
            icon     = "✅" if is_right else "❌"
            card_border = "#4ECDC4" if is_right else "#FF6B6B"
            st.markdown(
                f"<div class='card' style='border-left: 5px solid {card_border};'>"
                f"  <p style='font-size:16px; font-weight:700; color:white;'>{icon} Q{i+1}: {q['question']}</p>"
                f"  <div style='display:flex; gap:20px; font-size:13px; margin: 6px 0;'>"
                f"     <div><span style='color:rgba(255,255,255,0.5);'>Your answer:</span> <b style='color:{card_border};'>{user_ans}</b></div>"
                + (f"     <div><span style='color:rgba(255,255,255,0.5);'>Correct:</span> <b style='color:#4ECDC4;'>{correct}</b></div>" if not is_right else "")
                + f"  </div>"
                f"  <p style='color:rgba(255,255,255,0.65); font-size:12px; margin-top:8px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 6px;'>"
                f"     {q['emoji']} &nbsp;{q['fact']}"
                f"  </p>"
                f"</div>",
                unsafe_allow_html=True,
            )

        if st.button("Play Again", use_container_width=True):
            st.session_state.quiz_started  = False
            st.session_state.quiz_done     = False
            st.session_state.quiz_score    = 0
            st.session_state.quiz_index    = 0
            st.session_state.quiz_answers  = {}
            st.session_state.last_answered = None
            st.rerun()
        return

    # Active quiz
    questions = st.session_state.quiz_questions
    idx       = st.session_state.quiz_index
    total     = len(questions)
    q         = questions[idx]

    # Progress bar
    progress = idx / total
    
    st.markdown(
        f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;'>"
        f"  <div style='background:rgba(0,229,255,0.08); color:#00e5ff; border:1px solid rgba(0,229,255,0.25); border-radius:99px; padding:3px 14px; font-size:12px; font-weight:700;'>Question {idx+1} of {total}</div>"
        f"  <div style='background:rgba(255,255,255,0.05); color:white; border-radius:99px; padding:3px 14px; font-size:12px; font-weight:700;'>Score: <span style='color:#FFE66D;'>{st.session_state.quiz_score}</span></div>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.progress(progress)

    # Question card
    st.markdown(
        f"<div class='card' style='border-left: 5px solid #00e5ff; padding: 24px; margin-top:14px;'>"
        f"  <h3 style='color:white; font-size:20px; font-weight:700; margin:0; line-height:1.4;'>{q['emoji']} &nbsp; {q['question']}</h3>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Show result of last answer
    if st.session_state.last_answered is not None:
        user_ans = st.session_state.last_answered
        correct  = questions[idx - 1]["answer"] if idx > 0 else q["answer"]
        is_right = user_ans == correct

        if is_right:
            st.markdown(
                f"<div class='card' style='border-left: 5px solid #4ECDC4; background:rgba(78,205,196,0.05);'>"
                f"  <p style='color:#4ECDC4; font-weight:700; margin:0 0 4px 0;'>✅ Correct! +1 Point</p>"
                f"  <p style='color:rgba(255,255,255,0.75); font-size:13px; margin:0;'>"
                f"    {questions[idx-1]['emoji']} {questions[idx-1]['fact']}"
                f"  </p>"
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div class='card' style='border-left: 5px solid #FF6B6B; background:rgba(255,107,107,0.05);'>"
                f"  <p style='color:#FF6B6B; font-weight:700; margin:0 0 4px 0;'>❌ Wrong! Correct answer: {correct}</p>"
                f"  <p style='color:rgba(255,255,255,0.75); font-size:13px; margin:0;'>"
                f"    {questions[idx-1]['emoji']} {questions[idx-1]['fact']}"
                f"  </p>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # Answer buttons
    st.markdown("<p style='color:rgba(255,255,255,0.5); font-size:13px; margin:20px 0 10px;'>Select your answer:</p>",
                unsafe_allow_html=True)

    cols = st.columns(2)
    for i, option in enumerate(q["options"]):
        col = cols[i % 2]
        if col.button(str(option), key=f"q{idx}_{option}", use_container_width=True):
            is_correct = str(option) == str(q["answer"])
            st.session_state.quiz_answers[idx] = str(option)
            if is_correct:
                st.session_state.quiz_score += 1
            st.session_state.last_answered = str(option)
            st.session_state.quiz_index   += 1
            if st.session_state.quiz_index >= total:
                st.session_state.quiz_done = True
            st.rerun()
