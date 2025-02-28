#!/usr/bin/env python3
"""
Strava Token Helper

This script helps you get a refresh token for the Strava API.
"""

import os
import sys
from typing import Any

import requests  # type: ignore
from dotenv import load_dotenv


def print_auth_url(client_id: str) -> None:
    """
    Print the authorization URL for the user to visit.

    Args:
        client_id: The Strava API client ID
    """
    auth_url = (
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri=http://localhost"
        f"&response_type=code"
        f"&scope=read,activity:read,activity:read_all,profile:read_all"
    )

    print("\n=== Step 1: Visit the following URL in your browser ===")
    print(auth_url)
    print("\nAuthorize the application when prompted.")
    print("You'll be redirected to a URL like: http://localhost/?state=&code=AUTHORIZATION_CODE&scope=...")
    print("Copy the 'code' parameter value from the URL.\n")


def exchange_code_for_token(client_id: str, client_secret: str, auth_code: str) -> dict[str, Any]:
    """
    Exchange the authorization code for tokens.

    Args:
        client_id: The Strava API client ID
        client_secret: The Strava API client secret
        auth_code: The authorization code from the redirect URL

    Returns:
        dictionary containing token data (access_token, refresh_token, expires_at)

    Raises:
        SystemExit: If the token exchange fails
    """
    token_url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code,
        'grant_type': 'authorization_code'
    }

    try:
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        return dict(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error exchanging code for token: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        sys.exit(1)


def update_env_file(token_data: dict[str, Any]) -> None:
    """
    Update the .env file with the token data.

    Args:
        token_data: dictionary containing token data (access_token, refresh_token, expires_at)
    """
    env_file = ".env"

    # Read existing .env file if it exists
    env_vars: dict[str, str] = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value

    # Update with new token data
    env_vars['STRAVA_REFRESH_TOKEN'] = token_data['refresh_token']
    env_vars['STRAVA_ACCESS_TOKEN'] = token_data['access_token']
    env_vars['STRAVA_EXPIRES_AT'] = str(token_data['expires_at'])

    # Write back to .env file
    with open(env_file, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")

    print(f"Updated {env_file} with new token data")


def main() -> None:
    """Main function to guide the user through the token acquisition process."""
    load_dotenv()

    print("=== Strava API Token Helper ===")

    # Get client ID and secret
    client_id = os.environ.get('STRAVA_CLIENT_ID')
    client_secret = os.environ.get('STRAVA_CLIENT_SECRET')

    if not client_id or not client_secret:
        print("Please provide your Strava API credentials:")
        client_id = input("Client ID: ").strip()
        client_secret = input("Client Secret: ").strip()

        # Save to .env file
        with open(".env", 'w') as f:
            f.write(f"STRAVA_CLIENT_ID={client_id}\n")
            f.write(f"STRAVA_CLIENT_SECRET={client_secret}\n")

        print("Saved credentials to .env file")

    # Print authorization URL
    print_auth_url(client_id)

    # Get authorization code from user
    auth_code = input("Enter the authorization code from the URL: ").strip()

    # Exchange code for token
    print("\n=== Step 2: Exchanging code for token ===")
    token_data = exchange_code_for_token(client_id, client_secret, auth_code)

    # Print token information
    print("\n=== Token Information ===")
    print(f"Access Token: {token_data['access_token'][:10]}...")
    print(f"Refresh Token: {token_data['refresh_token'][:10]}...")
    print(f"Expires At: {token_data['expires_at']} (Unix timestamp)")

    # Update .env file
    update_env_file(token_data)

    print("\n=== Success! ===")
    print("You can now run the strava-mcp-server to access your Strava data.")


if __name__ == "__main__":
    main()
