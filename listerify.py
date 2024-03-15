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
        # TODO - remove newline from end of result_string
        os.system(f"echo {result_string} | clip")
    elif sys.platform == "darwin":
        os.system(f'echo "{result_string}" | pbcopy')
    elif sys.platform == "linux":
        os.system(f'echo "{result_string}" | xclip -selection clipboard')

    print(f"Copied {results['total']} {'track' if results['total'] == 1 else 'tracks'} to clipboard.")


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
    
    # TODO - finish cleaning function and test on searchList
    searchList = ['Stories In Light Trilucid', 'Supermode Tell Me Why James Carter Extended Remix', 'Time Moves So Fast PROFF Volen Sentirs Timestop Remix BT Sentir', 'Collision Argy', 'Wilderness Argy', 'Balance Wilkinson NORTH', 'Tarantula Max Styler Remix Pleasurekra', 'Thats OK Jonwayne', 'Lovers In A Past Life with RagnBone Man Calvin Harris', 'Sound of Shadows Lets Karpool Remix Matoma JP Cooper', 'Thank You Not So Bad Extended Dimitri Vegas Like Mike Ti sto Dido WW', 'No Warning Signal', 'Judgement Signal', 'Dusk Original Signal HYQXYZ', 'Doom Desire Signal', 'Catchin Freights Alejo', 'The Scientific Ultra Violet Light Generator Alejo', 'Put the Mic On Alejo Schmoop', 'Hated On (Funkatron) Gabry Ponte', 'so far so good viot', 'Haze Nuage Remix Bootie Grove', 'Haze Bootie Grove', 'Hear The Tongue Fork Throwing Snow', 'Higher Ground Extended Mix Robbie Rivera', 'I m Not Giving Up (with MEMBA) Louis The Child', 'I Think of You okaywill', 'Immersion Verdance', 'Impression Neversky', 'In the Dark AkaHendy', 'Interference Cover Mr. Bill', 'Into It (with Danni Carra) Sublab', 'It is Almost Fall Mindex', 'it s me extended spencer brown', 'Jetlag Glimlip', 'Karma Nora Van Elken', 'Keep on Shining Dreamers Delight', 'king christian quietly mew', 'Ladyship Deka Sul The Polish Ambassador', 'Last Words Edapollo Remix Lonely in the Rain, Neeskens', 'Legend Eternal Cymek', 'Letters Gryr', 'Light Tunnel Dreamers Delight', 'Lights Neversky', 'Like Drugs Gluckskind', 'Long Nights Neversky', 'Look Up Ranz', 'lust akahendy', 'mantra nora van elken', 'Mantra Nora Van Elken', 'Marco Polo Glimlip', 'Memories Chmura', 'more bounce KOLA', 'Mwaki Ti stos VIP Mix Zerb sto Sofiya Nzau', 'When Im With You Rimzee Chase Status', 'Everywhere Nowhere Rezz Blanke', 'tell me extended Shygirl Boys Noize', 'Intuici n Yulia Niko Sil Romero', 'Herald Neil Cowley', 'Moss PALLADIAN Remix Mookee PALLADIAN', 'Olsen Aer Midnight Lamorn', 'Iriso Livemixx Eprom', 'Rabat Emancipator Remix Balkan Bump', 'Grey Area Supertask', 'Say Nothing edapollo', 'Chicken Dinner okaywill', 'Walking Blackmill TRK', 'Mr. Nobody HIROWS', 'neversky', 'NEW TRK Blackmill Joviee', 'next to blue gauze', 'Nirvana Nora Van Elken', 'No One Extended Mix Matteo Marini', 'Nostalgia Late June Remix XIXI, Late June, Julie Trouvé', 'Andaman Islands Iyakuh LoRenzo', 'AEIOU Anfisa Letyago Remix PNAU Empire Of The Sun', 'Wolves Dreams Mindex Remix Vena Portae', 'When Youre Watching Me Original Mix Krankbrother', 'Neck Wrist JAYZ Pharrell Williams Pusha T', 'Palaces Damon Albarn Zelooperz Mount Kimbie Die Cuts Remix Flume Dom Maker', 'Oasis Deka Sul, The Polish Ambassador', 'Old Soul TRK, Dan Dakota, Blackmill', 'Omuamua M1NT', 'Pain Adiios', 'PARADISE HI-LO, DANNY AVILA, Oliver Heldens', 'Prana Nora Van Elken', 'Promise Entangled Mind', 'Pseudoscience Køps Relativity Lounge', 'pull up meeshroom', 'Quantum Dreamers Delight', 'Rapids Late June', 'Rapids Late June', 'Rebirth Nora Van Elken', 'Redemption Midnight in Amsterdam We re Up Late Remix MOGUAI, RMB, Midnight In Amsterdam', 'reluctant relativity lounge', 'Reverie Remastered Esbe', 'Right Gut FRCTLS', 'rosewatercounty, pt. II sunflwr', 'Sammy Sosa Samsohn', 'sanfekere', 'observatory dreamers', 'Softboi Vinyl Oomah Remix Mux Mool, Oomah', 'Soulevement Throwing Snow Remix Tristan De Liege', 'space between instrumentals phaeleh', 'Special Place Neversky', 'Speedle Nibana Remix Nibana, Electrocado, Circuit Bent', 'Stay Down extended mix Marava', 'supertask compression', 'Swimming Through The Sky AkaHendy', 'System Error Cospe', 'Take Control Grafix', 'Take My Hand AkaHendy PRZM', 'Boom Boom Boom Yeah Jon1st', 'Freedom over Everything (feat. Black Thought & Logan Richardson) (Lumen Remix) Vince Mendoza, Czech National Symphony Orchestra, Black Thought, Logan Richardson, Lumen', 'that way genix', 'That Way Genix Dub Mix Illuminor', 'the naughty list relativity', 'The World Is Dying Michael Woods', 'Through the Lens of the Forest Mfinity', 'Toca s Miracle (Culture Shock & Sub Focus Remix)', 'Too Late Arley', 'Transcendental Nora Van Elken', 'Ultra Light Kimyan Lawtt', 'Upstairs Blackmill TRK Dan Dakota', 'Voodoo People Delta Heavy remix The Prodigy', 'Way Of The Underground Born in 92', 'Dol Guldur visages', 'Wondering L!NVS', 'Your Body Instrumental Misha', 'Your Body Misha', 'ZOOM Machinedrum, Tinashea', 'Aftermath Beamer', 'altitude mfinity', 'Analogy Martin Roth', 'Arintintin Rico Nasty, Boys Noize', 'Astral Projections okaywill', 'Back to Zero dirtwire', 'Barely Lukewarm (Vinylshakerz Remix) KLAS1NG', 'Be Ready TRK, Blackmill', 'Be the one (madface bootleg) Eli Brown', 'Behind the Tree Dirtwire', 'Blue Coney PALLADIAN', 'Candy opiuo', 'Castle Mountain Canadian Rockies Kelpe Kel McKeown', 'Celebration of Life Reimagined Mfinity', 'Choices Village, flyingarden', 'cockpit country mungk', 'Come Back Original Mix AkaHendy', 'Cycles Late June', 'Dipping (feat. Ruku) Lab Group', 'dipping supertask', 'Dirty Bump T-Puse Remix Balkan Bump', 'Dissipate AkaHendy', 'Dreams (Rework) yune pinku', 'Eastern Sunrise Nopi Remix NevadaSYSTEM', 'Encore FRCTLS', 'Encore FRCTLS', 'Escape Marava', 'Everything Extended Mix Oliver Smith Tom Bailey', 'Falling Neversky', 'Färd Gryr', 'Flaws Late June', 'Floral Dance, Pt. 3 Radio Edit NevadaSYSTEM', 'Friends (Lexurus Bootleg) Meduza', 'Funhouse Record Club', 'Galaxy Eyes Dreamers Delight', 'Get Loose (feat. Pete Rock) Saigon', 'Go Mazde Rromarin', 'Gravity Sub Focus, Wilkinson', 'Wind of Freedom Rapossa', 'Flames Rapossa', 'Madera Rapossa Remix ANuT MoM', 'Road to Burn Rapossa', 'Shanti Goldcap Remix Rapossa', 'Delom DJ Phellix Gobi Desert Collective Sheenubb', 'Jafar Elfenberg', 'Cuzco Elfenberg', 'Gilgamesh Elfenberg', 'Sinere Elfenberg Remix rBert', 'Bazaar Elfenberg', 'Oiga Mi Alero Mollono Bass Remix Seba Campos Lemurian MollonoBass', 'All In A Dream LP Giobbi DJ Tennis Joseph Ashworth', 'LLTB Jam City Wet', 'The Yuzer DJ Plead Remix Dauwd', 'The Wall ABIS Signal Tasha Baxter', 'These Eyes Signal', 'Move Me Signal', 'Artworld Signal DLR ABIS', 'Delirium Signal Disprove', 'Whispers Of The Night Kaiyan', 'Fellas Extended Mix Spencer Brown', 'Ladies Love LFOs Spencer Brown']
    
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
