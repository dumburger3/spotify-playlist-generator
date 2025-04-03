import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_spotify_client():
    """
    Creates and returns an authenticated Spotify client
    with the necessary permissions.
    """
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = "http://127.0.0.1:9090/callback"

    scope = "user-library-read user-read-private user-top-read playlist-read-private playlist-modify-private playlist-modify-public"

    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        open_browser=False,
        show_dialog=True,
        cache_path=".cache"
    )

    spotify = spotipy.Spotify(auth_manager=auth_manager)

    # Print token for debug
    try:
        token_info = auth_manager.get_cached_token()
        if token_info:
            print("Access token acquired successfully.")
        else:
            print("No valid token found.")
    except Exception as e:
        print(f"Failed to acquire access token: {str(e)}")

    return spotify

if __name__ == "__main__":
    spotify = get_spotify_client()
    try:
        results = spotify.current_user()
        print(f"Authenticated as: {results['display_name']}")
    except Exception as e:
        print(f"Failed to fetch current user: {str(e)}")