"""
Database initialization and session management.

This module handles database connection, session creation, and
initialization of database tables.
"""

import os
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from .models import Base, Song, Movie

# Database URL configuration
DATABASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(DATABASE_DIR, 'database.db')
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create engine with optimized SQLite settings
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
    pool_pre_ping=True,
)

# SQLite optimizations
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign keys and WAL mode for SQLite."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    This function creates all tables defined in the ORM models.
    Safe to call multiple times (idempotent).
    """
    Base.metadata.create_all(bind=engine)
    print("[OK] Database initialized successfully")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session in Flask routes.
    
    Yields:
        SQLAlchemy Session object for database operations
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_initial_data() -> None:
    """
    Seed database with initial songs and movies data.
    
    This function populates the database with sample data for all mood categories.
    Only adds data if tables are empty to avoid duplicates.
    """
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Song).count() > 0:
            print("[OK] Database already seeded")
            return
        
        # SONGS DATA (50 songs — 10 per mood)
        songs_data = [
            # ── Happy ──
            Song(title="Happy", artist="Pharrell Williams", mood="Happy", genre="Pop",
                 spotify_link="https://open.spotify.com/track/6NPVjNh8Jhru9xOmyQigds"),
            Song(title="Don't Stop Me Now", artist="Queen", mood="Happy", genre="Rock",
                 spotify_link="https://open.spotify.com/track/43DHLzDkncpby82Po5jlOZ"),
            Song(title="Walking on Sunshine", artist="Katrina & The Waves", mood="Happy", genre="Pop",
                 spotify_link="https://open.spotify.com/track/05wIrZSwuaVWhcv5FfqeH0"),
            Song(title="Good as Hell", artist="Lizzo", mood="Happy", genre="Pop",
                 spotify_link="https://open.spotify.com/track/043CB5VqGkGOXOCndP650N"),
            Song(title="Uptown Funk", artist="Mark Ronson ft. Bruno Mars", mood="Happy", genre="Pop",
                 spotify_link="https://open.spotify.com/track/32OlwWuMpZ6b0aN2RZOeMS"),
            Song(title="Here Comes the Sun", artist="The Beatles", mood="Happy", genre="Rock",
                 spotify_link="https://open.spotify.com/track/3CPFHaVEHkkH26hAEPgMMp"),
            Song(title="Dancing Queen", artist="ABBA", mood="Happy", genre="Pop",
                 spotify_link="https://open.spotify.com/track/0GjEhVFGZW8afUYGChu3Rr"),
            Song(title="Shake It Off", artist="Taylor Swift", mood="Happy", genre="Pop",
                 spotify_link="https://open.spotify.com/track/3fthfkkvy9av3q3uAGVf7U"),
            Song(title="I Wanna Dance with Somebody", artist="Whitney Houston", mood="Happy", genre="Pop",
                 spotify_link="https://open.spotify.com/track/6VpQ0Ot9ZbXCFq4I3MWlI0"),
            Song(title="September", artist="Earth, Wind & Fire", mood="Happy", genre="Funk",
                 spotify_link="https://open.spotify.com/track/2grjqo0Frpf2okIBiifQKs"),

            # ── Joyful ──
            Song(title="Good Life", artist="Kanye West", mood="Joyful", genre="Hip-Hop",
                 spotify_link="https://open.spotify.com/track/0sDPkDKvPNvuRxOBIaiqCc"),
            Song(title="I Gotta Feeling", artist="Black Eyed Peas", mood="Joyful", genre="Pop",
                 spotify_link="https://open.spotify.com/track/4vp2J1l5RD4gMZwGFLfRAu"),
            Song(title="Soak Up the Sun", artist="Sheryl Crow", mood="Joyful", genre="Rock",
                 spotify_link="https://open.spotify.com/track/0I42sAzTAeO8LlrKoin7Sf"),
            Song(title="Levitating", artist="Dua Lipa", mood="Joyful", genre="Pop",
                 spotify_link="https://open.spotify.com/track/41z2bSbbtJ9wiIee4RXdi5"),
            Song(title="Can't Stop the Feeling!", artist="Justin Timberlake", mood="Joyful", genre="Pop",
                 spotify_link="https://open.spotify.com/track/6JV2JOEocMgcZxYSZelKcc"),
            Song(title="Sunflower", artist="Post Malone & Swae Lee", mood="Joyful", genre="Pop",
                 spotify_link="https://open.spotify.com/track/0RiRZpuVRbi7oqRdSMwhQY"),
            Song(title="Feel It Still", artist="Portugal. The Man", mood="Joyful", genre="Rock",
                 spotify_link="https://open.spotify.com/track/6QgjcU0zLnzq5OrUoSZ3OK"),
            Song(title="Treasure", artist="Bruno Mars", mood="Joyful", genre="Pop",
                 spotify_link="https://open.spotify.com/track/55h7vJchibLdUkxdlX3fK7"),
            Song(title="Brown Eyed Girl", artist="Van Morrison", mood="Joyful", genre="Rock",
                 spotify_link="https://open.spotify.com/track/3yrSvpt2l1xhsV9Em88Pul"),
            Song(title="Hey Ya!", artist="OutKast", mood="Joyful", genre="Hip-Hop",
                 spotify_link="https://open.spotify.com/track/5kg4LVSduhdPPXwEBXfw1c"),

            # ── Neutral ──
            Song(title="Wonderwall", artist="Oasis", mood="Neutral", genre="Rock",
                 spotify_link="https://open.spotify.com/track/1qPbGZqppFwLwcBC1JQ6Vr"),
            Song(title="Somebody That I Used to Know", artist="Gotye", mood="Neutral", genre="Pop",
                 spotify_link="https://open.spotify.com/track/4wCmqSrbyCgxEXROQE6vtV"),
            Song(title="Blinding Lights", artist="The Weeknd", mood="Neutral", genre="Pop",
                 spotify_link="https://open.spotify.com/track/5Sg09MvHqNWPWsYeuY2toY"),
            Song(title="Bad Guy", artist="Billie Eilish", mood="Neutral", genre="Pop",
                 spotify_link="https://open.spotify.com/track/2Fxmhks0bxGSBdJ92vM42m"),
            Song(title="Creep", artist="Radiohead", mood="Neutral", genre="Rock",
                 spotify_link="https://open.spotify.com/track/70LcF31zb1H0PyJoS1Sx1r"),
            Song(title="Boulevard of Broken Dreams", artist="Green Day", mood="Neutral", genre="Rock",
                 spotify_link="https://open.spotify.com/track/0U87auHx1iZTEFcq9KVdmO"),
            Song(title="Drive", artist="Incubus", mood="Neutral", genre="Rock",
                 spotify_link="https://open.spotify.com/track/7nnWIPM5hwE3DaUBkvOIpy"),
            Song(title="Under the Bridge", artist="Red Hot Chili Peppers", mood="Neutral", genre="Rock",
                 spotify_link="https://open.spotify.com/track/5PclxRY6shIQzSKxxbdZso"),
            Song(title="Mr. Brightside", artist="The Killers", mood="Neutral", genre="Rock",
                 spotify_link="https://open.spotify.com/track/7oK9VyNzrYvRFo7nQEYkWN"),
            Song(title="Lose Yourself", artist="Eminem", mood="Neutral", genre="Hip-Hop",
                 spotify_link="https://open.spotify.com/track/1MWlCmgxuLIe4izcR62xBE"),

            # ── Sad ──
            Song(title="Someone Like You", artist="Adele", mood="Sad", genre="Pop",
                 spotify_link="https://open.spotify.com/track/3bNv3VuUOKgrf5hu3YcuRo"),
            Song(title="The Scientist", artist="Coldplay", mood="Sad", genre="Rock",
                 spotify_link="https://open.spotify.com/track/75JFxkI2RXiU7L9VXzMkle"),
            Song(title="Hurt", artist="Johnny Cash", mood="Sad", genre="Country",
                 spotify_link="https://open.spotify.com/track/1jHhOrH4kIhjLFvagzvw1s"),
            Song(title="Black", artist="Pearl Jam", mood="Sad", genre="Rock",
                 spotify_link="https://open.spotify.com/track/5Xak5fmy089t0FYmh3VJiY"),
            Song(title="Yesterday", artist="The Beatles", mood="Sad", genre="Rock",
                 spotify_link="https://open.spotify.com/track/3BQHpFgAp4l80e1XslIjNI"),
            Song(title="Fix You", artist="Coldplay", mood="Sad", genre="Rock",
                 spotify_link="https://open.spotify.com/track/7LVHVU3tWfcxj5aiPFEW4Q"),
            Song(title="Nothing Compares 2 U", artist="Sinéad O'Connor", mood="Sad", genre="Pop",
                 spotify_link="https://open.spotify.com/track/3nvuPQTw2zuFAVuLsC9IYQ"),
            Song(title="Everybody Hurts", artist="R.E.M.", mood="Sad", genre="Rock",
                 spotify_link="https://open.spotify.com/track/6PypGyiu0Y2lCDBN1XZEnP"),
            Song(title="Skinny Love", artist="Bon Iver", mood="Sad", genre="Indie",
                 spotify_link="https://open.spotify.com/track/2cbic3TiUENlJX91y67ARR"),
            Song(title="Let Her Go", artist="Passenger", mood="Sad", genre="Folk",
                 spotify_link="https://open.spotify.com/track/3iG1kMTtO2udMRMzV4DqJO"),

            # ── Depressed ──
            Song(title="Hurt", artist="Nine Inch Nails", mood="Depressed", genre="Industrial",
                 spotify_link="https://open.spotify.com/track/27tX58NOpv1YKQ0abW7EPy"),
            Song(title="Hallelujah", artist="Leonard Cohen", mood="Depressed", genre="Folk",
                 spotify_link="https://open.spotify.com/track/7yzbimr8WVyAtBX3Eg6UL9"),
            Song(title="Mad World", artist="Gary Jules", mood="Depressed", genre="Alternative",
                 spotify_link="https://open.spotify.com/track/0LuVpXVTaWY9Un2w9GkXjf"),
            Song(title="Tears in Heaven", artist="Eric Clapton", mood="Depressed", genre="Rock",
                 spotify_link="https://open.spotify.com/track/1kgdslQYmeTR4thk9whoRw"),
            Song(title="No Surprises", artist="Radiohead", mood="Depressed", genre="Rock",
                 spotify_link="https://open.spotify.com/track/10nyNJ6zNy2YVYLrcwLccB"),
            Song(title="The Sound of Silence", artist="Simon & Garfunkel", mood="Depressed", genre="Folk",
                 spotify_link="https://open.spotify.com/track/3YfS47QufnLDFA71FUsgCM"),
            Song(title="My Immortal", artist="Evanescence", mood="Depressed", genre="Rock",
                 spotify_link="https://open.spotify.com/track/4UzVcXufOhGUwF56HT7b8M"),
            Song(title="Numb", artist="Linkin Park", mood="Depressed", genre="Rock",
                 spotify_link="https://open.spotify.com/track/2nLtzopw4rPReszdYBJU6h"),
            Song(title="How to Save a Life", artist="The Fray", mood="Depressed", genre="Rock",
                 spotify_link="https://open.spotify.com/track/5fVZC9GiM4e8vu99W0Xf6J"),
            Song(title="Fade to Black", artist="Metallica", mood="Depressed", genre="Metal",
                 spotify_link="https://open.spotify.com/track/0dqGfCMAGyDgpUAgLNOjWd"),
        ]
        
        # MOVIES DATA (50 movies — 10 per mood)
        TMDB_POSTER = "https://image.tmdb.org/t/p/w500"
        movies_data = [
            # ── Happy ──
            Movie(title="The Pursuit of Happyness", genre="Drama", mood="Happy", imdb_rating=8.0,
                  poster_url=f"{TMDB_POSTER}/lBYOKAMcxIvuk9s9hMuecB9dPBV.jpg"),
            Movie(title="Forrest Gump", genre="Drama", mood="Happy", imdb_rating=8.8,
                  poster_url=f"{TMDB_POSTER}/Cw4hIUIAmSYfK9QfaUW5igp9La.jpg"),
            Movie(title="Life is Beautiful", genre="Drama", mood="Happy", imdb_rating=8.6,
                  poster_url=f"{TMDB_POSTER}/nrmXQ0zcZUL8jFLrakWc90IR8z9.jpg"),
            Movie(title="Amélie", genre="Comedy", mood="Happy", imdb_rating=8.3,
                  poster_url=f"{TMDB_POSTER}/2CAL2433ZeIihfX1Hb2139CX0pW.jpg"),
            Movie(title="The Grand Budapest Hotel", genre="Comedy", mood="Happy", imdb_rating=8.1,
                  poster_url=f"{TMDB_POSTER}/rHUg2AuIuLSIYMYFgavVwqt1jtc.jpg"),
            Movie(title="La La Land", genre="Musical", mood="Happy", imdb_rating=8.0,
                  poster_url=f"{TMDB_POSTER}/uDO8zWDhfWwoFdKS4fzkUJt0Rf0.jpg"),
            Movie(title="Singin' in the Rain", genre="Musical", mood="Happy", imdb_rating=8.3,
                  poster_url=f"{TMDB_POSTER}/w03EiJVHP8Un77boQeE7hg9DVdU.jpg"),
            Movie(title="The Sound of Music", genre="Musical", mood="Happy", imdb_rating=8.1,
                  poster_url=f"{TMDB_POSTER}/c6CrUZypAsBCaRWX0M3RVRDbhNS.jpg"),
            Movie(title="Toy Story", genre="Animation", mood="Happy", imdb_rating=8.3,
                  poster_url=f"{TMDB_POSTER}/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg"),
            Movie(title="Soul", genre="Animation", mood="Happy", imdb_rating=8.0,
                  poster_url=f"{TMDB_POSTER}/6jmppcaubzLF8wkXM36ganVISCo.jpg"),

            # ── Joyful ──
            Movie(title="Coco", genre="Animation", mood="Joyful", imdb_rating=8.4,
                  poster_url=f"{TMDB_POSTER}/6Ryitt95xrO8KXuqRGm1fUuNwqF.jpg"),
            Movie(title="Inside Out", genre="Animation", mood="Joyful", imdb_rating=8.2,
                  poster_url=f"{TMDB_POSTER}/2H1TmgdfNtsKlU9jKdeNyYL5y8T.jpg"),
            Movie(title="The Intouchables", genre="Drama", mood="Joyful", imdb_rating=8.5,
                  poster_url=f"{TMDB_POSTER}/nSxDa3M9aMvGVLoItzWTepQ5h5d.jpg"),
            Movie(title="Paddington", genre="Comedy", mood="Joyful", imdb_rating=7.8,
                  poster_url=f"{TMDB_POSTER}/iAo1hlzsPV9XpYcLQp6Ud065tGO.jpg"),
            Movie(title="The Lion King", genre="Animation", mood="Joyful", imdb_rating=8.5,
                  poster_url=f"{TMDB_POSTER}/sKCr78MXSLixwmZ8DyJLrpMsd15.jpg"),
            Movie(title="Moana", genre="Animation", mood="Joyful", imdb_rating=7.6,
                  poster_url=f"{TMDB_POSTER}/9tzN8sPbyod2dsa0lwuvrwBDWra.jpg"),
            Movie(title="Zootopia", genre="Animation", mood="Joyful", imdb_rating=8.0,
                  poster_url=f"{TMDB_POSTER}/hlK0e0wAQ3VLuJcsfIYPvb4JVud.jpg"),
            Movie(title="The Secret Life of Pets", genre="Animation", mood="Joyful", imdb_rating=6.5,
                  poster_url=f"{TMDB_POSTER}/g3Hms6AE174doeGR1gz5zX5sVsv.jpg"),
            Movie(title="Mamma Mia!", genre="Musical", mood="Joyful", imdb_rating=6.4,
                  poster_url=f"{TMDB_POSTER}/zdUA4FNHbXPadzVOJiU0Rgn6cHR.jpg"),
            Movie(title="Ferris Bueller's Day Off", genre="Comedy", mood="Joyful", imdb_rating=7.8,
                  poster_url=f"{TMDB_POSTER}/9LTQNCvoLsKXP0LtaKAaYVtRaQL.jpg"),

            # ── Neutral ──
            Movie(title="Inception", genre="Sci-Fi", mood="Neutral", imdb_rating=8.8,
                  poster_url=f"{TMDB_POSTER}/xlaY2zyzMfkhk0HSC5VUwzoZPU1.jpg"),
            Movie(title="The Shawshank Redemption", genre="Drama", mood="Neutral", imdb_rating=9.3,
                  poster_url=f"{TMDB_POSTER}/9cqNxx0GxF0bflZmeSMuL5tnGzr.jpg"),
            Movie(title="Pulp Fiction", genre="Crime", mood="Neutral", imdb_rating=8.9,
                  poster_url=f"{TMDB_POSTER}/vQWk5YBFWF4bZaofAbv0tShwBvQ.jpg"),
            Movie(title="The Matrix", genre="Sci-Fi", mood="Neutral", imdb_rating=8.7,
                  poster_url=f"{TMDB_POSTER}/dXNAPwY7VrqMAo51EKhhCJfaGb5.jpg"),
            Movie(title="Interstellar", genre="Sci-Fi", mood="Neutral", imdb_rating=8.6,
                  poster_url=f"{TMDB_POSTER}/yQvGrMoipbRoddT0ZR8tPoR7NfX.jpg"),
            Movie(title="The Godfather", genre="Crime", mood="Neutral", imdb_rating=9.2,
                  poster_url=f"{TMDB_POSTER}/wWJbBo5yjw22AIjE8isBFoiBI3S.jpg"),
            Movie(title="The Dark Knight", genre="Action", mood="Neutral", imdb_rating=9.0,
                  poster_url=f"{TMDB_POSTER}/qJ2tW6WMUDux911r6m7haRef0WH.jpg"),
            Movie(title="Gone Girl", genre="Thriller", mood="Neutral", imdb_rating=8.1,
                  poster_url=f"{TMDB_POSTER}/ts996lKsxvjkO2yiYG0ht4qAicO.jpg"),
            Movie(title="Blade Runner 2049", genre="Sci-Fi", mood="Neutral", imdb_rating=8.0,
                  poster_url=f"{TMDB_POSTER}/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg"),
            Movie(title="Se7en", genre="Crime", mood="Neutral", imdb_rating=8.6,
                  poster_url=f"{TMDB_POSTER}/191nKfP0ehp3uIvWqgPbFmI4lv9.jpg"),

            # ── Sad ──
            Movie(title="A Star is Born", genre="Drama", mood="Sad", imdb_rating=7.6,
                  poster_url=f"{TMDB_POSTER}/wrFpXMNBRj2PBiN4Z5kix51XaIZ.jpg"),
            Movie(title="Requiem for a Dream", genre="Drama", mood="Sad", imdb_rating=8.4,
                  poster_url=f"{TMDB_POSTER}/9BTwsLaMVHOGFlmsSlx5QYCaXb.jpg"),
            Movie(title="Grave of the Fireflies", genre="Animation", mood="Sad", imdb_rating=8.5,
                  poster_url=f"{TMDB_POSTER}/eyH8SHApg7T37c0nCvub9YOWhRL.jpg"),
            Movie(title="Dancer in the Dark", genre="Drama", mood="Sad", imdb_rating=8.0,
                  poster_url=f"{TMDB_POSTER}/or1gBugydmjToAEq7OZY0owwFk.jpg"),
            Movie(title="Manchester by the Sea", genre="Drama", mood="Sad", imdb_rating=8.0,
                  poster_url=f"{TMDB_POSTER}/bajajkoErDst0JxdFyBkABiF9rW.jpg"),
            Movie(title="Eternal Sunshine of the Spotless Mind", genre="Romance", mood="Sad", imdb_rating=8.3,
                  poster_url=f"{TMDB_POSTER}/5MwkWH9tYHv3mV9OdYTMR5qreIz.jpg"),
            Movie(title="Brokeback Mountain", genre="Drama", mood="Sad", imdb_rating=7.7,
                  poster_url=f"{TMDB_POSTER}/3qnO72NHmUgs9JZXAmu4aId9QDl.jpg"),
            Movie(title="The Green Mile", genre="Drama", mood="Sad", imdb_rating=8.6,
                  poster_url=f"{TMDB_POSTER}/8VG8fDNiy50H4FedGwdSVUPoaJe.jpg"),
            Movie(title="Her", genre="Romance", mood="Sad", imdb_rating=8.0,
                  poster_url=f"{TMDB_POSTER}/eCOtqtfvn7mxGl6nfmq4b1exJRc.jpg"),
            Movie(title="The Shawshank Redemption", genre="Drama", mood="Sad", imdb_rating=9.3,
                  poster_url=f"{TMDB_POSTER}/9cqNxx0GxF0bflZmeSMuL5tnGzr.jpg"),

            # ── Depressed ──
            Movie(title="Nocturnal Animals", genre="Drama", mood="Depressed", imdb_rating=7.5,
                  poster_url=f"{TMDB_POSTER}/mdLDgQBD0va09npSQX5Zgo2evXM.jpg"),
            Movie(title="The Road", genre="Drama", mood="Depressed", imdb_rating=7.2,
                  poster_url=f"{TMDB_POSTER}/tFZQAuulEOtFTp0gHbVdEXwGrYe.jpg"),
            Movie(title="Synecdoche, New York", genre="Drama", mood="Depressed", imdb_rating=7.5,
                  poster_url=f"{TMDB_POSTER}/vuza0WqY239yBXOadKlGwJsZJFE.jpg"),
            Movie(title="A Ghost Story", genre="Drama", mood="Depressed", imdb_rating=7.3,
                  poster_url=f"{TMDB_POSTER}/rp5JPIyZi9sMob15l46zNQLe5cO.jpg"),
            Movie(title="Come and See", genre="War", mood="Depressed", imdb_rating=8.3,
                  poster_url=f"{TMDB_POSTER}/9IiSgiq4h4siTIS9H3o4nZ3h5L9.jpg"),
            Movie(title="Melancholia", genre="Drama", mood="Depressed", imdb_rating=7.1,
                  poster_url=f"{TMDB_POSTER}/fMneszMiQuTKY8JUXrGGB5vwqJf.jpg"),
            Movie(title="Schindler's List", genre="Drama", mood="Depressed", imdb_rating=9.0,
                  poster_url=f"{TMDB_POSTER}/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg"),
            Movie(title="The Pianist", genre="Drama", mood="Depressed", imdb_rating=8.5,
                  poster_url=f"{TMDB_POSTER}/2hFvxCCWrTmCYwfy7yum0GKRi3Y.jpg"),
            Movie(title="We Need to Talk About Kevin", genre="Thriller", mood="Depressed", imdb_rating=7.5,
                  poster_url=f"{TMDB_POSTER}/yKXRwMValA4ZbCaC68ANO24ALcY.jpg"),
            Movie(title="Black Swan", genre="Thriller", mood="Depressed", imdb_rating=8.0,
                  poster_url=f"{TMDB_POSTER}/viWheBd44bouiLCHgNMvahLThqx.jpg"),
        ]
        
        # Add all data to session
        db.add_all(songs_data)
        db.add_all(movies_data)
        db.commit()
        
        print(f"[OK] Database seeded with {len(songs_data)} songs and {len(movies_data)} movies")
        
    except Exception as e:
        db.rollback()
        print(f"[ERR] Error seeding database: {e}")
    finally:
        db.close()
