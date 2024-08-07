import argparse
import configparser
import os
import pyperclip
import spotipy
import sys

from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException


# TODO - handle cases
# TODO - keywords (ex. "spencer")
# TODO - inclulde more info in output files (album, year, etc.)
# TODO - put artist first for copy function
# TODO - accept album and track IDs as well as playlist IDs
# TODO - give spotify playlist ID args priority over importFile
# TODO - ensure all variable names make sense
# TODO - add error handling for all config sections / properties
# TODO - enable exporting multiple formats at once
# TODO - add config parameter for default export type / format
# TODO - add exclusions list to remove certain words from track names
# TODO - remove "x" from artist names (?)
# TODO - link to external config (?)
# TODO - code platform specific clipboard copy functions instead of using pyperclip
# TODO - add interface (?)
# TODO - rust version (?)
# TODO - optimize and clean up code
# TODO - write tests for all functions
# TODO - update REAMDE, test instructions for all system types
# TODO - fix shell profile instructions in REAMDE
# TODO - rename (zz)


# TODO - add config parameter for default export type / format
# TODO - ask user if they want to use import file
# TODO - add clipboard arg


def parse_args():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process Spotify playlist.")

    parser.add_argument(
        "--playlist", type=str, help="The URL or ID of the Spotify playlist."
    )
    parser.add_argument(
        "--exportPath", type=str, help="The path where the playlist will be exported."
    )
    parser.add_argument(
        "--importFile",
        type=str,
        nargs="?",
        help="The path where the imported list of track / artist names is located.",
    )
    parser.add_argument(
        "--txt", action="store_true", help="Export the playlist as a TXT file."
    )
    parser.add_argument(
        "--csv", action="store_true", help="Export the playlist as a CSV file."
    )

    return parser.parse_args()


def create_config():
    # Create a new configuration file
    config = configparser.ConfigParser()

    # Ask the user for the Spotify API credentials
    client_id = input("Enter your Spotify client ID: ")
    client_secret = input("Enter your Spotify client secret: ")

    # Ask whether the user wants to set a default playlist ID
    set_playlist_id = input("Do you want to set a default playlist ID? (y/n): ")

    if set_playlist_id.lower() == "y":
        playlist_id = input("Enter the default playlist ID: ")
    else:
        playlist_id = ""

    # Set the default configuration values
    config["Spotify"] = {
        "client_id": client_id,
        "client_secret": client_secret,
        "playlistID": playlist_id,
    }

    # Ask if the user wants to set a default export path
    set_export_path = input("Do you want to set a default export path? (y/n): ")

    if set_export_path.lower() == "y":
        export_path = input("Enter the default export path: ")
    else:
        export_path = os.getcwd()

    # Validate the export path
    while not os.path.isdir(export_path):
        if os.path.exists(os.path.dirname(export_path)):
            # Ask the user if they want to create the directory
            create_dir = input(
                "The directory does not exist. Do you want to create it? (y/n): "
            )

            if create_dir.lower() == "y":
                try:
                    os.makedirs(export_path)
                except OSError as e:
                    print(f"Error: {e}")
                    export_path = input("Please enter a valid export path: ")
            else:
                export_path = input("Please enter a valid export path: ")
        else:
            export_path = input("Please enter a valid export path: ")

    # Set the default configuration values
    config["General"] = {
        "exportPath": export_path,
        "importFile": "",
    }

    # Write the configuration to the file
    with open("config.ini", "w") as file:
        config.optionxform = str  # Preserve case sensitivity
        config.write(file)


def read_config():
    # Read the configuration file
    config = configparser.ConfigParser()
    config.read("config.ini")

    if not config.has_section("Spotify"):
        print("Error: The configuration file is missing the [Spotify] section.")
        sys.exit(1)

    # Get the Spotify API credentials from the configuration file
    client_id = config.get("Spotify", "client_id")
    client_secret = config.get("Spotify", "client_secret")

    # Validate the Spotify API credentials
    if not client_id or not client_secret:
        print("Error: Invalid Spotify API credentials.")
        sys.exit(1)

    # Set remaining configuration values
    if config.has_option("Spotify", "playlistID"):
        playlistID = config.get("Spotify", "playlistID")
    if config.has_option("General", "exportPath"):
        exportPath = config.get("General", "exportPath")

        if not os.path.isdir(exportPath):
            print("Error: Invalid export path.")
            sys.exit(1)
    else:
        exportPath = os.getcwd()

    # Check if an import file was provided
    if config.has_option("General", "importFile"):
        importFile = config.get("General", "importFile")
    else:
        importFile = None

    if importFile and not os.path.isfile(importFile):
        print("Error: Invalid import path.")
        sys.exit(1)

    return client_id, client_secret, playlistID, exportPath, importFile


def import_tracks(importFile):
    dirty_list = []

    print(f"Importing tracks from {importFile}...")

    with open(importFile, "r") as file:
        if not file.readable():
            print("Error: The file is not readable.")
            sys.exit(1)

        dirty_list = file.read().splitlines()

    return dirty_list


def get_playlist_id(playlistID):
    # Check if an ID was provided
    if playlistID is None or playlistID == "":
        # If not, query the user for the playlist ID
        playlist_id = input("Enter the playlist ID: ")
    else:
        playlist_id = playlistID

    return playlist_id


def get_playlist_name(playlist_id, sp):
    # Get the playlist metadata
    try:
        playlist = sp.playlist(playlist_id)
    except SpotifyException:
        print("Error: The playlist does not exist or could not be accessed.")
        sys.exit(1)
    except Exception as e:
        print(f"Spotify client {str(e)}")
        sys.exit(1)

    return playlist["name"]


def get_playlist_tracks(playlist_id, playlist_name, sp):
    limit = 100  # Maximum number of tracks per API request
    offset = 0
    list_tracks = []

    while True:
        # Get the playlist tracks
        try:
            dirty_list = sp.playlist_tracks(playlist_id, offset=offset, limit=limit)
        except SpotifyException:
            print(
                f"Error: The playlist with ID {playlist_id} does not exist or could not be accessed."
            )

            sys.exit(1)

        if dirty_list["total"] == 0:
            print(f"Playlist '{playlist_name}' does not contain any tracks.")
            sys.exit(1)

        for item in dirty_list["items"]:
            artists = [artist["name"] for artist in item["track"]["artists"]]
            track_and_artist = f"{item['track']['name']} - {', '.join(artists)}"
            list_tracks.append(track_and_artist)

        # Check if we need to fetch more tracks
        if len(dirty_list["items"]) < limit:
            break

        # Update the offset for the next request
        offset += limit

    return list_tracks


def clean_tracks(list):
    for i in range(len(list)):
        # remove 'feat.', 'feat', 'ft.', 'ft', 'featuring' from item
        list[i] = list[i].replace(" featuring", "")
        list[i] = list[i].replace(" feat.", "")
        list[i] = list[i].replace(" ft.", "")
        list[i] = list[i].replace(" feat ", " ")
        list[i] = list[i].replace(" ft ", " ")

        # remove "with" if line has more than 5 words
        if len(list[i].split()) > 5:
            list[i] = list[i].replace(" with ", " ")
            list[i] = list[i].replace("(with ", "")

        # remove all non alphanumeric characters from item
        list[i] = "".join(e if e.isalnum() or e.isspace() else " " for e in list[i])

        # Replace unknown ascii characters in item with blank spaces
        list[i] = "".join([c if ord(c) < 128 else " " for c in list[i]])

        # remove duplicate words from item
        list[i] = " ".join(dict.fromkeys(list[i].split()))

        # remove double spaces from item
        list[i] = list[i].replace("  ", " ")

    return list


def write_tracks(cleaned_list, playlist_name, exportPath):
    # Clean exportPath
    exportPath = os.path.join(exportPath, "")

    # Write the tracks to a file
    with open(os.path.join(exportPath, playlist_name), "w", encoding="utf-8") as file:
        if not file.writable():
            print("Error: The file is not writable.")
            sys.exit(1)

        for index, item in enumerate(cleaned_list):
            # Write the string to the text file
            if index != len(cleaned_list) - 1:
                file.write(f"{item}\n")
            else:
                file.write(f"{item}")

        # If tracks were written to the file, display the total number of tracks
        print(
            f"Successfully wrote {len(cleaned_list)} {'track' if len(cleaned_list) == 1 else 'tracks'} to {playlist_name}."
        )


def copy_to_clipboard(cleaned_list):
    # Join the list with commas and add a leading comma
    result_string = ", " + ", ".join([f"'{track}'" for track in cleaned_list])
    pyperclip.copy(result_string.strip())

    print(
        f"Copied {len(cleaned_list)} {'track' if len(cleaned_list) == 1 else 'tracks'} to clipboard."
    )


def main():
    args = parse_args()

    # Validate command-line arguments
    if args.csv and args.txt:
        print("Error: You cannot specify both --csv and --txt.")
        sys.exit(1)

    # Test path
    if args.exportPath:
        if not os.path.isdir(args.exportPath):
            print("Error: Invalid export path.")
            sys.exit(1)
    if args.importFile:
        if not os.path.isfile(args.importFile):
            print("Error: Invalid import file.")
            sys.exit(1)

    # Ensure config.ini exists
    if not os.path.isfile("config.ini"):
        create_config()

    # TODO - rename playlistID or playlist_id
    client_id, client_secret, playlistID, exportPath, importFile = read_config()

    # If command-line arguments were provided, use them instead of the values from the config file
    if args.playlist:
        playlistID = args.playlist
    if args.exportPath:
        exportPath = args.exportPath
    if args.importFile:
        importFile = args.importFile

    cleaned_list = []

    if importFile:
        dirty_list = import_tracks(importFile)
        cleaned_list = clean_tracks(dirty_list)
    else:
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
        playlist_name = get_playlist_name(playlist_id, sp)
        print(f"Analyzing playlist '{playlist_name}'.")

        # Clean tracks unless writing to file
        if args.csv or args.txt:
            cleaned_list = get_playlist_tracks(playlist_id, playlist_name, sp)
        else:
            cleaned_list = clean_tracks(
                get_playlist_tracks(playlist_id, playlist_name, sp)
            )

    if importFile:
        playlist_name = "Cleaned Tracks"

        if args.csv:
            write_tracks(cleaned_list, f"{playlist_name}.csv", exportPath)
        elif args.txt:
            write_tracks(cleaned_list, f"{playlist_name}.txt", exportPath)
        else:
            copy_to_clipboard(cleaned_list)
    else:
        if args.csv:
            playlist_name = f"{playlist_name}.csv"
            write_tracks(cleaned_list, playlist_name, exportPath)
        elif args.txt:
            playlist_name = f"{playlist_name}.txt"
            write_tracks(cleaned_list, playlist_name, exportPath)
        else:
            copy_to_clipboard(cleaned_list)


if __name__ == "__main__":
    main()
