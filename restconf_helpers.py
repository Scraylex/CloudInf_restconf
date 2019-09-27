import logging
from enum import Enum
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger('restconf.restconf_helpers')


class RestconfFormat(Enum):
    XML = 1
    JSON = 2


class RestconfRequestHelper:
    headers_json = {'Content-Type': 'application/yang-data+json',
                    'Accept': 'application/yang-data+json, application/yang-data.errors+json'}

    headers_xml = {'Content-Type': 'application/yang-data+xml',
                   'Accept': 'application/yang-data+xml, application/yang-data.errors+xml'}

    def get(self, url: str, username: str, password: str,
            restconf_format: Optional[RestconfFormat] = RestconfFormat.XML,
            headers: Optional[Dict[str, str]] = None,
            **kwargs: Dict[Any, Any]) -> str:
        """Executes a get request to the specified url and adds RESTCONF specific headers.
        Raises an exception if the request fails

        Parameters:
            url: url which should be requested
            username: the username for the authentication
            password: the password for the authentication
            restconf_format: which restconf headers should be set. (default RestconfFormat.XML)
            headers: which additional headers should be set (default None)
            kwargs: additional parameters for the request

        Returns:
            str: The text of the response
        """

        logger.debug(f'GET request to {url}')
        request_headers = self.get_headers(restconf_format, headers)
        print(request_headers)
        response = requests.request(method='GET', auth=(username, password),
                                    headers=request_headers,
                                    url=url,
                                    verify=False,
                                    **kwargs)
        logger.debug(f'Got response from {url} with code {response.status_code} and content \n {response.text}')
        response.raise_for_status()
        return response.text

    def get_headers(self, format: RestconfFormat, headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        """Adds restconf specific headers to a dict
        Parameters:
            restconf: which restconf headers should be set
            headers: which additional headers should be set
        Returns:
            dict: The
        """
        restconf_headers = self.headers_json if format == RestconfFormat.JSON else self.headers_xml
        if headers and isinstance(headers, dict):
            return dict(headers, **restconf_headers)
        return dict(restconf_headers)
