import requests
import json
from typing import Optional, Dict, Any
import os
from datetime import datetime, timedelta

class ICD11Client:
    """
    A client for interacting with the WHO ICD-11 API.
    """
    
    def __init__(self, client_id: str = None, client_secret: str = None):
        """
        Initialize the ICD-11 client.
        
        Args:
            client_id (str): The client ID for the ICD-11 API
            client_secret (str): The client secret for the ICD-11 API
        """
        self.client_id = client_id or os.getenv('ICD11_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('ICD11_CLIENT_SECRET')
        self.base_url = "https://id.who.int/icd"
        self.token_url = "https://icdaccessmanagement.who.int/connect/token"
        self.access_token = None
        self.token_expires_at = None
    
    def _get_access_token(self) -> str:
            """
            Get an access token for the ICD-11 API using client credentials.
            
            Returns:
                str: The access token
            """
            # Check if we already have a valid token
            if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
                return self.access_token
            
            # Request a new token
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'icdapi_access',
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            # Set expiration time (with a small buffer)
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            
            return self.access_token
    
    def _make_request(self, url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
            """
            Make an authenticated request to the ICD-11 API.
            
            Args:
                url (str): The URL to request
                params (dict): Query parameters
                
            Returns:
                dict: The JSON response
            """
            token = self._get_access_token()
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json',
                'Accept-Language': 'en',
                'API-Version': 'v2'
            }
            
            response = requests.get(url, headers=headers, params=params or {})
            response.raise_for_status()
            
            return response.json()
    
    def search_entities(self, query: str, language: str = 'en') -> Dict[str, Any]:
        """
        Search for ICD-11 entities.
        
        Args:
            query (str): The search query
            language (str): The language for the search (default: 'en')
            
        Returns:
            dict: The search results
        """
        url = f"{self.base_url}/entity/search"
        params = {
            'q': query,
            'language': language
        }
        
        return self._make_request(url, params)
    
    def get_entity_by_id(self, entity_id: str, language: str = 'en') -> Dict[str, Any]:
            """
            Get detailed information about a specific ICD-11 entity by ID.
            
            Args:
                entity_id (str): The ID of the entity
                language (str): The language for the response (default: 'en')
                
            Returns:
                dict: The entity details
            """
            url = f"{self.base_url}/entity/{entity_id}"
            params = {'language': language}
            
            return self._make_request(url, params)
    
    def get_linearization_entity(self, linearization: str, code: str, language: str = 'en') -> Dict[str, Any]:
            """
            Get information about a specific linearization entity by code.
            
            Args:
                linearization (str): The linearization name (e.g., 'mms')
                code (str): The entity code
                language (str): The language for the response (default: 'en')
                
            Returns:
                dict: The entity details
            """
            url = f"{self.base_url}/{linearization}/{code}"
            params = {'language': language}
            
            return self._make_request(url, params)
