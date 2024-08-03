from typing import List


from pyelectroluxgroup.appliance import Appliance
from pyelectroluxgroup.auth import Auth


class ElectroluxHubAPI:
    """Class to communicate with the ExampleHub API."""

    def __init__(self, auth: Auth):
        """Initialize the API and store the auth so we can make requests."""
        self.auth = auth

    async def async_get_appliances(self) -> List[Appliance]:
        """Return the lights."""
        resp = await self.auth.request("get", "appliances")
        resp.raise_for_status()
        return [Appliance(appliance_data, self.auth) for appliance_data in await resp.json()]