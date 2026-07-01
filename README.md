# 🎭 Mood Recommender

Tell us how you feel — get personalized music and movie recommendations.

A mood-based recommendation system built with Flask, VADER sentiment analysis, and a modern glass-morphism UI.

## ✨ Features

### 🎯 Mood Detection
Type how you feel or pick a quick mood chip — VADER analyzes your sentiment across 5 moods (Happy, Joyful, Neutral, Sad, Depressed)

### 🎵 Music + 🎬 Movies
**50 songs and 50 movies** — curated picks for every mood, each with working Spotify links and TMDB poster images

### 🎥 YouTube Trailers
One-click trailer search for every movie (cached per movie so it loads instantly on repeat visits)

### 🎛️ Genre Filter
Narrow your recommendations by genre after mood is detected

### 📈 Mood History Chart
Track your emotional trends over time with an interactive Chart.js bar chart

### ⚡ Basic / Advanced Sentiment
Switch between lightweight VADER (instant, no download) or HuggingFace Transformers (more accurate)

### 🌙 Dark Mode
Persistent theme toggle that remembers your preference

### 📤 Share Results
Copy your mood analysis to clipboard with one click

## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| Backend | Flask, SQLAlchemy, SQLite |
| Sentiment | VADER (NLTK) / distilBERT (Transformers) |
| Frontend | Vanilla JS, Chart.js, CSS Custom Properties |
| Design | Glass-morphism, mood-reactive gradients |
| APIs | Spotify (direct links), TMDB (posters), YouTube (trailers) |

## 🚀 Quick Start

```bash
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000**.

The database (`database.db`) auto-creates on first run with all 100 seed entries.

## 📁 Project Structure

```
├── app.py                 # Flask entry point
├── config.py              # Configuration
├── database/
│   ├── __init__.py         # DB connection + seed data
│   └── models.py           # SQLAlchemy models
├── ml/
│   ├── sentiment.py        # VADER (default)
│   ├── hf_sentiment.py     # HuggingFace (optional)
│   └── recommender.py      # Recommendation logic
├── routes/
│   └── recommendation.py   # API endpoints
├── utils/
│   └── youtube.py          # YouTube trailer search
├── static/
│   ├── css/style.css       # Design system
│   └── js/main.js          # Frontend app
├── templates/
│   └── index.html          # Single-page app
├── test_app.py             # 13 tests
├── pytest.ini              # Test config
├── Dockerfile              # Production container
├── docker-compose.yml      # Docker setup
├── requirements.txt        # Dependencies
└── .env.example            # Environment template
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze` | Analyze mood + get recommendations |
| GET | `/api/mood-stats` | Available entries per mood |
| GET | `/api/mood-history` | Historical data for chart |
| GET | `/api/trailer/<id>` | Fetch/cache YouTube trailer |
| GET | `/api/health` | Health check |

## 🔬 Advanced Sentiment

The app uses **VADER** by default (lightweight, instant, no download). To enable **HuggingFace Transformers**:

```bash
pip install transformers torch
```

Toggle the **Advanced** switch in the UI. Model downloads on first use (~260 MB).

## 🧪 Running Tests

```bash
pytest
```

All 13 tests pass — covering sentiment analysis, API endpoints, and end-to-end flow.

## 📄 License

MIT License — see the [LICENSE](LICENSE) file for details.
