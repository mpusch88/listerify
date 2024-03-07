# Listerify

Listerify is a Python script that uses the Spotify API to save Spotify playlists to a CSV file.

## Requirements

- Python 3
- spotipy Python library

## Installation

1. Clone this repository:

    git clone <https://github.com/mpusch88/listerify.git>

2. Install the required Python libraries:

    pip install spotipy

3. Create a Spotify application and get your client ID and client secret. You can do this by logging in to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications) and creating a new application.

4. (Optional) From the Listerify directory, create an alias to launch the script:

PowerShell - Add the following line to your profile file (e.g. `Microsoft.PowerShell_profile.ps1`):

```powershell
function listerify {
  cd "<path_to_listerify>"; & python listerify.py
}
```

ZSH - Add the following line to your `.zshrc` file:

```zsh
alias listerify="python <path_to_listerify>/listerify.py"
```

Bash - Add the following line to your `.bashrc` file:

```bash
alias listerify="python <path_to_listerify>/listerify.py"
```

## Configuration

The program can be configured via a `config.ini` file.

It is highly recommended to create this file to avoid having to enter your Spotify application's client ID and client secret every time you run the script.

It is also possible to set the path to the program's output file, as well as the default playlist ID.

The file should be located in the same directory as `listerify.py` and have the following format:

```ini
[Spotify]
client_id = <your_client_id>
client_secret = <your_client_secret>
exportPath = <path_to_export_file>
defaultPlaylistID = <default_playlist_id>
```

Where:

- `client_id` is your Spotify application's client ID. (example: `client_id = 1234567890abcdef1234567890abcdef`)
- `client_secret` is your Spotify application's client secret. (example: `client_secret = 987654321`)
- `exportPath` is the path to the CSV file where the track names will be written. Can be left empty to use the default path. (example: `exportPath = "C:\Users\user\Desktop\tracks.csv"`)
- `defaultPlaylistID` is the default Spotify playlist ID to use if none is provided via command-line argument. Can be left empty to prompt the user for a playlist ID. (example: `defaultPlaylistID = 5LNJmXPclDxbncKlzqYVdw`)

## Usage

A Spotify playlist ID can be provided when running the script as follows:

```bash
python listerify.py <playlist_id>
```

If no playlist is provided, the script will use the defined default playlist ID. If no default playlist ID is defined, the script will prompt the user to enter one.

Note that running this script will generate a cache file in the same directory as `listerify.py` called `.cache`. This file is used to store the user's Spotify access token and should not be deleted.

## License

This project is licensed under the terms of the MIT license.
