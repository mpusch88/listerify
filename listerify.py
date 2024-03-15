import os
import sys
import argparse
import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException


# TODO - add / update shell profile instructions to readme
# TODO - add option to clean imported list of track / artist names from file
# TODO - add option for export format (CSV, TXT, etc.)
# TODO - list filesnames that contain invalid characters before writing to file
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
    # Check if an ID was provided
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


def get_playlist_tracks(sp, playlist_id, playlist_name):
    # Get the playlist tracks
    try:
        results = sp.playlist_tracks(playlist_id)
    except SpotifyException:
        print(
            f"Error: The playlist with ID {playlist_id} does not exist or could not be accessed."
        )

        sys.exit(1)

    if results["total"] == 0:
        print(f"Error: Playlist '{playlist_name}' does not contain any tracks.")
        sys.exit(1)
    else:
        return results


def write_tracks(exportPath, results, playlist_name):
    # Clean export path
    exportPath = os.path.join(exportPath, "")
    # Write the tracks to a file
    with open(os.path.join(exportPath, playlist_name), "w") as file:
        if not file.writable():
            print("Error: The file is not writable.")
            sys.exit(1)

        file.write(",")

        for item in results["items"]:
            track = item["track"]
            artist_names = [artist["name"] for artist in track["artists"]]

            # Concatenate track name and artist names into a single string
            track_and_artist = f"{track['name']} {' '.join(artist_names)}"

            # TODO - move cleaning to separate function, write single string to file
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
                file.write(f"'{track_and_artist}', ")
            else:
                file.write(f"'{track_and_artist}'")

        # If all tracks were written to the file, display the total number of tracks
        print(
            f"Successfully wrote {results['total']} {'track' if results['total'] == 1 else 'tracks'} to {exportPath}{playlist_name}"
        )


def copy_to_clipboard(results):
    resultList = []

    # TODO - handle this elsewhere (?)
    # Convert results to a string
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

        # Append the track_and_artist to the resultList
        resultList.append(track_and_artist)

    # Join the resultList with commas and add a leading comma
    result_string = ", " + ", ".join(resultList)

    # Copy the result_string to the clipboard
    if sys.platform == "win32":
        os.system(f"echo {result_string} | clip")
    elif sys.platform == "darwin":
        os.system(f'echo "{result_string}" | pbcopy')
    elif sys.platform == "linux":
        os.system(f'echo "{result_string}" | xclip -selection clipboard')

    print("Copied to clipboard.")


# TODO - use import_tracks function to clean the imported list of track / artist names from file
# def import_tracks(exportPath, args):
#     # Clean export path
#     exportPath = os.path.join(exportPath, "")
#     resultList = []

#     # Read the file
#     with open(os.path.join(exportPath, args.clean), "r") as file:
#         if not file.readable():
#             print("Error: The file is not readable.")
#             sys.exit(1)

#         # Read the file and remove all non alphanumeric characters
#         trackList = file.read()
#         trackList = "".join(e for e in trackList if e.isalnum() or e.isspace())

#         # Replace unknown ascii characters with blank spaces
#         trackList = "".join([c if ord(c) < 128 else " " for c in trackList])

#         # Remove duplicate words
#         trackList = " ".join(dict.fromkeys(trackList.split()))

#         # Remove double spaces
#         trackList = trackList.replace("  ", " ")

#         # Write the cleaned list to resultList
#         resultList.append(trackList)

#     return resultList


# TODO - use clean_tracks function to clean any list of track / artist names
# def clean_tracks(exportPath, args):
#     # Clean export path
#     exportPath = os.path.join(exportPath, "")

#     # Read the file
#     with open(os.path.join(exportPath, args.clean), "r") as file:
#         if not file.readable():
#             print("Error: The file is not readable.")
#             sys.exit(1)

#         # Read the file and remove all non alphanumeric characters
#         trackList = file.read()
#         trackList = "".join(e for e in trackList if e.isalnum() or e.isspace())

#         # Replace unknown ascii characters with blank spaces
#         trackList = "".join([c if ord(c) < 128 else " " for c in trackList])

#         # Remove duplicate words
#         trackList = " ".join(dict.fromkeys(trackList.split()))

#         # Remove double spaces
#         trackList = trackList.replace("  ", " ")

#         # Write the cleaned list to a new file
#         with open(os.path.join(exportPath, "cleaned_playlist.txt"), "w") as file:
#             if not file.writable():
#                 print("Error: The file is not writable.")
#                 sys.exit(1)

#             file.write(trackList)

#         # If all tracks were written to the file, display the total number of tracks
#         print(
#             f"Successfully wrote {results['total']} {'track' if results['total'] == 1 else 'tracks'} to {exportPath}{playlist_name}"
#         )


def parse_args():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process Spotify playlist.")

    parser.add_argument(
        "playlist", type=str, nargs="?", help="The URL or ID of the Spotify playlist."
    )
    parser.add_argument(
        "--path", type=str, help="The path where the playlist will be exported."
    )
    parser.add_argument(
        "--txt", action="store_true", help="Export the playlist as a TXT file."
    )
    parser.add_argument(
        "--csv", action="store_true", help="Export the playlist as a CSV file."
    )
    parser.add_argument(
        "--clean",
        type=str,
        nargs="?",
        help="Clean the imported list of track / artist names from file.",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # Validate command-line arguments
    if args.csv and args.txt:
        print("Error: You cannot specify both --csv and --txt.")
        sys.exit(1)

    # Test path
    if args.path:
        if not os.path.isdir(args.path):
            print("Error: Invalid export path.")
            sys.exit(1)

    # TODO - rename playlistID or playlist_id
    client_id, client_secret, exportPath, playlistID = read_config()

    # If command-line arguments were provided, use them instead of the values from the config file
    if args.playlist:
        playlistID = args.playlist
    if args.path:
        exportPath = args.path

    # Get the playlist ID
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

    # Get the playlist name and tracks
    playlist_name = get_playlist_name(sp, playlist_id)
    results = get_playlist_tracks(sp, playlist_id, playlist_name)

    if args.csv:
        playlist_name = f"{playlist_name}.csv"
        write_tracks(exportPath, results, playlist_name)
    elif args.txt:
        playlist_name = f"{playlist_name}.txt"
        write_tracks(exportPath, results, playlist_name)
    else:
        copy_to_clipboard(results)


if __name__ == "__main__":
    main()
