import argparse
import asyncio
import json
import logging
import ssl

import aiohttp
import certifi

from pyelectroluxgroup.api import ElectroluxHubAPI
from pyelectroluxgroup.token_managers.filesystem import TokenManagerFileSystem

logging.basicConfig(level=logging.DEBUG)

async def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    login_parser = subparsers.add_parser("login")
    required_argument = login_parser.add_argument_group("required arguments")
    required_argument.add_argument(
        "-k", dest="api_key", help="API key received from Electrolux", required=True
    )
    required_argument.add_argument(
        "-t",
        dest="access_token",
        help="Access token received from Electrolux",
        required=True,
    )
    required_argument.add_argument(
        "-r",
        dest="refresh_token",
        help="Refresh token received from Electrolux",
        required=True,
    )

    _list_parser = subparsers.add_parser("list")

    command_parser = subparsers.add_parser("command")
    command_parser.add_argument(
        "-d", dest="appliance_id", help="ID of the target device", required=True
    )
    command_parser.add_argument(
        "-c",
        dest="command",
        help="Command that should be sent to the device",
        required=True,
    )

    args = parser.parse_args()

    ssl_context = ssl.create_default_context(cafile=certifi.where())
    conn = aiohttp.TCPConnector(ssl=ssl_context)

    token_manager = TokenManagerFileSystem()

    if args.cmd == "login":
        token_manager.update(args.access_token, args.refresh_token, args.api_key)
        return

    try:
        token_manager.load()
    except FileNotFoundError:
        print("You have to run the 'login' command first")
        return

    async with aiohttp.ClientSession(connector=conn) as session:
        hub = ElectroluxHubAPI(session, token_manager)
        appliances = await hub.async_get_appliances()

        if args.cmd == "list":
            for appliance in appliances:
                print(f"Appliance ID: {appliance.id}")
                print(f"Appliance name: {appliance.name}")
                print(f"Appliance type: {appliance.type}")

                await appliance.async_update()
                print(f" -- Serial number: {appliance.serial_number}")
                print(f" -- Brand: {appliance.brand}")
                print(f" -- Model: {appliance.model}")
                print(f" -- Device Type: {appliance.device_type}")
                print(" -- State --")
                for k, v in appliance.state.items():
                    print(f" ---- {k}: {v}")

        if args.cmd == "command":
            try:
                appliance = next(
                    filter(lambda x: x.id == args.appliance_id, appliances)
                )

                await appliance.send_command(json.loads(args.command))
            except StopIteration:
                print(f"Appliance with ID {args.appliance_id} was not found")


if __name__ == "__main__":
    asyncio.run(main())
