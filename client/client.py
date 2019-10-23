"""Defines a class for managing connection to Opsman

Environtment Variables:
    OPSMAN_CLIENT_ID (str): Client ID to programmatically use with client.
    OPSMAN_CLIENT_SECRET (str): Client Secret to programmatically use with client.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""
import os
import json
import getpass
import logging
from typing import Dict, Any

import requests
from oauth2_client.credentials_manager import ServiceInformation, CredentialManager, OAuthError


class OpsmanClient(CredentialManager):
    """Object for managing OpsMan API calls.

    Attributes:
        base_url (str): The base url of the OpsManager the client is pointed to. Includes the proto.
        api_url (str): The api url of the OpsManager the client is pointed to. Includes the proto.
    """
    def __init__(self, url: str, ssl_verify: [str, bool], proto: str = 'https://',
                 proxies: Dict[str, str] = None, interactive: bool = False):
        """Define a base object

        Args:
            url (str): opsman url without the protocol.
            ssl_verify (str, bool): path to certs or False.
            proto (str, optional): Protocol to use; defaults to https://.
            proxies (dict, optional): The proxies to use when making oauth calls. Defaults to None.
            interactive (bool, optional): If the client will be used in an interactive shell.
                Defaults to False.
        """
        # Setup inital session
        self.base_url = f'{proto}{url}'
        self.api_url = f'{self.base_url}/api/v0'
        self.__session = requests.Session()
        self.__session.verify = ssl_verify
        self.__session.headers.update({'Accept': 'application/json'})

        if 'OPSMAN_CLIENT_ID' not in os.environ and not interactive:
            raise NameError('Environment variable, OPSMAN_CLIENT_ID, is not set.')
        self.client_id = os.getenv('OPSMAN_CLIENT_ID')
        if not self.client_id:
            self.client_id = input(f"Opsman Client ID: ")

        # Get Token
        authorize_url = f'{self.base_url}/oauth/authorize'
        login_url = f'{self.base_url}/uaa/oauth/token'
        if 'OPSMAN_CLIENT_SECRET' not in os.environ:
            if not interactive:
                raise NameError('Environment variable, OPSMAN_CLIENT_SECRET, is not set.')
            else:
                service_info = ServiceInformation(authorize_url, login_url,
                                                  self.client_id,
                                                  getpass.getpass(f"Opsman Client Secret: "),
                                                  [], ssl_verify)
                super(OpsmanClient, self).__init__(service_info, proxies=proxies)
        else:
            service_info = ServiceInformation(authorize_url, login_url,
                                              self.client_id,
                                              os.getenv('OPSMAN_CLIENT_SECRET'),
                                              [], ssl_verify)
            super(OpsmanClient, self).__init__(service_info, proxies=proxies)
        try:
            self.init_with_client_credentials()
            self.__session.headers.update({
                'Authorization': f"bearer {self._access_token}"
            })
        except requests.exceptions.ConnectionError as err:
            raise ValueError(f'Unable to reach the provided url: {login_url}')
        except OAuthError as err:
            raise ValueError(err)

    def _make_api_call(self, verb: str, uri: str, headers: Dict[str, Any] = None,
                       params: Dict[str, Any] = None, payload: Dict[str, Any] = None
                       ) -> Dict[str, Any]:
        """Internal function for calling Opsman.

        This internal function is written more to provide a mechanism for making api calls that have
        yet to be implemented as client functions.

        Args:
            verb (str): The API verb to use.
            uri (str): Opsman uri to call; /api/<version> should not be included.
            headers (dict, optional): Additional headers to be included in the call.
            params (dict, optional): Any URL-encoded params to include in the call.
            payload (dict, optional): The json payload to include in the call.

        Returns:
            A dict containing the body of the response.
        """
        res = self.__session.request(verb.upper(), url=f'{self.api_url}{uri}',
                                     headers=headers,
                                     params=params,
                                     data=json.dumps(payload))
        logging.debug('%r', res)
        body = res.json()
        return body

    def get_info(self):
        """Get OpsMan api info.

        Returns:
            A dict containing the opsman api info.

        Notes:
            https://docs.pivotal.io/pivotalcf/2-2/opsman-api/#info

        """
        uri = '/info'
        return self._make_api_call('GET', uri)
