# Listerify

Listerify is a Python script that uses the Spotify API to save track information from Spotify playlists.

## Required Packages

- [spotipy](https://pypi.org/project/spotipy/)
- [pyperclip](https://pypi.org/project/pyperclip/)

## Installation

1. Clone this repository:

    `git clone <https://github.com/mpusch88/listerify>`

2. Install the required Python packages:

    `pip install -r requirements.txt`

3. Create a Spotify application and get your client ID and client secret. You can do this by logging in to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications) and creating a new application. Note that the name and description of the application do not matter.

<!-- 4. (Optional) From the Listerify directory, create an alias to launch the script:

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
``` -->

## Configuration

The program can be configured via the generated `config.ini` file.

The `config.ini` file should be located in the same directory as `listerify.py` and should have the following format:

```ini
[Spotify]
client_id = your_spotify_client_id
client_secret = your_spotify_client_secret
playlistID = your_spotify_playlist_id

[General]
exportPath = path_to_export_directory
importFile = path_to_import_file
```

Where:

- `client_id` is your Spotify application's client ID. (example: `client_id = 1234567890abcdef1234567890abcdef`)
- `client_secret` is your Spotify application's client secret. (example: `client_secret = 987654321`)
- `playlistID` (Optional) The default Spotify playlist ID to get data from. Can be left empty to prompt the user for a playlist ID. (example: `playlistID = 5LNJmXPclDxbncKlzqYVdw`)
- `exportPath`: The directory where the playlist will be exported. (example: `exportPath = "C:\Users\user\Desktop"`)
- `importFile`: (Optional) Path to a file containing a list of track / artist names to import. (example: `importFile = "C:\Users\user\Documents\tracks.txt"`)

## Usage

A Spotify playlist ID can be provided when running the script as follows:

```bash
python listerify.py <playlist_id> [--importFile <pathToImportFile>| --txt | --csv]
```

The following arguments can be added:

- A playlist ID can optionally be provided as the first argument.
- `--importFile <pathToImportFile>` - Will clean tracks from the import file instead of Spotify.
- `--txt` - Outputs to text file
- `--csv` - Outputs to CSV

Note that only one of the `txt` or `csv` outputs can be selected at a time.

If no playlist ID argument is provided, the script will use the default playlist ID from `config.ini`. If no default playlist ID is defined, the script will prompt the user to enter one.

Note that running this script will generate a cache file in the same directory as `listerify.py` called `.cache`. This fle is used to store thei user's Spotify access token and should not be deleted.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
