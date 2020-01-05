from typing import Union
from urllib.error import HTTPError

import requests
from user_agent import generate_user_agent

from ..repeater import repeater


class BaseApiClient:
    """
        API client. Get request to API endpoint.
    """
    def __init__(self, endpoint: str, params: dict):
        self.endpoint = endpoint
        self.params = params
        self.headers = {
            'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux'))
        }
        self.response_type = 'json'

    @repeater()
    def execute_request(self) -> Union[dict, str]:
        """Get data from endpoint"""
        try:
            resp = requests.get(
                url=self.endpoint,
                params=self.params,
                headers=self.headers,
                timeout=30
            )
            print(f'{resp.status_code}: {resp.url}')
        except HTTPError as e:
            print(f'Error on url {self.endpoint}: {e}')
        except requests.ReadTimeout as e:
            print(f'Error on url {self.endpoint}: {e}')
        else:
            return resp.json() if self.response_type == 'json' else resp.text


class BaseModel:
    def save(self):
        pass
