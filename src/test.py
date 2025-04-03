from spotify_auth import get_spotify_client

sp = get_spotify_client()

# This should work
print("➡️ Current user:", sp.current_user())

# This should NOT 403
print("➡️ Audio features:", sp.audio_features(["1YH01s3qSCjwt1eEHg6LRG"]))

# This should NOT 404
print("➡️ Genre seeds:", sp.recommendation_genre_seeds())
