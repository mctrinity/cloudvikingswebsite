from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_mail import Mail, Message
from email_validator import validate_email, EmailNotValidError  # Import email validation
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
app.secret_key = os.urandom(24)

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
    current_year = datetime.now().year
    clan_data = get_clan_data()
    # Initialize default values
    clan_name = clan_data.get('name', 'Unknown Clan')
    clan_level = clan_data.get('clanLevel', 'N/A')
    clan_points = clan_data.get('clanPoints', 'N/A')
    cwl_rank = clan_data.get('warLeague', {}).get('name', 'N/A')
    capital_hall_level = clan_data.get('clanCapital', {}).get('capitalHallLevel', 'N/A')
    member_count = len(clan_data.get('memberList', []))

    return render_template(
        'index.html',
        clan_name=clan_name,
        clan_level=clan_level,
        clan_points=clan_points,
        cwl_rank=cwl_rank,
        capital_hall_level=capital_hall_level,
        member_count=member_count,
        current_year=current_year,
        page="home"  # Specify "home" for this page
    )


# Route to display members of the clan
@app.route('/members')
def members():
    current_year = datetime.now().year
    clan_data = get_clan_data()
    members = clan_data.get('memberList', [])

    return render_template('members.html', members=members, current_year=current_year, page="members")


# Route to handle form submission from the "Drop Us a Line" form
@app.route('/contact', methods=['POST'])
def contact():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    # Server-side email and domain validation
    try:
        valid = validate_email(email, check_deliverability=True)
        email = valid.email
    except EmailNotValidError as e:
        return jsonify({"status": "error", "message": f"Invalid email: {str(e)}"})

    # Compose email
    msg = Message(subject=f"Cloud Vikings - Message from {name}",
                  sender=app.config.get('MAIL_USERNAME'),
                  recipients=[app.config.get('MAIL_USERNAME')],
                  body=f"From: {name} <{email}>\n\nMessage:\n{message}")

    try:
        mail.send(msg)
        return jsonify({"status": "success", "message": "Your message has been sent successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"An error occurred while sending the message: {str(e)}"})


# Widgets route
@app.route('/widgets')
def widgets():
    open_weather_api_key = os.getenv("OPEN_WEATHER_API_KEY")
    bing_news_api_key = os.getenv("BING_NEWS_API_KEY")  # Updated API key
    tmdb_api_key = os.getenv("TMDB_API_KEY")

    user_ip = request.remote_addr  # Get user's IP address
    ip_info = get_ip_info(user_ip)

    # Fetch trending movies data
    trending_movies = get_trending_movies()

    return render_template(
        'widgets.html',
        openweather_api_key=open_weather_api_key,
        bing_news_api_key=bing_news_api_key,  # Pass Bing API key
        tmdb_api_key=tmdb_api_key,
        trending_movies=trending_movies,
        ip_info=ip_info,
        page="infohub"
    )


# Refresh IP Info
# @cache.cached(timeout=300, key_prefix='ip_info')
def get_ip_info(ip_address):
    ipinfo_api_key = os.getenv("IPINFO_API_KEY")
    url = f"https://ipinfo.io/{ip_address}?token={ipinfo_api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print("IP Info Retrieved:", data)  # Debug: Print IP info to console
        return data  # Return IP data if successful
    except requests.exceptions.RequestException as e:
        print(f"Error fetching IP info: {e}")
        return {
            "ip": ip_address,
            "city": "Unavailable",
            "region": "Unavailable",
            "country": "Unavailable",
            "loc": "Unavailable"
        }

# IP Look-up route
@app.route('/ip_lookup', methods=['POST'])
def ip_lookup():
    input_ip = request.form.get('input_ip')
    ip_info = get_ip_info(input_ip)  # Fetch location info for the entered IP address

    # Return JSON response instead of rendering a template
    return jsonify(ip_info)

# Refresh trending movies
@cache.cached(timeout=14400, key_prefix='trending_movies')  # Cache for 4 hours
def get_trending_movies():
    tmdb_api_key = os.getenv("TMDB_API_KEY")
    trending_url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={tmdb_api_key}"

    try:
        response = requests.get(trending_url)
        response.raise_for_status()  # Raise an error if the request failed
        return response.json()  # Return the JSON data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching trending movies: {e}")
        return {}  # Return an empty dict if there's an error
    
# For testing only, clear cache
@app.route('/clear_cache')
def clear_cache():
    cache.clear()
    return "Cache cleared!"

# Route to get the ISS location with caching
# Default cache timeout
CACHE_TIMEOUT = 30  # 30 seconds

@app.route('/iss-location')
@cache.cached(timeout=CACHE_TIMEOUT, key_prefix='iss_location')
def iss_location():
    global CACHE_TIMEOUT  # Allow dynamic adjustment of cache timeout
    iss_api_url = "http://api.open-notify.org/iss-now.json"

    try:
        # Fetch ISS location from the Open Notify API
        response = requests.get(iss_api_url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()
        iss_position = data.get("iss_position", {})
        latitude = iss_position.get("latitude", "Unavailable")
        longitude = iss_position.get("longitude", "Unavailable")
        timestamp = data.get("timestamp", "Unavailable")

        # Log the successful fetch
        app.logger.info(f"Fetched ISS Location: lat={latitude}, long={longitude}, time={timestamp}")

        # Reset cache timeout if successful
        CACHE_TIMEOUT = 30  # Reset to a short timeout for frequent updates

        return jsonify({
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": timestamp
        })

    except requests.exceptions.HTTPError as e:
        if response.status_code == 429:  # Rate limit error
            app.logger.warning("Rate limit exceeded. Increasing cache timeout.")
            CACHE_TIMEOUT = min(CACHE_TIMEOUT * 2, 3600)  # Double the timeout up to 1 hour
            return jsonify({
                "latitude": "Unavailable",
                "longitude": "Unavailable",
                "timestamp": "Unavailable",
                "error": "Rate limit exceeded. Please try again later."
            }), 429

        # Handle other HTTP errors
        app.logger.error(f"HTTP Error: {e}")
        return jsonify({
            "latitude": "Unavailable",
            "longitude": "Unavailable",
            "timestamp": "Unavailable",
            "error": f"HTTP Error: {e}"
        }), response.status_code

    except requests.exceptions.RequestException as e:
        # Handle generic request errors
        app.logger.error(f"Request Exception: {e}")
        return jsonify({
            "latitude": "Unavailable",
            "longitude": "Unavailable",
            "timestamp": "Unavailable",
            "error": f"Request Error: {e}"
        }), 500



if __name__ == '__main__':
    app.run(debug=True)
