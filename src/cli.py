import argparse
import asyncio
import ssl

import aiohttp
import certifi

from pyelectroluxgroup.api import ElectroluxHubAPI
from pyelectroluxgroup.auth import Auth


async def main():
    parser = argparse.ArgumentParser()
    required_argument = parser.add_argument_group('required arguments')
    required_argument.add_argument('-k', dest='api_key',
                                   help='API key received from Electrolux',
                                   required=True)
    required_argument.add_argument('-t', dest='access_token',
                                   required=True)
    required_argument.add_argument('-r', dest='refresh_token',
                                   required=True)

    args = parser.parse_args()

    ssl_context = ssl.create_default_context(cafile=certifi.where())
    conn = aiohttp.TCPConnector(ssl=ssl_context)

    api_key = args.api_key
    access_token = args.access_token
    refresh_token = args.refresh_token

    async with aiohttp.ClientSession(connector=conn) as session:
        hub = ElectroluxHubAPI(session, access_token, refresh_token, api_key)
        appliances = await hub.async_get_appliances()

        for appliance in appliances:
            print("Appliance ID", appliance.id)
            print("Appliance name", appliance.name)

            await appliance.async_update()
            print(" -- Serial number", appliance.serial_number)
            print(" -- Brand", appliance.brand)
            print(" -- Model", appliance.model)
            print(" -- Device Type", appliance.device_type)


if __name__ == '__main__':
    asyncio.run(main())
