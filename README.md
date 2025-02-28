# Strava MCP Server

![Python Package](https://github.com/tomekkorbak/strava-mcp-server/workflows/Python%20Package/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)

A [Model Context Protocol](https://modelcontextprotocol.io/introduction) (MCP) server that provides access to the Strava API. It allows language models to query athlete activities data from the Strava API.

## Available Tools

The server exposes the following tools:

### Activities Queries

- `get_activities(limit: int = 10)`: Get the authenticated athlete's recent activities
- `get_activities_by_date_range(start_date: str, end_date: str, limit: int = 30)`: Get activities within a specific date range
- `get_activity_by_id(activity_id: int)`: Get detailed information about a specific activity
- `get_recent_activities(days: int = 7, limit: int = 10)`: Get activities from the past X days

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

## Usage

### Claude for Desktop

Update your `claude_desktop_config.json` (located in `~/Library/Application\ Support/Claude/claude_desktop_config.json` on macOS and `%APPDATA%/Claude/claude_desktop_config.json` on Windows) to include the following:

```json
{
    "mcpServers": {
        "strava": {
            "command": "uvx",
            "args": [
                "strava-mcp-server"
            ],
            "env": {
                "STRAVA_CLIENT_ID": "YOUR_CLIENT_ID",
                "STRAVA_CLIENT_SECRET": "YOUR_CLIENT_SECRET",
                "STRAVA_REFRESH_TOKEN": "YOUR_REFRESH_TOKEN"
            }
        }
    }
}
```

### Claude Web

For Claude Web, you can run the server locally and connect it using the MCP extension.

## Example Queries

Once connected, you can ask Claude questions like:

- "What are my recent activities?"
- "Show me my activities from last week"
- "What was my longest run in the past month?"
- "Get details about my latest cycling activity"

## Error Handling

The server provides human-readable error messages for common issues:

- Invalid date formats
- API authentication errors
- Network connectivity problems

## License

This project is licensed under the MIT License - see the LICENSE file for details.
