import asyncio
import ssl

import aiohttp
import certifi

from pyelectroluxgroup.api import ElectroluxHubAPI
from pyelectroluxgroup.auth import Auth


async def main():
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    conn = aiohttp.TCPConnector(ssl=ssl_context)

    async with aiohttp.ClientSession(connector=conn) as session:
        api_key = ""
        access_token = ""

        auth = Auth(session, "https://api.developer.electrolux.one/api/v1", access_token, api_key)
        hub = ElectroluxHubAPI(auth)
        appliances = await hub.async_get_appliances()

        for appliance in appliances:
            print("Appliance ID", appliance.id)
            print("Appliance name", appliance.name)
            
        print("HTTP response JSON content", appliances)


if __name__ == '__main__':
    asyncio.run(main())
