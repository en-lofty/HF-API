# HF-API
## Usage
`python hf_pb_notifier.py [-h] [-r REQUESTSPERHOUR] [-k HACKFORUMSKEY]
                         [-p PUSHBULLETKEY]`

### Optional arguments:
  `-r REQUESTSPERHOUR`
                        Sets the maximum requests per hour
                        
  `-k HACKFORUMSKEY`
                        Pass your Hackforums API key
                        
`  -p PUSHBULLETKEY`
                        Pass your Pushbullet API key
                        
## Features
- Alerts when a new reply is detected on a thread 
- Tracks when a new private message is received

## ToDo
### Thread tracking
- Push a snippet of the message
- Send the username of the user replying
### Other
- Wrap the json responses in a class for easy parsing.
