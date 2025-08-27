# Strava Weekly Activity Tracker

A Python script that fetches your Strava activities and generates a line graph showing your total moving time per week over a specified period. The script excludes strength training activities and focuses on cardio/endurance activities.

## Features

- 🔐 **OAuth Authentication**: Secure authentication with Strava API
- 📊 **Weekly Visualization**: Line graph showing moving time per week
- 🚫 **Smart Filtering**: Automatically excludes strength training activities
- ⚡ **Fast Data Retrieval**: Uses curl commands for efficient API calls
- 📅 **Flexible Time Periods**: Specify any number of weeks to analyze

## Prerequisites

- Python 3.6 or higher
- `matplotlib` library
- A Strava account
- A Strava API application

## Installation

1. **Clone or download this project**

2. **Install required dependencies:**
   ```bash
   pip install matplotlib
   ```

3. **Set up your Strava API application:**
   - Go to [Strava API Settings](https://www.strava.com/settings/api)
   - Click "Create App"
   - Fill in the required information:
     - **Application Name**: Your choice (e.g., "Weekly Activity Tracker")
     - **Category**: Your choice
     - **Club**: Leave blank
     - **Website**: Can be localhost or any URL
     - **Application Description**: Brief description
     - **Authorization Callback Domain**: `localhost`
   - Note down your **Client ID** and **Client Secret**

## Authentication Setup

### Step 1: Create Keys File

1. **Copy the example keys file:**
   ```bash
   cp keys.py.example keys.py
   ```

2. **Edit `keys.py` with your Strava app credentials:**
   ```python
   # Strava App Credentials - Get these from https://www.strava.com/settings/api
   CLIENT_ID = "YOUR_CLIENT_ID_HERE"        # Replace with your Client ID
   CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE" # Replace with your Client Secret
   
   # Strava API Access Token - Will be filled after OAuth process
   STRAVA_API_TOKEN = "YOUR_ACCESS_TOKEN_HERE"
   ```

   **⚠️ Important**: The `keys.py` file contains sensitive credentials and is automatically ignored by git.

### Step 2: Authenticate with Strava

1. **Run the OAuth authentication:**
   ```bash
   python strava_oauth.py
   ```

2. **Follow the authentication process:**
   - A browser window will open automatically
   - Log in to Strava if prompted
   - **IMPORTANT**: Make sure to check "View data about your activities" permission
   - Click "Authorize"
   - The script will automatically capture your authorization and exchange it for an access token

3. **Update your keys file:**
   - The script will display your access token
   - Copy the token value (just the long string, not the variable name)
   - Edit `keys.py` and replace `"YOUR_ACCESS_TOKEN_HERE"` with your actual token:
     ```python
     STRAVA_API_TOKEN = "your_actual_token_here"
     ```

## Usage

Run the script with the number of weeks you want to analyze:

```bash
python strava_weekly_stats.py <number_of_weeks>
```

### Examples

```bash
# Analyze last 4 weeks
python strava_weekly_stats.py 4

# Analyze last 12 weeks (3 months)
python strava_weekly_stats.py 12

# Analyze last 26 weeks (6 months)
python strava_weekly_stats.py 26
```

## What Gets Tracked

### ✅ Included Activities
- Running
- Cycling/Biking
- Rowing
- Swimming
- Hiking
- All cardio/endurance activities

### ❌ Excluded Activities
- Weight Training
- Strength Training
- Workout (generic)

## Output

The script generates:

1. **Console Output:**
   ```
   Fetching activities from 2025-07-30 to 2025-08-27
   Found 40 total activities
   After filtering: 31 activities
   ```

2. **Interactive Graph:**
   - Line chart with data points
   - Weekly moving time in hours
   - Week labels (MM/DD format)
   - Total hours summary
   - Strava orange color scheme

## Files Included

- **`strava_weekly_stats.py`** - Main script that generates the weekly activity graph
- **`strava_oauth.py`** - OAuth authentication helper script
- **`keys.py.example`** - Example keys file template
- **`keys.py`** - Your actual keys file (created by you, ignored by git)
- **`strava_tokens.json`** - Generated file containing your API tokens (created after authentication)
- **`.gitignore`** - Ensures sensitive files are not committed to version control

## Troubleshooting

### Authentication Issues

**Problem**: "Error: keys.py file not found!"

**Solution**: 
1. Copy the example file: `cp keys.py.example keys.py`
2. Edit `keys.py` with your actual credentials

**Problem**: "Authorization Error - activity:read_permission missing"

**Solution**: 
1. Go to [Strava Apps Settings](https://www.strava.com/settings/apps)
2. Find your app and click "Revoke Access"
3. Re-run `python strava_oauth.py`
4. Make sure to check "View data about your activities" during authorization

### No Data Displayed

**Problem**: Graph shows no data or "No activities found"

**Possible causes:**
- Token doesn't have proper permissions (see above)
- No activities in the specified time period
- All activities are strength training (which are filtered out)

### OAuth Browser Issues

**Problem**: Browser doesn't open automatically

**Solution**: 
- Copy the authorization URL from the console output
- Paste it manually in your browser
- Complete the authorization process
- Copy the authorization code from the redirected URL

## Token Management

- **Access tokens expire every 6 hours**
- **Refresh tokens last longer** and can be used to get new access tokens
- The `strava_tokens.json` file contains both tokens for future use
- If your token expires, re-run the OAuth process

## Privacy & Security

- **All sensitive credentials are stored in `keys.py`** (automatically git-ignored)
- **Tokens are stored locally** in `strava_tokens.json` (also git-ignored)
- **The script only requests read access** to your activities
- **No data is transmitted** outside of Strava's official API
- **Git safety**: `.gitignore` prevents accidental commits of sensitive data

## API Limits

Strava has the following API limits:
- **200 requests per 15 minutes**
- **2,000 requests per day**

This script is designed to be efficient and should rarely hit these limits for personal use.