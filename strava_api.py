#!/usr/bin/env python3
"""
Strava API Client

This script fetches data from the Strava API, formats it as nice JSON, and prints it.
"""

import os
import json
import time
import requests
from typing import Any, Optional
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.json import JSON
from rich.table import Table
from rich import print as rprint


@dataclass
class StravaConfig:
    """Configuration for Strava API authentication."""
    client_id: str
    client_secret: str
    refresh_token: str
    access_token: Optional[str] = None
    expires_at: Optional[int] = None


class StravaClient:
    """Client for interacting with the Strava API."""
    
    BASE_URL = "https://www.strava.com/api/v3"
    
    def __init__(self, config: StravaConfig):
        """Initialize the Strava client with configuration."""
        self.config = config
        self._ensure_valid_token()
    
    def _ensure_valid_token(self) -> None:
        """Ensure we have a valid access token, refreshing if necessary."""
        current_time = int(time.time())
        
        # If token is missing or expired, refresh it
        if (not self.config.access_token or 
                not self.config.expires_at or 
                current_time >= self.config.expires_at):
            self._refresh_token()
    
    def _refresh_token(self) -> None:
        """Refresh the access token using the refresh token."""
        refresh_url = "https://www.strava.com/oauth/token"
        payload = {
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'refresh_token': self.config.refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(refresh_url, data=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to refresh token: {response.text}")
        
        token_data = response.json()
        self.config.access_token = token_data['access_token']
        self.config.expires_at = token_data['expires_at']
        rprint("[bold green]Token refreshed successfully[/bold green]")
    
    def _make_request(self, endpoint: str, params: Optional[dict] = None) -> Any:
        """Make an authenticated request to the Strava API."""
        self._ensure_valid_token()
        
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.config.access_token}"}
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.text}")
        
        return response.json()
    
    def get_athlete(self) -> dict:
        """Get the authenticated athlete's profile."""
        return self._make_request("athlete")
    
    def get_activities(self, limit: int = 10) -> list:
        """Get the authenticated athlete's activities."""
        params = {"per_page": limit}
        activities = self._make_request("athlete/activities", params)
        return self._filter_activities(activities)
    
    def get_activity(self, activity_id: int) -> dict:
        """Get detailed information about a specific activity."""
        activity = self._make_request(f"activities/{activity_id}")
        return self._filter_activity(activity)
    
    def get_stats(self) -> dict:
        """Get the authenticated athlete's stats."""
        athlete = self.get_athlete()
        return self._make_request(f"athletes/{athlete['id']}/stats")
    
    def get_routes(self, limit: int = 10) -> list:
        """Get the authenticated athlete's routes."""
        params = {"per_page": limit}
        return self._make_request("athlete/routes", params)
    
    def get_segments(self, activity_id: int) -> list:
        """Get segments for a specific activity."""
        activity = self._make_request(f"activities/{activity_id}")
        if 'segment_efforts' in activity:
            return activity['segment_efforts']
        return []
    
    def _filter_activity(self, activity: dict) -> dict:
        """Filter activity to only include specific keys and rename with units."""
        # Define field mappings with units
        field_mappings = {
            'calories': 'calories',
            'distance': 'distance_metres',
            'elapsed_time': 'elapsed_time_seconds',
            'elev_high': 'elev_high_metres',
            'elev_low': 'elev_low_metres',
            'end_latlng': 'end_latlng',
            'average_speed': 'average_speed_mps',  # metres per second
            'max_speed': 'max_speed_mps',  # metres per second
            'moving_time': 'moving_time_seconds',
            'sport_type': 'sport_type',
            'start_date': 'start_date',
            'start_latlng': 'start_latlng',
            'total_elevation_gain': 'total_elevation_gain_metres',
            'name': 'name'  # Keep name for display purposes
        }
        
        # Create a new dictionary with renamed fields
        filtered_activity = {}
        for old_key, new_key in field_mappings.items():
            if old_key in activity:
                filtered_activity[new_key] = activity[old_key]
        
        return filtered_activity
    
    def _filter_activities(self, activities: list) -> list:
        """Filter a list of activities to only include specific keys with units."""
        return [self._filter_activity(activity) for activity in activities]


def pretty_print_json(data: Any, title: str = None) -> None:
    """Print data as nicely formatted JSON using Rich."""
    console = Console()
    
    if title:
        console.print(Panel(f"[bold cyan]{title}[/bold cyan]", border_style="cyan"))
    
    if isinstance(data, (list, dict)):
        # Convert to JSON string and then to Rich JSON object for pretty printing
        json_str = json.dumps(data, indent=2, sort_keys=True)
        rich_json = JSON(json_str)
        console.print(rich_json)
    else:
        # For non-JSON data, just print it
        console.print(data)


def print_activities_table(activities: list) -> None:
    """Print activities as a formatted table."""
    console = Console()
    
    table = Table(title="Recent Activities", show_header=True, header_style="bold magenta")
    table.add_column("Date", style="dim")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Distance (km)", justify="right")
    table.add_column("Duration", justify="right")
    table.add_column("Elevation (m)", justify="right")
    table.add_column("Calories", justify="right")
    table.add_column("Avg Speed (km/h)", justify="right")
    
    for activity in activities:
        # Format date
        start_date = datetime.fromisoformat(activity['start_date'].replace('Z', '+00:00'))
        date_str = start_date.strftime("%Y-%m-%d %H:%M")
        
        # Format duration (seconds to HH:MM:SS)
        seconds = int(activity['elapsed_time_seconds'])
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Format distance (metres to kilometers)
        distance = f"{activity['distance_metres'] / 1000:.2f}"
        
        # Format elevation
        elevation = f"{activity.get('total_elevation_gain_metres', 0):.0f}"
        
        # Format calories
        calories = str(activity.get('calories', 'N/A'))
        
        # Format average speed (m/s to km/h)
        avg_speed_mps = activity.get('average_speed_mps', 0)
        avg_speed_kmh = f"{avg_speed_mps * 3.6:.1f}"  # Convert m/s to km/h
        
        # Get sport type
        sport_type = activity.get('sport_type', 'Unknown')
        
        table.add_row(
            date_str,
            activity.get('name', 'Unnamed Activity'),
            sport_type,
            distance,
            duration,
            elevation,
            calories,
            avg_speed_kmh
        )
    
    console.print(table)


def save_json_to_file(data: Any, filename: str) -> None:
    """Save data to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, sort_keys=True)
    rprint(f"[bold blue]Data saved to [/bold blue][italic]{filename}[/italic]")


def load_config() -> StravaConfig:
    """Load Strava API configuration from environment variables."""
    load_dotenv()  # Load environment variables from .env file
    
    required_vars = ['STRAVA_CLIENT_ID', 'STRAVA_CLIENT_SECRET', 'STRAVA_REFRESH_TOKEN']
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return StravaConfig(
        client_id=os.environ['STRAVA_CLIENT_ID'],
        client_secret=os.environ['STRAVA_CLIENT_SECRET'],
        refresh_token=os.environ['STRAVA_REFRESH_TOKEN'],
        access_token=os.environ.get('STRAVA_ACCESS_TOKEN'),
        expires_at=int(os.environ.get('STRAVA_EXPIRES_AT', 0)) or None
    )


def print_athlete_summary(athlete: dict) -> None:
    """Print a summary of the athlete profile."""
    console = Console()
    
    panel = Panel.fit(
        f"[bold]{athlete['firstname']} {athlete['lastname']}[/bold]\n"
        f"[cyan]Username:[/cyan] {athlete['username']}\n"
        f"[cyan]Location:[/cyan] {athlete.get('city', 'N/A')}, {athlete.get('country', 'N/A')}\n"
        f"[cyan]Following:[/cyan] {athlete['friend_count']} | [cyan]Followers:[/cyan] {athlete['follower_count']}\n"
        f"[cyan]Activities:[/cyan] {athlete.get('total_activity_count', 'N/A')}\n",
        title="[bold cyan]Athlete Profile[/bold cyan]",
        border_style="cyan"
    )
    
    console.print(panel)


def main():
    """Main function to demonstrate Strava API usage."""
    try:
        console = Console()
        console.print(Panel("[bold cyan]Strava API Client[/bold cyan]", border_style="cyan"))
        
        config = load_config()
        client = StravaClient(config)
        
        # Get athlete profile
        console.print("\n[bold cyan]Fetching athlete profile...[/bold cyan]")
        athlete = client.get_athlete()
        print_athlete_summary(athlete)
        save_json_to_file(athlete, "strava_athlete.json")
        
        # Get recent activities
        console.print("\n[bold cyan]Fetching recent activities...[/bold cyan]")
        activities = client.get_activities(limit=5)
        print_activities_table(activities)
        save_json_to_file(activities, "strava_activities.json")
        
        if activities:
            # Get the ID from the original API response before filtering
            activity_id = None
            for idx, activity in enumerate(activities):
                if idx == 0:  # Get the first activity
                    # Extract ID from the name to use for fetching details
                    activity_name = activity.get('name', '')
                    console.print(f"\n[bold cyan]Fetching details for activity: {activity_name}[/bold cyan]")
                    
                    # Use the original API to get the ID
                    original_activities = client._make_request("athlete/activities", {"per_page": 1})
                    if original_activities:
                        activity_id = original_activities[0]['id']
            
            if activity_id:
                activity_details = client.get_activity(activity_id)
                pretty_print_json(activity_details, "Latest Activity Details")
                save_json_to_file(activity_details, "strava_latest_activity.json")
        
        # Get athlete stats
        console.print("\n[bold cyan]Fetching athlete stats...[/bold cyan]")
        stats = client.get_stats()
        pretty_print_json(stats, "Athlete Stats")
        save_json_to_file(stats, "strava_stats.json")
    
        console.print("\n[bold green]All data fetched and saved successfully![/bold green]")
        
    except Exception as e:
        rprint(f"[bold red]Error:[/bold red] {e}")


if __name__ == "__main__":
    main() 