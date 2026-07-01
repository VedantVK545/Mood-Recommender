"""
Flask routes for the Mood-Based Recommendation System.

This module defines all REST API endpoints and web routes.
"""

import json
from datetime import datetime, date
from flask import Blueprint, request, jsonify, render_template
from sqlalchemy import func
from ml.sentiment import analyze_text_emotions
from ml import hf_sentiment
from ml.recommender import get_recommendations_for_mood, get_mood_statistics
from database.models import RecommendationHistory

recommendation_bp = Blueprint('recommendation', __name__)


@recommendation_bp.route('/', methods=['GET'])
def index():
    """Render the home page."""
    return render_template('index.html')


@recommendation_bp.route('/api/analyze', methods=['POST'])
def analyze():
    """
    API endpoint for analyzing text and getting recommendations.
    
    Request body:
    {
        "text": "I am so excited today!"
    }
    
    Response:
    {
        "success": true,
        "mood": "Happy",
        "emoji": "😄",
        "sentiment_score": 0.83,
        "description": "Very positive and enthusiastic",
        "songs": [...],
        "movies": [...]
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing "text" field in request'
            }), 400
        
        user_text = data['text'].strip()
        
        if not user_text:
            return jsonify({
                'success': False,
                'error': 'Text cannot be empty'
            }), 400
        
        if len(user_text) > 1000:
            return jsonify({
                'success': False,
                'error': 'Text too long (maximum 1000 characters)'
            }), 400
        
        # Choose sentiment engine (vader or huggingface)
        use_hf = data.get('model') == 'huggingface'
        if use_hf:
            try:
                emotion_analysis = hf_sentiment.analyze_text_emotions_hf(user_text)
            except RuntimeError as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 400
        else:
            emotion_analysis = analyze_text_emotions(user_text)
        mood = emotion_analysis['mood']
        sentiment_score = emotion_analysis['sentiment_score']
        
        # Get recommendations
        from database import get_db
        db = next(get_db())
        
        recommendations = get_recommendations_for_mood(
            db, mood, num_songs=5, num_movies=5
        )
        
        # Save to history if database available
        try:
            history_record = RecommendationHistory(
                user_text=user_text,
                detected_mood=mood,
                sentiment_score=sentiment_score,
                recommended_songs=json.dumps([s['id'] for s in recommendations['songs']]),
                recommended_movies=json.dumps([m['id'] for m in recommendations['movies']])
            )
            db.add(history_record)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Warning: Could not save to history: {e}")
        finally:
            db.close()
        
        # Build response
        response = {
            'success': True,
            'mood': mood,
            'emoji': emotion_analysis['emoji'],
            'sentiment_score': round(sentiment_score, 2),
            'description': emotion_analysis['description'],
            'confidence': round(emotion_analysis['confidence'], 2),
            'sentiment_details': {
                'positive': round(emotion_analysis['sentiment_details']['positive'], 2),
                'negative': round(emotion_analysis['sentiment_details']['negative'], 2),
                'neutral': round(emotion_analysis['sentiment_details']['neutral'], 2),
            },
            'songs': recommendations['songs'],
            'movies': recommendations['movies'],
            'recommendations_count': len(recommendations['songs']) + len(recommendations['movies']),
            'model': emotion_analysis.get('model', 'VADER'),
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@recommendation_bp.route('/api/mood-stats', methods=['GET'])
def mood_stats():
    """
    API endpoint for getting statistics about available recommendations.
    
    Response:
    {
        "success": true,
        "stats": {
            "Happy": {"songs": 5, "movies": 5, "total": 10},
            ...
        }
    }
    """
    try:
        from database import get_db
        db = next(get_db())
        
        stats = get_mood_statistics(db)
        db.close()
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@recommendation_bp.route('/api/mood-history', methods=['GET'])
def mood_history():
    """
    API endpoint for getting mood history data.

    Returns mood analysis history grouped by day for charting.

    Response:
    {
        "success": true,
        "history": [
            {
                "date": "2024-06-26",
                "moods": {"Happy": 3, "Sad": 1},
                "total": 4
            },
            ...
        ]
    }
    """
    try:
        from database import get_db
        db = next(get_db())

        # Query all history entries, last 30 days, ordered by date
        history = (
            db.query(
                func.date(RecommendationHistory.created_at).label('date'),
                RecommendationHistory.detected_mood,
                func.count(RecommendationHistory.id).label('count'),
            )
            .group_by(func.date(RecommendationHistory.created_at), RecommendationHistory.detected_mood)
            .order_by(func.date(RecommendationHistory.created_at).desc())
            .limit(90)  # 30 days max × 3 moods per day max
            .all()
        )

        # Group by date
        from collections import defaultdict
        daily = defaultdict(dict)
        for row in history:
            daily[str(row.date)][row.detected_mood] = row.count

        result = [
            {'date': d, 'moods': moods, 'total': sum(moods.values())}
            for d, moods in sorted(daily.items(), reverse=True)[:30]
        ]

        db.close()

        return jsonify({'success': True, 'history': result}), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@recommendation_bp.route('/api/health', methods=['GET'])
def health():
    """
    Health check endpoint.

    Response:
    {
        "status": "healthy",
        "timestamp": "2024-06-26T10:30:00Z"
    }
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 200


@recommendation_bp.route('/api/trailer/<int:movie_id>', methods=['GET'])
def get_trailer(movie_id):
    """
    API endpoint for getting a movie trailer URL.

    Searches YouTube for the trailer, caches it in the database for
    future requests, and returns the URL.

    Response:
    {
        "success": true,
        "trailer_url": "https://www.youtube.com/watch?v=xxxxx"
    }
    """
    try:
        from database import get_db
        from database.models import Movie
        from utils.youtube import search_trailer

        db = next(get_db())
        movie = db.query(Movie).filter(Movie.id == movie_id).first()

        if not movie:
            db.close()
            return jsonify({'success': False, 'error': 'Movie not found'}), 404

        # If we already have a cached trailer URL, return it
        if movie.trailer_url:
            db.close()
            return jsonify({'success': True, 'trailer_url': movie.trailer_url}), 200

        # Search YouTube for the trailer
        trailer_url = search_trailer(movie.title)

        # Cache it in the database
        movie.trailer_url = trailer_url
        db.commit()
        db.close()

        return jsonify({'success': True, 'trailer_url': trailer_url}), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@recommendation_bp.route('/api/example', methods=['GET'])
def example():
    """
    Get example recommendation data (for frontend testing).
    
    Response:
    {
        "success": true,
        "example_text": "I finally got my dream job!",
        "example_result": {...}
    }
    """
    from database import get_db
    db = next(get_db())
    
    example_text = "I finally got my dream job today!"
    emotion_analysis = analyze_text_emotions(example_text)
    mood = emotion_analysis['mood']
    
    recommendations = get_recommendations_for_mood(db, mood)
    db.close()
    
    return jsonify({
        'success': True,
        'example_text': example_text,
        'example_result': {
            'mood': mood,
            'emoji': emotion_analysis['emoji'],
            'sentiment_score': round(emotion_analysis['sentiment_score'], 2),
            'songs': recommendations['songs'][:3],
            'movies': recommendations['movies'][:3],
        }
    }), 200
