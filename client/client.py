"""Defines a class for managing connection to Opsman

Environtment Variables:
    OPSMAN_CLIENT_ID (str): Client ID to programmatically use with client
    OPSMAN_CLIENT_SECRET (str): Client Secret to programmatically use with client

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""
import os
import sys
import getpass
import logging
from typing import Dict, Any, List

import requests
from oauth2_client.credentials_manager import ServiceInformation, CredentialManager


class OpsmanClient(CredentialManager):
    """Object for storing opsman auth info"""
    def __init__(self, url: str, ssl_verify: [str, bool],
                proxies: Dict[str, str] = dict(http='', https=''), interactive: bool = False):
        """Define a base object

        Args:
            url (str): opsman url without the protocol
            ssl_verify (str, bool): path to certs or False
        """
        # Setup inital session
        self.url = url
        self.api_url = f'https://{url}/api/v0'
        self.session = requests.Session()
        self.session.verify = ssl_verify
        self.session.headers.update({'Accept': 'application/json'})

        if 'OPSMAN_CLIENT_ID' not in os.environ and not interactive:
            raise NameError('Environment variable, OPSMAN_CLIENT_ID, is not set.')
        self.client_id = os.getenv('OPSMAN_CLIENT_ID')
        if not self.client_id:
            self.client_id = input(f"Opsman Client ID: ")

        # Get Token
        authorize_url = f'https://{self.url}/oauth/authorize'
        login_url = f'https://{self.url}/uaa/oauth/token'
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
        self.init_with_client_credentials()
        # res = self.session.post(login_url, params=params, headers={
        #     'Content-Type': 'application/x-www-form-urlencoded',
        #     'Host': f'login.{self.sys_url}'
        # })
        # logging.debug("Response from %s: %r\n%r", login_url, res, res.text)
        # self.oauth = res.json()
        self.session.headers.update({
            'Authorization': f"bearer {self._access_token}"
        })

    def get_info(self):
        """Get OpsMan api info"""
        uri = '/info'
        res = self.session.get(f'{self.api_url}{uri}')
        logging.debug('%r', res)
        body = res.json()
        return body
