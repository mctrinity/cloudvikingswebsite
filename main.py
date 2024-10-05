import requests
from flask import Flask, render_template
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv(dotenv_path='.env')

# Get the API key and clan tag from the .env file
API_KEY = os.getenv('API_KEY')
CLAN_TAG = os.getenv('CLAN_TAG')


# Function to get clan data from the Clash of Clans API
def get_clan_data():
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    # Debugging: Print the Authorization header to verify
    print(f"Authorization Header Sent: {headers}")

    # Make the API request
    response = requests.get(f"https://api.clashofclans.com/v1/clans/{CLAN_TAG.replace('#', '%23')}", headers=headers)

    # Debugging: Print the response details
    print(f"API Status Code: {response.status_code}")
    print(f"API Response: {response.text}")

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching clan data: {response.status_code}")
        return {}



# Route to display members of the clan
@app.route('/members')
def members():
    clan_data = get_clan_data()
    if 'memberList' in clan_data:
        members = clan_data['memberList']
    else:
        members = []  # If there's an error, show an empty list

    return render_template('members.html', members=members, page="members")

# Other routes (home, about, events, etc.)
@app.route('/')
def home():
    return render_template('index.html', page="home")

@app.route('/about')
def about():
    return render_template('about.html', page="about")

@app.route('/events')
def events():
    return render_template('events.html', page="events")

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
