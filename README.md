# Work in progress

## Electrolux Group API Client
This is a Python client for the Electrolux Group API. It is a simple wrapper around the API, which allows you to interact with the API in a more Pythonic way.

### Usage
```bash
usage: cli.py [-h] -k API_KEY -t ACCESS_TOKEN -r REFRESH_TOKEN {list,command} ...

positional arguments:
  {list,command}

options:
  -h, --help        show this help message and exit

required arguments:
  -k API_KEY        API key received from Electrolux
  -t ACCESS_TOKEN   Access token received from Electrolux
  -r REFRESH_TOKEN  Refresh token received from Electrolux
```

#### Sending commands
Commands to be sent must a proper JSON. You can use the `list` command to find keys that will be accepted by the appliance.

For example, to change the fan speed for an air purifier you can use the following commands:
```
poetry run python3 src/cli.py -k $API_KEY -t $ACCESS_TOKEN -r $REFRESH_TOKEN command -d $APPLIANCE_ID -c '{"Workmode": "Manual"}'
poetry run python3 src/cli.py -k $API_KEY -t $ACCESS_TOKEN -r $REFRESH_TOKEN command -d $APPLIANCE_ID -c '{"Fanspeed": 3}'
```
and to switch it to automatic mode you can use
```
poetry run python3 src/cli.py -k $API_KEY -t $ACCESS_TOKEN -r $REFRESH_TOKEN command -d $APPLIANCE_ID -c '{"Workmode": "Auto"}'
```

### Disclaimer
This client is not officially supported by Electrolux Group. It is a community project, and it is not guaranteed to be up-to-date with the latest changes in the API.
