import os
import sys
import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException


# TODO - add CLI args for playlistID, exportPath, and CSV export option
# TODO - generate config.ini if not found or make config optional (?)
# TODO - test readme instructions for all system types
# TODO - optimize and clean up code
# TODO - add error handling for missing config.ini
# TODO - add error handling for missing playlistID
# TODO - add error handling for invalid playlistID
# TODO - add error handling for missing exportPath
# TODO - add error handling for invalid exportPath
# TODO - rename to zigzag (?)


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
        results = sp.playlist_tracks(playlist_id)
    except SpotifyException:
        print(
            f"Error: The playlist with ID {playlist_id} does not exist or could not be accessed."
        )

        sys.exit(1)

    if results["total"] == 0:
        print(f"Error: The playlist with ID {playlist_id} does not contain any tracks.")
        sys.exit(1)
    else:
        return results


def write_tracks(exportPath, results, playlist_name):
    # Clean export path
    exportPath = os.path.join(exportPath, "")

    playlist_name = f"{playlist_name}.txt"

    # Write the track names and artist names to a text file
    with open(os.path.join(exportPath, playlist_name), "w") as file:
        if not file.writable():
            print("Error: The file is not writable.")
            sys.exit(1)

        for item in results["items"]:
            track = item["track"]
            artist_names = [artist["name"] for artist in track["artists"]]

            # Concatenate track name and artist names into a single string
            track_and_artist = f"{track['name']} {' '.join(artist_names)}"

            # remove 'feat.', 'ft.', 'ft', 'featuring' from track_and_artist
            track_and_artist = track_and_artist.replace("featuring", "")
            track_and_artist = track_and_artist.replace("feat.", "")
            track_and_artist = track_and_artist.replace("ft.", "")
            track_and_artist = track_and_artist.replace("ft", "")

            # remove all non alphanumeric characters from track_and_artist
            track_and_artist = "".join(
                e for e in track_and_artist if e.isalnum() or e.isspace()
            )

            # Replace unknown ascii characters in track_and_artist with blank spaces
            track_and_artist = "".join(
                [c if ord(c) < 128 else " " for c in track_and_artist]
            )

            # remove duplicate words from track_and_artist
            track_and_artist = " ".join(dict.fromkeys(track_and_artist.split()))

            # remove double spaces from track_and_artist
            track_and_artist = track_and_artist.replace("  ", " ")

            # Write the string to the text file
            if item != results["items"][-1]:
                file.write(f'"{track_and_artist}", ')
            else:
                file.write(f'"{track_and_artist}"')

        # If all tracks were written to the file, display the total number of tracks
        print(
            f"Successfully wrote {results['total']} {'track' if results['total'] == 1 else 'tracks'} to {exportPath}{playlist_name}"
        )


def main():
    client_id, client_secret, exportPath, playlistID = read_config()
    playlist_id = get_playlist_id(playlistID)

    # Create a Spotify client
    try:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id, client_secret=client_secret
        )
    except SpotifyException:
        print("Error: Invalid Spotify API credentials.")
        sys.exit(1)

    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    playlist_name = get_playlist_name(sp, playlist_id)
    results = get_playlist_tracks(sp, playlist_id)

    write_tracks(exportPath, results, playlist_name)


if __name__ == "__main__":
    main()
