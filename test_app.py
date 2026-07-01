"""
Unit tests for Mood-Based Recommendation System.

Run with: pytest
"""

import pytest
from app import create_app
from database import SessionLocal, init_db
from ml.sentiment import analyze_text_emotions, detect_mood


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config['TESTING'] = True
    
    with app.app_context():
        init_db()
    
    yield app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestSentimentAnalysis:
    """Test sentiment analysis functionality."""
    
    def test_happy_sentiment(self):
        """Test happy mood detection."""
        result = analyze_text_emotions("I'm so happy and excited!")
        assert result['mood'] == 'Happy'
        assert result['sentiment_score'] > 0.5

    def test_sad_sentiment(self):
        """Test sad mood detection."""
        result = analyze_text_emotions("I feel terrible and depressed")
        assert result['mood'] in ('Sad', 'Depressed')
        assert result['sentiment_score'] < -0.1

    def test_neutral_sentiment(self):
        """Test neutral mood detection."""
        result = analyze_text_emotions("This is a regular day")
        assert result['mood'] == 'Neutral'
        assert -0.09 <= result['sentiment_score'] <= 0.09
    
    def test_detect_mood_boundaries(self):
        """Test mood detection boundaries."""
        assert detect_mood(0.7) == 'Happy'
        assert detect_mood(0.3) == 'Joyful'
        assert detect_mood(0.0) == 'Neutral'
        assert detect_mood(-0.3) == 'Sad'
        assert detect_mood(-0.7) == 'Depressed'


class TestAPI:
    """Test API endpoints."""
    
    def test_home_page(self, client):
        """Test home page endpoint."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'How are you feeling' in response.data or b'mood' in response.data
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        assert 'healthy' in response.get_json()['status'].lower()
    
    def test_analyze_endpoint_success(self, client):
        """Test mood analysis endpoint with valid input."""
        response = client.post('/api/analyze',
                             json={'text': 'I feel great today!'},
                             content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'mood' in data
        assert 'sentiment_score' in data
        assert 'songs' in data
        assert 'movies' in data
    
    def test_analyze_endpoint_empty_text(self, client):
        """Test analyze endpoint with empty text."""
        response = client.post('/api/analyze',
                             json={'text': ''},
                             content_type='application/json')
        assert response.status_code == 400
        assert response.get_json()['success'] is False
    
    def test_analyze_endpoint_missing_text(self, client):
        """Test analyze endpoint without text field."""
        response = client.post('/api/analyze',
                             json={},
                             content_type='application/json')
        assert response.status_code == 400
        assert response.get_json()['success'] is False
    
    def test_analyze_endpoint_text_too_long(self, client):
        """Test analyze endpoint with text exceeding limit."""
        long_text = 'a' * 1001
        response = client.post('/api/analyze',
                             json={'text': long_text},
                             content_type='application/json')
        assert response.status_code == 400
        assert response.get_json()['success'] is False
    
    def test_mood_stats_endpoint(self, client):
        """Test mood statistics endpoint."""
        response = client.get('/api/mood-stats')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'stats' in data
        assert 'Happy' in data['stats']


class TestIntegration:
    """Integration tests."""
    
    def test_end_to_end_analysis(self, client):
        """Test complete analysis flow."""
        # Happy case
        response = client.post('/api/analyze',
                             json={'text': 'I just won the lottery!'},
                             content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['mood'] in ['Happy', 'Joyful']
        assert data['sentiment_score'] > 0.1
        assert len(data['songs']) > 0
        assert len(data['movies']) > 0
    
    def test_different_moods_return_different_results(self, client):
        """Test that different moods return different recommendations."""
        # Happy input
        happy_response = client.post('/api/analyze',
                                    json={'text': 'I am so happy!'},
                                    content_type='application/json')
        happy_mood = happy_response.get_json()['mood']
        
        # Sad input
        sad_response = client.post('/api/analyze',
                                  json={'text': 'I am so sad'},
                                  content_type='application/json')
        sad_mood = sad_response.get_json()['mood']
        
        assert happy_mood != sad_mood


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
