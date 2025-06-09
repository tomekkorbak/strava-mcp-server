# Strava MCP Server

![Python Package](https://github.com/tomekkorbak/strava-mcp-server/workflows/Python%20Package/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/install-mcp?name=strava&config=eyJjb21tYW5kIjoidXZ4IHN0cmF2YS1tY3Atc2VydmVyIiwiZW52Ijp7IlNUUkFWQV9DTElFTlRfSUQiOiJZT1VSX0NMSUVOVF9JRCIsIlNUUkFWQV9DTElFTlRfU0VDUkVUIjoiWU9VUl9DTElFTlRfU0VDUkVUIiwiU1RSQVZBX1JFRlJFU0hfVE9LRU4iOiJZT1VSX1JFRlJFU0hfVE9LRU4ifX0%3D)

A [Model Context Protocol](https://modelcontextprotocol.io/introduction) (MCP) server that provides access to the Strava API. It allows language models to query athlete activities data from the Strava API.

## Available Tools

The server exposes the following tools:

### Activities Queries

- `get_activities(limit: int = 10)`: Get the authenticated athlete's recent activities (includes lap data)
- `get_activities_by_date_range(start_date: str, end_date: str, limit: int = 30)`: Get activities within a specific date range (includes lap data)
- `get_activity_by_id(activity_id: int)`: Get detailed information about a specific activity (includes lap data)
- `get_recent_activities(days: int = 7, limit: int = 10)`: Get activities from the past X days (includes lap data)
- `get_activity_laps(activity_id: int)`: Get laps for a specific activity
- `get_activity_streams(activity_id: int, keys: str)`: Get detailed time-series data (GPS coordinates, heart rate, power, cadence, altitude, etc.) for a specific activity
- `get_activity_zones(activity_id: int)`: Get heart rate and power zone distribution data for a specific activity

Dates should be provided in ISO format (`YYYY-MM-DD`).

## Activity Data Format

The server returns activity data with consistent field names and units:

| Field | Description | Unit |
|-------|-------------|------|
| `name` | Activity name | - |
| `sport_type` | Type of sport | - |
| `start_date` | Start date and time | ISO 8601 |
| `distance_metres` | Distance | meters |
| `elapsed_time_seconds` | Total elapsed time | seconds |
| `moving_time_seconds` | Moving time | seconds |
| `average_speed_mps` | Average speed | meters per second |
| `max_speed_mps` | Maximum speed | meters per second |
| `total_elevation_gain_metres` | Total elevation gain | meters |
| `elev_high_metres` | Highest elevation | meters |
| `elev_low_metres` | Lowest elevation | meters |
| `calories` | Calories burned | kcal |
| `start_latlng` | Start coordinates | [lat, lng] |
| `end_latlng` | End coordinates | [lat, lng] |

## Authentication

To use this server, you'll need to authenticate with the Strava API. Follow these steps:

1. Create a Strava API application:
   - Go to [Strava API Settings](https://www.strava.com/settings/api)
   - Create an application to get your Client ID and Client Secret
   - Set the Authorization Callback Domain to `localhost`

2. Get your refresh token:
   - Use the included `get_strava_token.py` script:
   ```bash
   python get_strava_token.py
   ```
   - Follow the prompts to authorize your application
   - The script will save your tokens to a `.env` file

3. Set environment variables:
   The server requires the following environment variables:
   - `STRAVA_CLIENT_ID`: Your Strava API Client ID
   - `STRAVA_CLIENT_SECRET`: Your Strava API Client Secret
   - `STRAVA_REFRESH_TOKEN`: Your Strava API Refresh Token

## Installation

To set up the Strava MCP Server locally, run the following commands:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
```

## Usage

### Claude for Desktop

Update your `claude_desktop_config.json` (located in `~/Library/Application\ Support/Claude/claude_desktop_config.json` on macOS and `%APPDATA%/Claude/claude_desktop_config.json` on Windows) to include the following:

```json
{
    "mcpServers": {
        "strava": {
            "command": "/path/to/your/venv/bin/strava-mcp-server",
            "args": [],
            "env": {
                "STRAVA_CLIENT_ID": "YOUR_CLIENT_ID",
                "STRAVA_CLIENT_SECRET": "YOUR_CLIENT_SECRET",
                "STRAVA_REFRESH_TOKEN": "YOUR_REFRESH_TOKEN"
            }
        }
    }
}
```

- `command`: Path to your installed `strava-mcp-server` executable (update as needed for your environment)
- `STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET`, `STRAVA_REFRESH_TOKEN`: Replace with your own Strava API credentials

### Claude Web

For Claude Web, you can run the server locally and connect it using the MCP extension.

## Example Queries

Once connected, you can ask Claude questions like:

- "What are my recent activities?"
- "Show me my activities from last week"
- "What was my longest run in the past month?"
- "Get details about my latest cycling activity"
- "Get the GPS track and heart rate data for activity 12345"
- "Show me the power zones for my last bike ride"
- "Get detailed streams data for my morning run"
- "Analyze the elevation profile of my latest hike"

## Error Handling

The server provides human-readable error messages for common issues:

- Invalid date formats
- API authentication errors
- Network connectivity problems

## License

This project is licensed under the MIT License - see the LICENSE file for details.