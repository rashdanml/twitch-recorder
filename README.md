# twitch-recorder

Python Script to automatically archive Twitch streams, checking periodically to see if channel is live. Adapted from an old blog post, using newer Twitch API and other minor tweaks. [How to Record Twitch Streams Automatically in Python](https://www.godo.dev/tutorials/python-record-twitch/)

## Setup

- Clone the repository
- Rename config-example.ini to config.ini
- Obtain ClientID and ClientSecret from dev.twitch.tv by creating an application, update config.ini with it. 
- Leave OAuthToken blank, it will automatically fetch a token on first run. 
- Create virtual environment, install dependencies from requirements.txt

### Key dependencies
- ffmpeg
- streamlink

## Usage
Run: 
`python twitch-recorder.py -u [username] -q [quality]` from within the virtual environment. 

If username and quality not specified, script defaults to `self.username` and `self.quality` specified in twitch-recorder.py 

### Quality options

Available options depend on the stream, which can be checked by running `streamlink`. Options: best, 1080p, 720p, 480p, 360p, etc. **best** selects the highest available. 
