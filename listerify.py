import csv
import os
import sys
import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException


# TODO - macOS only - uninstall autoenv, install direnv (?)
# TODO - remove .env files (?)
# TODO - make config optional
# TODO - generate config.ini if not found (?)
# TODO - remove config from git
# TODO - sanitize output
# TODO - test readme instructions
# TODO - optimize and clean up code


def read_config():
    # Read the configuration file
    config = configparser.ConfigParser()
    config.read("config.ini")

    # Get the Spotify API credentials from the configuration file
    client_id = config.get("Spotify", "client_id")
    client_secret = config.get("Spotify", "client_secret")
    exportPath = config.get("Spotify", "exportPath")
    playlistID = config.get("Spotify", "defaultPlaylistID")

    # Validate configuration
    if not client_id or not client_secret:
        print("Error: Invalid Spotify API credentials.")
        sys.exit(1)

    if not os.path.isdir(exportPath):
        print("Error: Invalid export path.")
        sys.exit(1)

    return client_id, client_secret, exportPath, playlistID


def get_playlist_id(playlistID):
    # Check if a command-line argument was provided
    if playlistID is None or playlistID == "":
        # If not, query the user for the playlist ID
        playlist_id = input("Enter the playlist ID: ")
    else:
        playlist_id = playlistID

    return playlist_id


def get_playlist_name(sp, playlist_id):
    # Get the playlist metadata
    try:
        print("Fetching playlist metadata...")
        playlist = sp.playlist(playlist_id)
    except SpotifyException:
        print(
            f"Error: The playlist with ID {playlist_id} does not exist or could not be accessed."
        )

        sys.exit(1)

    return playlist["name"]


def get_playlist_tracks(sp, playlist_id):
    # Get the playlist tracks
    try:
        print("Fetching playlist tracks...")
        results = sp.playlist_tracks(playlist_id)
    except SpotifyException:
        print(
            f"Error: The playlist with ID {playlist_id} does not exist or could not be accessed."
        )

        sys.exit(1)

    return results


def write_tracks_to_csv(exportPath, results, playlist_name):
    # Clean export path
    exportPath = os.path.join(exportPath, "")

    # Open a CSV file on the desktop
    with open(os.path.join(exportPath, "playlist.csv"), "w", newline="") as file:
        if not file.writable():
            print("Error: The file is not writable.")
            sys.exit(1)

        writer = csv.writer(file)

        # Write the track names and artist names to the CSV file
        print("Writing tracks to CSV file...")

        for item in results["items"]:
            track = item["track"]
            artist_names = [artist["name"] for artist in track["artists"]]

            # Concatenate track name and artist names into a single string
            track_and_artist = f"{track['name']} {', '.join(artist_names)}"

            # Write the string to the CSV file as a single column
            writer.writerow([track_and_artist])

        # If all tracks were written to the file, display the total number of tracks
        print(
            f"Successfully wrote {results['total']} {'track' if results['total'] == 1 else 'tracks'} to {exportPath}{playlist_name}.csv."
        )


def main():
    client_id, client_secret, exportPath, playlistID = read_config()
    playlist_id = get_playlist_id(playlistID)

    # Create a Spotify client
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id, client_secret=client_secret
    )

    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    playlist_name = get_playlist_name(sp, playlist_id)
    results = get_playlist_tracks(sp, playlist_id)

    write_tracks_to_csv(exportPath, results, playlist_name)


if __name__ == "__main__":
    main()
