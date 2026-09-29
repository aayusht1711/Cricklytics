# 🏏 Cricklytics V2.0 — Enterprise AI Cricket Analytics Platform

> **"Decode every seam, spin, and match-defining duel. Built for players, strategists, and cricket purists."**

---

## 📌 Executive Overview

**Cricklytics V2.0** is an enterprise-grade AI scouting, tactical match intelligence, and duel simulation monorepo platform. Key capabilities include:
- **0-Latency WebSocket Match Tracking** (`ws://localhost:8000/ws/live-match`)
- **Batter vs Bowler Tactical Duel Simulator & Probability Engine**
- **AI Player Scouting Database** (`/api/scout/players`)
- **Next.js 15+ App Router Frontend** with Tailwind CSS dark-mode sports design

---

## 🏗️ System Monorepo Architecture

```
/cricklytics-v2/
├── /backend/
│   ├── /app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI REST & WebSocket Server
│   │   ├── models.py       # Pydantic & SQLAlchemy Schemas
│   │   ├── database.py     # SQLite Database Setup
│   │   └── crud.py         # Database CRUD Operations
│   ├── /ai_engine/
│   │   ├── __init__.py
│   │   └── simulator.py    # Tactical Duel Probability Simulator
│   ├── requirements.txt    # Python Dependencies (FastAPI, SQLAlchemy, NumPy)
│   └── Dockerfile          # Multi-stage Optimized Python Container
├── /frontend/
│   ├── /app/
│   │   ├── layout.js       # Next.js App Router Root Layout
│   │   ├── page.js         # Cricklytics V2.0 Landing Page
│   │   ├── /tactics/
│   │   │   └── page.js     # Batter vs Bowler Tactical Duel Simulator UI
│   │   └── /live/
│   │       └── page.js     # WebSocket 0-Latency Live Score Tracking UI
│   ├── package.json        # Next.js & React Dependencies
│   └── Dockerfile          # Alpine Node.js Container for Next.js
├── docker-compose.yml      # Monorepo Container Orchestration
└── README.md               # System Documentation
```

---

## 🚀 Quick Start Guide

### Option 1: Run with Docker Compose (Recommended)

```bash
# Clone or enter directory
cd cricklytics-v2

# Build and start all services
docker-compose up --build
```
- **Frontend App**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **Interactive OpenAPI Docs**: `http://localhost:8000/docs`

---

### Option 2: Run Locally (Without Docker)

#### 1. Backend Setup (FastAPI & Probability Engine)
```bash
cd backend

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch FastAPI backend
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup (Next.js 15+)
```bash
cd frontend

# Install Node dependencies
npm install

# Launch Next.js dev server
npm run dev
```

---

## 📡 REST & WebSocket API Specifications

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Health check & API version |
| `POST` | `/api/simulate` | Calculates physical matchup probabilities & 6-ball over blueprint |
| `POST` | `/api/scout/players` | Saves scouted player profile into database |
| `GET` | `/api/scout/players` | Fetches all scouted player records |
| `WS` | `/ws/live-match` | 0-Latency WebSocket broadcast for live score ticker |

---

## 🎯 Tactical Simulation Engine Highlights

| Parameter | Function |
| :--- | :--- |
| **Matchup Factors** | Pitch condition (*Green Top*, *Rank Turner*, *Flat Deck*), Phase (*Powerplay*, *Middle*, *Death*), Dew Factor |
| **Calculated Outputs** | Wicket Probability, Boundary Probability, Dot Ball Rate, Expected RPO |
| **Toss Analytics** | Automated Toss Strategy & Dew Penalty Calculation |
| **6-Ball Blueprint** | Ball-by-ball tactical delivery sequence with target zones |

---

## 🌐 Deployment Instructions

### Deploy Frontend to Netlify
1. Connect your repository to **Netlify**.
2. Base Directory: `frontend`
3. Build Command: `npm run build`
4. Publish Directory: `frontend/.next`
5. Environment Variable: `NEXT_PUBLIC_BACKEND_URL=https://your-backend.onrender.com`

### Deploy Backend to Render / Railway
1. Connect repository to **Render.com** as a Web Service.
2. Root Directory: `backend`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## 📄 License

Distributed under the MIT License. Built for enterprise cricket analytics & match tactical intelligence.
