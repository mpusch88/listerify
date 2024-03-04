# Listerify

Python program that uses the Spotify Web API to fetch and print the names of all tracks in a given Spotify playlist.

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

PowerShell:

```powershell
New-Alias -Name listerify -Value "python <path_to_listerify>\listerify.py"
New-Alias -Name spotdl -Value "python C:\Users\mpusc\Repos\listerify\listerify.py"
```

ZSH:

```zsh
alias listerify="python <path_to_listerify>/listerify.py"
```

Bash:

```bash
alias listerify="python <path_to_listerify>/listerify.py"
```

## Configuration

The program can be configured via the config.ini file as follows:

- client_id: Your Spotify application's client ID.
- client_secret: Your Spotify application's client secret.
- exportPath: The path to the CSV file where the track names will be written.
- defaultPlaylistID: The default Spotify playlist ID to use if none is provided via command-line argument.

## Usage

A Spotify playlist ID can be provided when running the script as follows:

```bash
python listerify.py <playlist_id>
```

If no playlist is provided, the script will use the defined default playlist ID. If no default playlist ID is defined, the script will prompt the user to enter one.

## License

This project is licensed under the terms of the MIT license.
