"""
YouTube utility for fetching movie trailer links.

Searches YouTube and returns the first video URL for a movie trailer.
Falls back to a search URL if the fetch fails.
"""

import re
import urllib.request
import urllib.parse


def search_trailer(movie_title: str) -> str:
    """
    Search YouTube for a movie's official trailer.

    Makes a lightweight request to YouTube search and extracts the first
    video ID from the results. Returns the direct YouTube watch URL.

    Args:
        movie_title: Title of the movie

    Returns:
        YouTube video URL, or a search URL as fallback
    """
    query = urllib.parse.quote(f"{movie_title} official movie trailer")
    search_url = f"https://www.youtube.com/results?search_query={query}"

    try:
        req = urllib.request.Request(
            search_url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            html = response.read().decode("utf-8", errors="replace")

        # Extract first video ID from the page
        # YouTube embeds video IDs in watch URLs in the initial data
        match = re.search(r'/watch\?v=([a-zA-Z0-9_-]{11})', html)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/watch?v={video_id}"

    except Exception:
        pass

    # Fallback: return a YouTube search results page
    return search_url
