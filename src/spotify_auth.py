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
    redirect_uri = "http://localhost:8888/callback"
    
    # Define the scopes (permissions) your app needs
    scope = "user-library-read playlist-read-private playlist-modify-private playlist-modify-public"
    
    # Create the Spotify OAuth client
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope
    )
    
    # Create and return the Spotify client
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify

if __name__ == "__main__":
    # Test the authentication
    spotify = get_spotify_client()
    results = spotify.current_user()
    print(f"Authenticated as: {results['display_name']}")