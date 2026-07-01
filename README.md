# Mood

Tell us how you feel — get personalized music and movie recommendations.

A mood-based recommendation system built with Flask, VADER sentiment analysis, and a modern glass-morphism UI.

## Quick Start

```bash
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000**.

The database (`database.db`) is auto-created on first run with 50 songs and 50 movies.

## Features

- **Mood detection** — Type how you feel or pick a quick mood chip
- **50 songs + 50 movies** — Recommendations across 5 moods (Happy, Joyful, Neutral, Sad, Depressed)
- **Spotify links** — Every song links directly to Spotify
- **Movie posters** — TMDB-powered poster images
- **YouTube trailers** — One-click trailer search (cached per movie)
- **Genre filter** — Narrow recommendations by genre
- **Mood history chart** — Track emotional trends over time (Chart.js)
- **Basic / Advanced sentiment** — Switch between VADER (instant) and HuggingFace Transformers
- **Dark mode** — Persistent theme toggle
- **Share results** — Copy mood analysis to clipboard

## Project Structure

```
├── app.py                 # Flask entry point
├── config.py              # Configuration
├── database/
│   ├── __init__.py         # DB connection + 100 seed entries
│   └── models.py           # Song, Movie, RecommendationHistory models
├── ml/
│   ├── sentiment.py        # VADER sentiment analysis (default)
│   ├── hf_sentiment.py     # HuggingFace Transformers engine (optional)
│   └── recommender.py      # Recommendation logic
├── routes/
│   └── recommendation.py   # API endpoints
├── utils/
│   └── youtube.py          # YouTube trailer search
├── static/
│   ├── css/style.css       # Design system (glass-morphism, mood-reactive colors)
│   └── js/main.js          # Frontend application
├── templates/
│   └── index.html          # Single-page app
├── test_app.py             # 13 tests (pytest)
├── pytest.ini              # Test configuration
├── Dockerfile              # Production container
├── docker-compose.yml      # Docker orchestration
├── requirements.txt        # Python dependencies
└── .env.example            # Environment template
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze` | Analyze mood + get song/movie recommendations |
| GET | `/api/mood-stats` | Available entries per mood |
| GET | `/api/mood-history` | Historical mood data for chart |
| GET | `/api/trailer/<id>` | Fetch/cache YouTube trailer for a movie |
| GET | `/api/health` | Health check |
| GET | `/api/example` | Example analysis response |

### POST /api/analyze

```json
{ "text": "I feel amazing today!" }

{ "text": "I feel amazing today!", "model": "huggingface" }
```

Returns mood, sentiment score, 5 songs with Spotify links, and 5 movies with poster URLs.

## Advanced Sentiment

The app uses **VADER** by default (lightweight, instant, no download). To enable **HuggingFace Transformers**:

```bash
pip install transformers torch
```

Toggle the "Advanced" switch in the UI. The model downloads on first use (~260 MB).

## Running Tests

```bash
pytest
```

## Tech Stack

Backend: Flask, SQLAlchemy, SQLite  
Sentiment: VADER (NLTK) / distilBERT (Transformers)  
Frontend: Vanilla JS, Chart.js, CSS custom properties

## License

MIT
