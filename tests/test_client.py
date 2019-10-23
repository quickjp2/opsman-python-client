"""Test the OpsMan client"""
import os
# import json
# import getpass
# import logging
# from typing import Dict, Any

import pytest
# import requests
# from oauth2_client.credentials_manager import ServiceInformation, CredentialManager

from client.client import OpsmanClient

class TestClientInit:
    def test_requires_OPSMAN_CLIENT_ID_by_default(self, monkeypatch):
        monkeypatch.delenv('OPSMAN_CLIENT_ID')
        monkeypatch.delenv('OPSMAN_CLIENT_SECRET')
        with pytest.raises(NameError):
            OpsmanClient('sample_url', False)
    def test_requires_OPSMAN_CLIENT_SECRET_by_default(self, monkeypatch):
        monkeypatch.delenv('OPSMAN_CLIENT_SECRET')
        with pytest.raises(NameError):
            OpsmanClient('sample_url', False)
    def test_raise_value_error_with_bad_url(self):
        with pytest.raises(ValueError):
            OpsmanClient('sample_url', False)
    def test_raise_value_error_with_bad_creds(self, monkeypatch):
        monkeypatch.setenv('OPSMAN_CLIENT_ID', 'test')
        monkeypatch.setenv('OPSMAN_CLIENT_SECRET', 'test')
        with pytest.raises(ValueError):
            OpsmanClient(os.getenv('OPSMAN_URL'), False)
    def test_interactive_client_secret(self, monkeypatch):
        monkeypatch.delenv('OPSMAN_CLIENT_SECRET')
        monkeypatch.setattr('builtins.input', lambda: os.getenv('OPSMAN_CLIENT_SECRET'))
        test_client = OpsmanClient(os.getenv('OPSMAN_URL'), False, interactive=True)
        assert test_client.client_id == os.getenv('OPSMAN_CLIENT_ID')

class TestInternalAPICaller:
    def test_info_method(self):
        test_client = OpsmanClient(os.getenv('OPSMAN_URL'), False)
        info = test_client.get_info()
        assert isinstance(info, dict)
        assert 'info' in info
