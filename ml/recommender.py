"""
Recommendation engine for music and movies based on detected mood.

This module provides functions to fetch and recommend songs and movies
matching the user's detected mood from the database.
"""

import random
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from database.models import Song, Movie


class RecommendationEngine:
    """
    Engine for generating music and movie recommendations based on mood.
    """
    
    def __init__(self, db_session: Session, num_songs: int = 5, num_movies: int = 5):
        """
        Initialize the recommendation engine.
        
        Args:
            db_session: SQLAlchemy database session
            num_songs: Number of songs to recommend
            num_movies: Number of movies to recommend
        """
        self.db = db_session
        self.num_songs = num_songs
        self.num_movies = num_movies
    
    def get_songs_by_mood(self, mood: str) -> List[Song]:
        """
        Fetch all songs matching the specified mood from database.
        
        Args:
            mood: Mood category
            
        Returns:
            List of Song objects
        """
        return self.db.query(Song).filter(Song.mood == mood).all()
    
    def get_movies_by_mood(self, mood: str) -> List[Movie]:
        """
        Fetch all movies matching the specified mood from database.
        
        Args:
            mood: Mood category
            
        Returns:
            List of Movie objects
        """
        return self.db.query(Movie).filter(Movie.mood == mood).all()
    
    def recommend_songs(self, mood: str) -> List[Dict]:
        """
        Recommend songs based on mood.
        
        Fetches all songs matching the mood and returns random selection.
        
        Args:
            mood: Detected mood category
            
        Returns:
            List of recommended song dictionaries
        """
        songs = self.get_songs_by_mood(mood)
        
        if not songs:
            return []
        
        # Select random songs (up to num_songs)
        recommended = random.sample(songs, min(self.num_songs, len(songs)))
        
        return [
            {
                'id': song.id,
                'title': song.title,
                'artist': song.artist,
                'mood': song.mood,
                'genre': song.genre,
                'spotify_link': song.spotify_link,
            }
            for song in recommended
        ]
    
    def recommend_movies(self, mood: str) -> List[Dict]:
        """
        Recommend movies based on mood.
        
        Fetches all movies matching the mood and returns random selection.
        
        Args:
            mood: Detected mood category
            
        Returns:
            List of recommended movie dictionaries
        """
        movies = self.get_movies_by_mood(mood)
        
        if not movies:
            return []
        
        # Select random movies (up to num_movies)
        recommended = random.sample(movies, min(self.num_movies, len(movies)))
        
        return [
            {
                'id': movie.id,
                'title': movie.title,
                'genre': movie.genre,
                'mood': movie.mood,
                'imdb_rating': movie.imdb_rating,
                'poster_url': movie.poster_url,
                'trailer_url': movie.trailer_url,
            }
            for movie in recommended
        ]
    
    def get_recommendations(self, mood: str) -> Dict:
        """
        Get complete recommendations (songs and movies) for a mood.
        
        Args:
            mood: Detected mood category
            
        Returns:
            Dictionary containing songs and movies recommendations
        """
        songs = self.recommend_songs(mood)
        movies = self.recommend_movies(mood)
        
        return {
            'mood': mood,
            'songs': songs,
            'movies': movies,
            'songs_count': len(songs),
            'movies_count': len(movies),
        }


def get_recommendations_for_mood(db: Session, mood: str, 
                                num_songs: int = 5, 
                                num_movies: int = 5) -> Dict:
    """
    Convenience function to get recommendations for a mood.
    
    Args:
        db: Database session
        mood: Detected mood category
        num_songs: Number of songs to recommend
        num_movies: Number of movies to recommend
        
    Returns:
        Dictionary with recommendations
    """
    engine = RecommendationEngine(db, num_songs, num_movies)
    return engine.get_recommendations(mood)


def get_recommendations_by_text(db: Session, mood: str, 
                               text: str = "",
                               num_songs: int = 5, 
                               num_movies: int = 5) -> Dict:
    """
    Get recommendations with metadata about the input.
    
    Args:
        db: Database session
        mood: Detected mood category
        text: Original user input text
        num_songs: Number of songs to recommend
        num_movies: Number of movies to recommend
        
    Returns:
        Dictionary with recommendations and metadata
    """
    engine = RecommendationEngine(db, num_songs, num_movies)
    recommendations = engine.get_recommendations(mood)
    
    return {
        'input_text': text,
        'mood': mood,
        'songs': recommendations['songs'],
        'movies': recommendations['movies'],
        'recommendations_count': len(recommendations['songs']) + len(recommendations['movies']),
    }


def get_mood_statistics(db: Session) -> Dict:
    """
    Get statistics about available recommendations per mood.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with song and movie counts per mood
    """
    moods = ['Happy', 'Joyful', 'Neutral', 'Sad', 'Depressed']
    stats = {}
    
    for mood in moods:
        song_count = db.query(Song).filter(Song.mood == mood).count()
        movie_count = db.query(Movie).filter(Movie.mood == mood).count()
        stats[mood] = {
            'songs': song_count,
            'movies': movie_count,
            'total': song_count + movie_count,
        }
    
    return stats
