from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mail import Mail, Message
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

# Email Configuration (Gmail)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Your Gmail address from .env
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Your Gmail app password from .env
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# Secret key for flash messages
app.secret_key = 'your_secret_key'

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

    # Initialize default values in case data is not present
    clan_name = clan_data.get('name', 'Unknown Clan')
    clan_level = clan_data.get('clanLevel', 'N/A')
    clan_points = clan_data.get('clanPoints', 'N/A')
    cwl_rank = clan_data.get('warLeague', {}).get('name', 'N/A')
    capital_hall_level = clan_data.get('clanCapital', {}).get('capitalHallLevel', 'N/A')
    member_count = len(clan_data.get('memberList', []))  # Get the count of members in the list

    return render_template(
        'index.html',
        clan_name=clan_name,
        clan_level=clan_level,
        clan_points=clan_points,
        cwl_rank=cwl_rank,
        capital_hall_level=capital_hall_level,
        member_count=member_count,
        current_year=current_year,
        page="home"
    )


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


# Route to handle form submission from the "Drop Us a Line" form
@app.route('/contact', methods=['POST'])
def contact():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    # Compose email
    msg = Message(subject=f"Message from {name}",
                  sender=app.config.get('MAIL_USERNAME'),
                  recipients=[app.config.get('MAIL_USERNAME')],  # Your Gmail address
                  body=f"From: {name} <{email}>\n\nMessage:\n{message}")

    try:
        mail.send(msg)
        flash('Your message has been sent successfully!', 'success')
    except Exception as e:
        flash(f'An error occurred while sending the message: {str(e)}', 'danger')

    return redirect(url_for('home'))


# Widgets route (existing route)
@app.route('/widgets')
def widgets():
    return render_template('widgets.html')


if __name__ == '__main__':
    app.run(debug=True)
