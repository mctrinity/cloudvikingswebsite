from flask import Flask, render_template
import os
import requests
from dotenv import load_dotenv
from flask_caching import Cache
from datetime import datetime  # Import datetime module

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv(dotenv_path='.env')

# Cache configuration (using simple cache for development)
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # Cache timeout in seconds (5 minutes)
cache = Cache(app)

# Get the API key and clan tag from the .env file
API_KEY = os.getenv('API_KEY')
CLAN_TAG = os.getenv('CLAN_TAG')


# Function to get clan data from the Clash of Clans API
@cache.cached(timeout=300, key_prefix='clan_data')
def get_clan_data():
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    # Make the API request
    response = requests.get(f"https://api.clashofclans.com/v1/clans/{CLAN_TAG.replace('#', '%23')}", headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching clan data: {response.status_code}")
        return {}


# Route for the home page
@app.route('/')
def home():
    current_year = datetime.now().year  # Get current year
    clan_data = get_clan_data()
    if 'name' in clan_data:
        clan_name = clan_data['name']
        clan_level = clan_data['clanLevel']
        clan_points = clan_data['clanPoints']
    else:
        clan_name = "Unknown Clan"
        clan_level = "N/A"
        clan_points = "N/A"

    return render_template('index.html', clan_name=clan_name, clan_level=clan_level, clan_points=clan_points, current_year=current_year, page="home")


# Route to display members of the clan
@app.route('/members')
def members():
    current_year = datetime.now().year  # Get current year
    clan_data = get_clan_data()
    if 'memberList' in clan_data:
        members = clan_data['memberList']
    else:
        members = []  # If there's an error, show an empty list

    return render_template('members.html', members=members, current_year=current_year, page="members")


if __name__ == '__main__':
    app.run(debug=True)