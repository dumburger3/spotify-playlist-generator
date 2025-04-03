import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import time
import pandas as pd

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

    try:
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        user = spotify.current_user()
        print(f"Authenticated as: {user['display_name']}")
        return spotify
    except Exception as e:
        print(f"Failed to authenticate: {str(e)}")
        return None

def get_audio_features(spotify, track_ids):
    """Get audio features for a list of tracks using patched logic"""
    empty_df = pd.DataFrame(columns=['id', 'danceability', 'energy', 'key',
                                     'loudness', 'mode', 'speechiness',
                                     'acousticness', 'instrumentalness',
                                     'liveness', 'valence', 'tempo'])

    if not track_ids:
        return empty_df

    features_data = []
    for i in range(0, len(track_ids), 20):  # safer batching
        batch = [tid for tid in track_ids[i:i+20] if tid]  # skip None/empty
        try:
            ids = ",".join(batch)
            response = spotify._get(f"audio-features?ids={ids}")
            features = response.get('audio_features', [])
            for feature in features:
                if feature:
                    features_data.append(feature)
            time.sleep(0.5)
        except Exception as e:
            print(f"Error processing batch {i//20 + 1}: {str(e)}")
            continue

    if features_data:
        features_df = pd.DataFrame(features_data)
        return features_df[['id', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
                            'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']]
    return empty_df

def test_raw_audio_features(spotify):
    print("\n🔍 TESTING RAW AUDIO FEATURE FETCH")
    headers = spotify._auth_headers()
    print("Authorization Header:", headers)

    test_id = "4uLU6hMCjMI75M1A2tKUQC"  # Lose Yourself
    try:
        url = f"https://api.spotify.com/v1/audio-features?ids={test_id}"
        response = spotify._session.get(url, headers=headers)
        print("Raw status code:", response.status_code)
        print("Raw response:", response.text)
    except Exception as e:
        print("Error making raw request:", str(e))

if __name__ == "__main__":
    spotify = get_spotify_client()
    if spotify:
        print("Spotify client initialized.")
        track = spotify.track("4uLU6hMCjMI75M1A2tKUQC")
        print("Track name:", track['name'])
        analysis = spotify.audio_analysis("4uLU6hMCjMI75M1A2tKUQC")
        print("Tempo from audio_analysis:", analysis['track']['tempo'])

        test_raw_audio_features(spotify)

    else:
        print("Spotify client not available.")
