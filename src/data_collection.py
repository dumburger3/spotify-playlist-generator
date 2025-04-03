import os
import pandas as pd
import time
from spotify_auth import get_spotify_client

def get_user_top_items(limit=50, time_range='medium_term'):
    """
    Get a user's top tracks and artists from Spotify
    
    Parameters:
    -----------
    limit : int
        The number of items to fetch (max 50)
    time_range : str
        The time range to consider: 'short_term' (4 weeks), 
        'medium_term' (6 months), or 'long_term' (years)
    
    Returns:
    --------
    tuple : (top_tracks_df, top_artists_df)
        DataFrames containing the user's top tracks and artists
    """
    spotify = get_spotify_client()
    
    # Get top tracks
    top_tracks = spotify.current_user_top_tracks(limit=limit, time_range=time_range)
    
    # Process tracks data
    tracks_data = []
    for i, track in enumerate(top_tracks['items']):
        track_data = {
            'rank': i + 1,
            'id': track['id'],
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'artist_id': track['artists'][0]['id'],
            'album': track['album']['name'],
            'popularity': track['popularity'],
            'duration_ms': track['duration_ms']
        }
        tracks_data.append(track_data)
    
    # Create DataFrame from tracks data
    top_tracks_df = pd.DataFrame(tracks_data)
    
    # Get top artists
    top_artists = spotify.current_user_top_artists(limit=limit, time_range=time_range)
    
    # Process artists data
    artists_data = []
    for i, artist in enumerate(top_artists['items']):
        artist_data = {
            'rank': i + 1,
            'id': artist['id'],
            'name': artist['name'],
            'genres': ', '.join(artist['genres']),
            'popularity': artist['popularity'],
            'followers': artist['followers']['total']
        }
        artists_data.append(artist_data)
    
    # Create DataFrame from artists data
    top_artists_df = pd.DataFrame(artists_data)
    
    return top_tracks_df, top_artists_df

def get_audio_features(track_ids):
    """
    Get audio features for a list of tracks
    """
    spotify = get_spotify_client()
    
    # Create an empty DataFrame as fallback
    empty_df = pd.DataFrame(columns=['id', 'danceability', 'energy', 'key', 
                           'loudness', 'mode', 'speechiness', 
                           'acousticness', 'instrumentalness', 
                           'liveness', 'valence', 'tempo'])
    
    if not track_ids:
        return empty_df
    
    # Process in much smaller batches - try just 10 at a time
    features_data = []
    
    try:
        # Process in batches of 10
        for i in range(0, len(track_ids), 10):
            batch = track_ids[i:i+10]
            try:
                # Get features for individual tracks instead of batch
                for track_id in batch:
                    try:
                        # Get feature for a single track
                        feature = spotify.audio_features(track_id)[0]
                        if feature:
                            features_data.append(feature)
                        # Slight pause to avoid rate limits
                        time.sleep(0.1)
                    except Exception as e:
                        print(f"Error getting features for track {track_id}: {str(e)}")
                        continue
                
                # Longer pause between batches
                time.sleep(1)
            except Exception as e:
                print(f"Error processing batch {i//10 + 1}: {str(e)}")
                continue
        
        # Convert to DataFrame
        if features_data:
            features_df = pd.DataFrame(features_data)
            
            # Select only the useful columns
            if not features_df.empty:
                features_df = features_df[['id', 'danceability', 'energy', 'key', 
                                       'loudness', 'mode', 'speechiness', 
                                       'acousticness', 'instrumentalness', 
                                       'liveness', 'valence', 'tempo']]
                return features_df
        
        return empty_df
        
    except Exception as e:
        print(f"Failed to get audio features: {str(e)}")
        return empty_df

def get_genre_recommendations(genres, limit=50):
    """
    Get track recommendations based on seed genres
    
    Parameters:
    -----------
    genres : list
        List of seed genres (max 5)
    limit : int
        Number of tracks to recommend (max 100)
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing recommended tracks
    """
    spotify = get_spotify_client()
    
    # Create empty DataFrame
    empty_df = pd.DataFrame(columns=['id', 'name', 'artist', 'artist_id', 'album', 'popularity'])
    
    # Check if we have valid genres
    valid_genres = [g for g in genres if g and g.strip()]
    if not valid_genres:
        print("No valid genres provided for recommendations")
        return empty_df
    
    # Ensure we don't exceed the 5 seed genres limit
    seed_genres = valid_genres[:5]
    
    try:
        # Get recommendations
        print(f"Getting recommendations for genres: {', '.join(seed_genres)}")
        recommendations = spotify.recommendations(seed_genres=seed_genres, limit=limit)
        
        # Process recommendations data
        rec_data = []
        for i, track in enumerate(recommendations['tracks']):
            rec_item = {
                'id': track['id'],
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'artist_id': track['artists'][0]['id'],
                'album': track['album']['name'],
                'popularity': track['popularity']
            }
            rec_data.append(rec_item)
        
        rec_df = pd.DataFrame(rec_data)
        return rec_df
        
    except Exception as e:
        print(f"Error getting recommendations: {str(e)}")
        return empty_df

def save_data(dataframe, filename):
    """
    Save a DataFrame to CSV in the data directory
    
    Parameters:
    -----------
    dataframe : pandas.DataFrame
        The DataFrame to save
    filename : str
        The name of the file (without path)
    """
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Save to CSV
    filepath = os.path.join('data', filename)
    dataframe.to_csv(filepath, index=False)
    print(f"Data saved to {filepath}")

def collect_and_save_user_data():
    """
    Collect user data and audio features and save to CSV files
    """
    try:
        print("Collecting user's top tracks and artists...")
        top_tracks_df, top_artists_df = get_user_top_items(limit=50)
        
        # Save basic data first
        save_data(top_tracks_df, 'top_tracks.csv')
        save_data(top_artists_df, 'top_artists.csv')
        
        try:
            print("Collecting audio features for top tracks...")
            track_ids = top_tracks_df['id'].tolist()
            audio_features_df = get_audio_features(track_ids)
            
            # Merge track info with audio features
            if not audio_features_df.empty:
                tracks_with_features = pd.merge(top_tracks_df, audio_features_df, on='id')
                save_data(tracks_with_features, 'tracks_with_features.csv')
            
        except Exception as e:
            print(f"Warning: Could not get audio features: {str(e)}")
            print("Continuing without audio features...")
        
        # Extract genres from top artists - FIX HERE
        genres = []
        for genre_str in top_artists_df['genres']:
            if pd.notna(genre_str) and genre_str.strip():  # Check if not NaN or empty
                genres.extend([g.strip() for g in genre_str.split(',')])
        
        # Count genre frequencies and get top 5
        if genres:
            genre_counts = pd.Series(genres).value_counts()
            # Only take non-empty genres
            
            # Get valid Spotify seed genres
            valid_seed_genres = spotify .recommendation_genre_seeds()['genres']
            # Filter top genres to only those accepted by Spotify
            valid_genres = [g for g in genre_counts.index if g.strip().lower() in valid_seed_genres][:5]
            
            if valid_genres:
                print(f"Top genres identified: {', '.join(valid_genres)}")
                
                # Get recommendations based on top genres
                print("Getting recommendations based on top genres...")
                recommendations_df = get_genre_recommendations(valid_genres, limit=100)
                save_data(recommendations_df, 'recommendations.csv')
            else:
                print("No valid genres found. Skipping recommendations.")
        else:
            print("No genres found. Skipping recommendations.")
        
        print("Data collection complete!")
        
    except Exception as e:
        print(f"Error during data collection: {str(e)}")

if __name__ == "__main__":
    collect_and_save_user_data()
