#!/usr/bin/env python3

import argparse
import subprocess
import json
import datetime
from collections import defaultdict
import matplotlib.pyplot as plt

# Import API token from keys module
try:
    from keys import STRAVA_API_TOKEN
except ImportError:
    print("Error: keys.py file not found!")
    print("Please create a keys.py file with your Strava API access token.")
    print("See README.md for setup instructions.")
    exit(1)

def make_strava_request(endpoint):
    """Make a curl request to Strava API and return parsed JSON response"""
    url = f"https://www.strava.com/api/v3{endpoint}"
    
    cmd = [
        'curl',
        '-H', f'Authorization: Bearer {STRAVA_API_TOKEN}',
        '-s',  # Silent mode
        url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error making API request: {e}")
        print(f"Response: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Raw response: {result.stdout}")
        return None

def get_activities_in_date_range(start_date, end_date):
    """Fetch all activities between start_date and end_date"""
    activities = []
    page = 1
    per_page = 200
    
    # Convert dates to epoch timestamps
    start_epoch = int(start_date.timestamp())
    end_epoch = int(end_date.timestamp())
    
    while True:
        endpoint = f"/athlete/activities?before={end_epoch}&after={start_epoch}&page={page}&per_page={per_page}"
        response = make_strava_request(endpoint)
        
        if not response:
            break
        
        # Check for API errors
        if isinstance(response, dict) and 'errors' in response:
            print(f"API Error: {response.get('message', 'Unknown error')}")
            if 'errors' in response:
                for error in response['errors']:
                    print(f"  - {error.get('resource', '')}: {error.get('code', '')}")
            return []
        
        # Must be a list of activities
        if not isinstance(response, list) or len(response) == 0:
            break
            
        activities.extend(response)
        
        if len(response) < per_page:
            break
            
        page += 1
    
    return activities

def filter_activities(activities):
    """Filter out strength training activities and return relevant data"""
    filtered_activities = []
    
    for activity in activities:
        # Skip strength training activities
        if activity.get('type', '').lower() in ['weighttraining', 'workout']:
            continue
            
        filtered_activities.append({
            'start_date': activity['start_date'],
            'moving_time': activity.get('moving_time', 0),  # in seconds
            'type': activity.get('type', 'Unknown')
        })
    
    return filtered_activities

def group_by_week(activities):
    """Group activities by week and sum moving times"""
    weekly_data = defaultdict(int)
    
    for activity in activities:
        # Parse start date
        start_date = datetime.datetime.fromisoformat(activity['start_date'].replace('Z', '+00:00'))
        
        # Get the Monday of the week (ISO week)
        monday = start_date - datetime.timedelta(days=start_date.weekday())
        week_key = monday.strftime('%Y-%m-%d')
        
        # Add moving time (convert from seconds to hours)
        weekly_data[week_key] += activity['moving_time'] / 3600.0
    
    return weekly_data

def create_graph(weekly_data, num_weeks):
    """Create and display a line chart of weekly moving time"""
    if not weekly_data:
        print("No data to display")
        return
    
    # Sort by date
    sorted_weeks = sorted(weekly_data.items())
    
    # Take only the last num_weeks
    if len(sorted_weeks) > num_weeks:
        sorted_weeks = sorted_weeks[-num_weeks:]
    
    weeks = [item[0] for item in sorted_weeks]
    times = [item[1] for item in sorted_weeks]
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    plt.plot(range(len(weeks)), times, marker='o', linewidth=2, markersize=6, color='#FC4C02')  # Strava orange
    
    # Customize the plot
    plt.title(f'Weekly Moving Time - Last {num_weeks} Weeks', fontsize=16, fontweight='bold')
    plt.xlabel('Week Starting (Monday)', fontsize=12)
    plt.ylabel('Moving Time (Hours)', fontsize=12)
    
    # Format x-axis labels
    plt.xticks(range(len(weeks)), [datetime.datetime.strptime(w, '%Y-%m-%d').strftime('%m/%d') for w in weeks], 
               rotation=45, ha='right')
    
    # Add value labels on points
    for i, time in enumerate(times):
        plt.annotate(f'{time:.1f}h', (i, time), textcoords="offset points", 
                    xytext=(0,10), ha='center', fontsize=9)
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Show total hours
    total_hours = sum(times)
    plt.figtext(0.02, 0.02, f'Total: {total_hours:.1f} hours', fontsize=10, style='italic')
    
    plt.show()

def main():
    parser = argparse.ArgumentParser(description='Graph weekly moving time from Strava activities')
    parser.add_argument('weeks', type=int, help='Number of weeks to analyze')
    args = parser.parse_args()
    
    if args.weeks <= 0:
        print("Number of weeks must be positive")
        return
    
    # Calculate date range
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(weeks=args.weeks)
    
    print(f"Fetching activities from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Fetch activities
    activities = get_activities_in_date_range(start_date, end_date)
    if not activities:
        print("No activities found or error fetching data")
        return
    
    print(f"Found {len(activities)} total activities")
    
    # Filter activities (exclude strength training)
    filtered_activities = filter_activities(activities)
    print(f"After filtering: {len(filtered_activities)} activities")
    
    # Group by week
    weekly_data = group_by_week(filtered_activities)
    
    # Create graph
    create_graph(weekly_data, args.weeks)

if __name__ == "__main__":
    main()