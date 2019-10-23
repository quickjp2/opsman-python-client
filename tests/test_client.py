"""Test the OpsMan client"""
# import os
# import json
# import getpass
# import logging
# from typing import Dict, Any

import pytest
# import requests
# from oauth2_client.credentials_manager import ServiceInformation, CredentialManager

from client.client import OpsmanClient

class TestClientInit:
    def test_requires_OPSMAN_CLIENT_ID_by_default(self):
        with pytest.raises(NameError):
            OpsmanClient('sample_url', False)
    def test_requires_OPSMAN_CLIENT_SECRET_by_default(self, monkeypatch):
        monkeypatch.setenv('OPSMAN_CLIENT_ID', 'test')
        with pytest.raises(NameError):
            OpsmanClient('sample_url', False)
