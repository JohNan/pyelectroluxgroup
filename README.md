# Work in progress

## Electrolux Group API Client
This is a Python client for the Electrolux Group API. It is a simple wrapper around the API, which allows you to interact with the API in a more Pythonic way.

### Installation
Use `poetry install --extras cli` to install dependencies for CLI and the library itself.

### Usage
```bash
usage: cli.py [-h] -k API_KEY -t ACCESS_TOKEN -r REFRESH_TOKEN {list,command} ...

positional arguments:
  {login,list,command}

options:
  -h, --help        show this help message and exit
```

#### Authentication
Before being able to use the CLI, you'll need to provide access token, refresh token and API key.
All of these can be obtained using the [developer dashboard](https://developer.electrolux.one/dashboard).

To store credentials locally, use the `login` command:
```
poetry run python3 src/cli.py login -k $API_KEY -t $ACCESS_TOKEN -r $REFRESH_TOKEN
```

#### Listing devices
To list all devices, use the `list` command:
```
poetry run python3 src/cli.py list
```

#### Sending commands
Commands to be sent must be proper JSON.
You can use the `list` command described above to find appliance IDs and commands that will be accepted by the appliance.

For example, to change the fan speed for an air purifier you can use the following commands:
```
poetry run python3 src/cli.py command -d $APPLIANCE_ID -c '{"Workmode": "Manual"}'
poetry run python3 src/cli.py command -d $APPLIANCE_ID -c '{"Fanspeed": 3}'
```

and to switch it to automatic mode you can use
```
poetry run python3 src/cli.py command -d $APPLIANCE_ID -c '{"Workmode": "Auto"}'
```

### Disclaimer
This client is not officially supported by Electrolux Group. It is a community project, and it is not guaranteed to be up-to-date with the latest changes in the API.
