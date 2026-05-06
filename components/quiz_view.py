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
    bowl_stats = data.groupby("bowler").agg(runs=("runs_bowler","sum"), balls=("valid_ball","sum"))
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
            "<div class='card'>"
            "<h3 style='color:#FFE66D;'>Ready to test your IPL knowledge?</h3>"
            "<p>10 questions | All answers from real data | No time limit</p>"
            "<p style='margin-top:10px;color:rgba(255,255,255,0.5);'>"
            "Questions cover: records, stats, champions, players</p>"
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

        if pct == 100:   grade, color, msg = "Perfect!", "#FFE66D", "You are an IPL encyclopedia!"
        elif pct >= 80:  grade, color, msg = "Excellent!", "#4ECDC4", "You really know your cricket."
        elif pct >= 60:  grade, color, msg = "Good job!", "#00FFFF", "Solid cricket knowledge."
        elif pct >= 40:  grade, color, msg = "Not bad!", "#F7700E", "Room to improve though."
        else:            grade, color, msg = "Keep learning!", "#FF6B6B", "Brush up on your IPL history."

        st.markdown(
            f"<div class='card'>"
            f"<h3 style='color:{color};font-size:28px;'>{grade}</h3>"
            f"<p style='font-size:20px;'>You scored <b style='color:{color};'>{score} / {total}</b> ({pct}%)</p>"
            f"<p style='color:rgba(255,255,255,0.6);margin-top:8px;'>{msg}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # Answer review
        st.markdown("<h3>Answer Review</h3>", unsafe_allow_html=True)
        for i, q in enumerate(st.session_state.quiz_questions):
            user_ans = st.session_state.quiz_answers.get(i, "Not answered")
            correct  = q["answer"]
            is_right = user_ans == correct
            icon     = "✅" if is_right else "❌"
            color2   = "#4ECDC4" if is_right else "#FF6B6B"
            st.markdown(
                f"<div class='card'>"
                f"<p>{icon} <b>Q{i+1}:</b> {q['question']}</p>"
                f"<p style='color:{color2};'>Your answer: {user_ans}</p>"
                + (f"<p style='color:#4ECDC4;'>Correct: {correct}</p>" if not is_right else "")
                + f"<p style='color:rgba(255,255,255,0.5);font-size:12px;margin-top:6px;'>"
                  f"{q['emoji']} {q['fact']}</p>"
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
        f"<p style='color:rgba(255,255,255,0.5);font-size:13px;'>"
        f"Question {idx+1} of {total} &nbsp;|&nbsp; "
        f"Score: {st.session_state.quiz_score}</p>",
        unsafe_allow_html=True,
    )
    st.progress(progress)

    # Question card
    st.markdown(
        f"<div class='card'>"
        f"<p style='font-size:12px;color:rgba(255,255,255,0.4);margin-bottom:8px;'>"
        f"QUESTION {idx+1}</p>"
        f"<h3 style='color:white;font-size:18px;'>{q['emoji']} &nbsp; {q['question']}</h3>"
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
                f"<div class='card'>"
                f"<p style='color:#4ECDC4;font-weight:700;'>✅ Correct! +1 point</p>"
                f"<p style='color:rgba(255,255,255,0.6);font-size:13px;'>"
                f"{questions[idx-1]['emoji']} {questions[idx-1]['fact']}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div class='card'>"
                f"<p style='color:#FF6B6B;font-weight:700;'>❌ Wrong! Correct answer: {correct}</p>"
                f"<p style='color:rgba(255,255,255,0.6);font-size:13px;'>"
                f"{questions[idx-1]['emoji']} {questions[idx-1]['fact']}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # Answer buttons
    st.markdown("<p style='color:rgba(255,255,255,0.5);font-size:13px;margin-top:12px;'>Choose your answer:</p>",
                unsafe_allow_html=True)

    for option in q["options"]:
        if st.button(str(option), key=f"q{idx}_{option}", use_container_width=True):
            is_correct = str(option) == str(q["answer"])
            st.session_state.quiz_answers[idx] = str(option)
            if is_correct:
                st.session_state.quiz_score += 1
            st.session_state.last_answered = str(option)
            st.session_state.quiz_index   += 1
            if st.session_state.quiz_index >= total:
                st.session_state.quiz_done = True
            st.rerun()
