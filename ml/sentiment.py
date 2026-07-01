"""
Sentiment analysis module using VADER (Valence Aware Dictionary and sEntiment Reasoner).

This module provides sentiment analysis and mood detection from text input.
Maps sentiment compound scores to mood categories.
"""

from typing import Dict, Tuple
from nltk.sentiment import SentimentIntensityAnalyzer

# Initialize VADER sentiment analyzer
try:
    sia = SentimentIntensityAnalyzer()
except Exception as e:
    print(f"Warning: Could not initialize VADER: {e}")
    sia = None

# Mood thresholds based on VADER compound score
MOOD_THRESHOLDS = {
    'Happy': (0.5, 1.0),           # compound >= 0.5
    'Joyful': (0.1, 0.49),          # 0.1 to 0.49
    'Neutral': (-0.09, 0.09),       # -0.09 to 0.09
    'Sad': (-0.49, -0.1),           # -0.49 to -0.1
    'Depressed': (-1.0, -0.5),      # compound <= -0.5
}

# Mood emoji mapping for UI
MOOD_EMOJIS = {
    'Happy': '😄',
    'Joyful': '😊',
    'Neutral': '😐',
    'Sad': '😢',
    'Depressed': '😔',
}


def analyze_sentiment(text: str) -> Dict[str, float]:
    """
    Analyze sentiment of text using VADER.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Dictionary containing:
            - positive: Positive sentiment score (0-1)
            - negative: Negative sentiment score (0-1)
            - neutral: Neutral sentiment score (0-1)
            - compound: Overall compound sentiment score (-1 to 1)
            
    Example:
        >>> sentiment = analyze_sentiment("I'm feeling amazing!")
        >>> sentiment['compound']
        0.8316
    """
    if sia is None:
        raise RuntimeError("VADER sentiment analyzer not initialized")
    
    scores = sia.polarity_scores(text)
    return {
        'positive': scores['pos'],
        'negative': scores['neg'],
        'neutral': scores['neu'],
        'compound': scores['compound'],
    }


def detect_mood(compound_score: float) -> str:
    """
    Map compound sentiment score to mood category.
    
    Args:
        compound_score: VADER compound score (-1 to 1)
        
    Returns:
        Mood category: 'Happy', 'Joyful', 'Neutral', 'Sad', or 'Depressed'
    """
    for mood, (min_val, max_val) in MOOD_THRESHOLDS.items():
        if min_val <= compound_score <= max_val:
            return mood
    
    # Fallback (should not reach here if thresholds cover -1 to 1)
    return 'Neutral'


def get_mood_emoji(mood: str) -> str:
    """
    Get emoji representation for a mood.
    
    Args:
        mood: Mood category
        
    Returns:
        Emoji string
    """
    return MOOD_EMOJIS.get(mood, '😐')


def analyze_mood(text: str) -> Tuple[str, float, Dict[str, float]]:
    """
    Complete mood analysis pipeline.
    
    Performs sentiment analysis and maps to mood category.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Tuple containing:
            - mood: Detected mood category
            - sentiment_score: Compound sentiment score
            - sentiment_details: Full sentiment scores dictionary
            
    Example:
        >>> mood, score, details = analyze_mood("I feel amazing!")
        >>> mood
        'Happy'
        >>> score
        0.8316
    """
    sentiment_scores = analyze_sentiment(text)
    compound_score = sentiment_scores['compound']
    mood = detect_mood(compound_score)
    
    return mood, compound_score, sentiment_scores


def get_mood_description(mood: str) -> str:
    """
    Get a human-readable description of a mood.
    
    Args:
        mood: Mood category
        
    Returns:
        Description string
    """
    descriptions = {
        'Happy': 'Very positive and enthusiastic',
        'Joyful': 'Positive and cheerful',
        'Neutral': 'Neutral or balanced',
        'Sad': 'Negative or melancholic',
        'Depressed': 'Very negative and somber',
    }
    return descriptions.get(mood, 'Unknown mood')


def analyze_text_emotions(text: str) -> Dict:
    """
    Comprehensive emotion and mood analysis.
    
    Args:
        text: Input text
        
    Returns:
        Dictionary with complete analysis
    """
    mood, sentiment_score, sentiment_details = analyze_mood(text)
    
    return {
        'mood': mood,
        'emoji': get_mood_emoji(mood),
        'description': get_mood_description(mood),
        'sentiment_score': sentiment_score,
        'sentiment_details': sentiment_details,
        'confidence': abs(sentiment_score),  # Higher absolute score = higher confidence
    }


def batch_analyze_moods(texts: list) -> list:
    """
    Analyze multiple texts for mood.
    
    Args:
        texts: List of text strings
        
    Returns:
        List of mood analysis results
    """
    return [analyze_text_emotions(text) for text in texts]
