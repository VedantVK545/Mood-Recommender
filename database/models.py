"""
Database models for the Mood-Based Recommendation System.

This module defines SQLAlchemy ORM models for storing songs, movies,
and recommendation history with mood-based categorization.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()


class Song(Base):
    """
    Song model for storing music recommendations.

    Attributes:
        id: Primary key
        title: Song title
        artist: Artist name
        mood: Associated mood category
        genre: Music genre
        spotify_link: Link to Spotify (optional, for Phase 2)
    """

    __tablename__ = 'songs'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    artist = Column(String(255), nullable=False)
    mood = Column(String(50), nullable=False, index=True)
    genre = Column(String(100), nullable=True)
    spotify_link = Column(String(500), nullable=True)

    __table_args__ = (
        Index('idx_song_mood', 'mood'),
        Index('idx_song_artist', 'artist'),
    )

    def __repr__(self) -> str:
        return f"<Song(id={self.id}, title='{self.title}', artist='{self.artist}', mood='{self.mood}')>"


class Movie(Base):
    """
    Movie model for storing movie recommendations.

    Attributes:
        id: Primary key
        title: Movie title
        genre: Movie genre
        mood: Associated mood category
        imdb_rating: IMDb rating (0-10)
        poster_url: URL to movie poster
        trailer_url: URL to YouTube trailer
    """

    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    genre = Column(String(100), nullable=False)
    mood = Column(String(50), nullable=False, index=True)
    imdb_rating = Column(Float, nullable=True)
    poster_url = Column(String(500), nullable=True)
    trailer_url = Column(String(500), nullable=True)

    __table_args__ = (
        Index('idx_movie_mood', 'mood'),
        Index('idx_movie_title', 'title'),
    )

    def __repr__(self) -> str:
        return f"<Movie(id={self.id}, title='{self.title}', mood='{self.mood}', rating={self.imdb_rating})>"


class RecommendationHistory(Base):
    """
    Recommendation history model for tracking user interactions (Phase 2 feature).

    Attributes:
        id: Primary key
        user_text: Original user input text
        detected_mood: The mood detected from the text
        sentiment_score: Compound sentiment score
        recommended_songs: JSON string of recommended songs IDs
        recommended_movies: JSON string of recommended movies IDs
        created_at: Timestamp of recommendation
    """

    __tablename__ = 'recommendation_history'

    id = Column(Integer, primary_key=True, index=True)
    user_text = Column(String(1000), nullable=False)
    detected_mood = Column(String(50), nullable=False, index=True)
    sentiment_score = Column(Float, nullable=False)
    recommended_songs = Column(String(500), nullable=True)  # JSON string of IDs
    recommended_movies = Column(String(500), nullable=True)  # JSON string of IDs
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_history_mood', 'detected_mood'),
        Index('idx_history_created', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<RecommendationHistory(id={self.id}, mood='{self.detected_mood}', score={self.sentiment_score})>"
