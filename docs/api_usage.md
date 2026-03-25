# API Usage Guide

This documentation provides an overview of how to interact with the Electrolux Group API using the `pyelectroluxgroup` client, including standard polling methods and the live stream API (Server-Sent Events) for real-time updates.

## Initializing the Client

First, create an authenticated `ElectroluxHubAPI` instance:

```python
import aiohttp
from pyelectroluxgroup.api import ElectroluxHubAPI
from pyelectroluxgroup.token_manager import TokenManager

# Use your own logic to persist or provide tokens
token_manager = TokenManager(
    access_token="<your_access_token>",
    refresh_token="<your_refresh_token>",
    api_key="<your_api_key>"
)

async def main():
    async with aiohttp.ClientSession() as session:
        api = ElectroluxHubAPI(session, token_manager)

        # Do something with the api here
```

## Standard API (Polling)

The standard API allows you to fetch lists of appliances and query their state directly. Note that polling too frequently is discouraged; you should use the Live Stream API for real-time state changes instead.

### Listing Appliances

```python
appliances = await api.async_get_appliances()
for appliance in appliances:
    print(f"Appliance ID: {appliance.id}, Name: {appliance.name}")
```

### Getting Appliance State and Sending Commands

```python
# Fetch basic info and state
appliance = await api.async_get_appliance("<appliance_id>")
await appliance.async_update()

print(f"Current State: {appliance.state}")

# Send a command to the appliance
command = {"Workmode": "Auto"}
await appliance.send_command(command)
```

## Live Stream API (Server-Sent Events)

The Live Stream API is the recommended way to get real-time state changes from your appliances. Instead of polling, you establish a long-lived connection that yields changes as they happen.

The `watch_appliances` method handles the underlying Server-Sent Events (SSE) connection automatically. It also includes built-in retry logic: if the connection drops or the token expires, it will sleep briefly, refresh the token if needed, and attempt to reconnect.

### Using the Live Stream

```python
import asyncio

async def listen_for_changes(api: ElectroluxHubAPI):
    print("Connecting to live stream...")

    # This async generator will run indefinitely and yield events as they occur
    async for event in api.watch_appliances():
        # Event looks like: {"applianceId": "123", "property": "Fanspeed", "value": 3}
        appliance_id = event.get("applianceId")
        property_name = event.get("property")
        value = event.get("value")

        print(f"[{appliance_id}] {property_name} changed to {value}")

async def main():
    async with aiohttp.ClientSession() as session:
        api = ElectroluxHubAPI(session, token_manager)

        # Run the listener as a background task
        listener_task = asyncio.create_task(listen_for_changes(api))

        # Keep the application running or await the task (it runs indefinitely)
        await listener_task
```

### Note on Reconnection

The `watch_appliances()` method wraps the EventSource listener in an infinite loop (`while True`). If an expected error occurs (such as an auth failure or a dropped connection), it catches the exception, logs a warning/error, waits 5 seconds, and then tries to connect again using a fresh token.

If you are integrating this into a larger system (like Home Assistant), you can simply consume the async generator and trust that the client will attempt to keep the stream alive.
