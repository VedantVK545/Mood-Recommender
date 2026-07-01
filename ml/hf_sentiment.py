"""
HuggingFace Transformers sentiment analysis module.

Provides an optional upgrade over VADER using a transformer model.
The model is downloaded and loaded on first use (lazy), so the app
starts fast even if the user never clicks "Advanced" mode.

Uses distilbert-base-uncased-finetuned-sst-2-english which returns
binary positive/negative scores. A compound score is derived from
the positive and negative logits so the result plugs into the same
detect_mood() thresholds used by VADER.

Dependencies (optional): transformers, torch
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Try to load transformers — graceful fallback if not installed
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    pipeline = None  # type: ignore

# Lazy-loaded pipeline singleton
_hf_pipeline = None
_model_name = "distilbert-base-uncased-finetuned-sst-2-english"


def _get_pipeline():
    """Get or create the HuggingFace pipeline (lazy load)."""
    global _hf_pipeline
    if _hf_pipeline is not None:
        return _hf_pipeline

    if not TRANSFORMERS_AVAILABLE:
        raise RuntimeError(
            "HuggingFace Transformers not installed. "
            "Run: pip install transformers torch"
        )

    logger.info(f"Loading HuggingFace model: {_model_name}...")
    _hf_pipeline = pipeline(
        "sentiment-analysis",
        model=_model_name,
        tokenizer=_model_name,
    )
    logger.info(f"Model {_model_name} loaded successfully")
    return _hf_pipeline


def analyze_sentiment_hf(text: str) -> Dict[str, float]:
    """
    Analyze sentiment using HuggingFace transformers.

    Maps the binary classification to a dict matching the VADER format,
    with a compound score in [-1, 1] that can be fed into detect_mood().

    Args:
        text: Input text to analyze

    Returns:
        Dict with keys: positive, negative, neutral, compound
    """
    pipe = _get_pipeline()
    result = pipe(text[:512])[0]  # Truncate to model max length
    label = result["label"].lower()
    score = result["score"]

    # Derive compound score in [-1, 1] range
    # Positive label → compound = score (0 to 1)
    # Negative label → compound = -score (-1 to 0)
    if label == "positive":
        compound = score
        positive = score
        negative = 0.0
    elif label == "negative":
        compound = -score
        positive = 0.0
        negative = score
    else:
        compound = 0.0
        positive = 0.0
        negative = 0.0

    return {
        "positive": round(positive, 3),
        "negative": round(negative, 3),
        "neutral": round(max(0.0, 1.0 - positive - negative), 3),
        "compound": round(compound, 3),
    }


def analyze_text_emotions_hf(text: str) -> Dict:
    """
    Full emotion analysis using HuggingFace, matching VADER's output format.

    Args:
        text: Input text

    Returns:
        Dict with mood, emoji, description, sentiment_score,
        sentiment_details, and confidence
    """
    from ml.sentiment import detect_mood, get_mood_emoji, get_mood_description

    sentiment_details = analyze_sentiment_hf(text)
    compound_score = sentiment_details["compound"]
    mood = detect_mood(compound_score)

    return {
        "mood": mood,
        "emoji": get_mood_emoji(mood),
        "description": get_mood_description(mood),
        "sentiment_score": compound_score,
        "sentiment_details": sentiment_details,
        "confidence": abs(compound_score),
        "model": "HuggingFace Transformers",
    }
