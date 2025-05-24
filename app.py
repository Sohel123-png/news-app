from flask import Flask, request, jsonify, render_template # Added render_template
import psycopg2
import os # For potential environment variable usage for db credentials
from datetime import date, datetime # For date validation

app = Flask(__name__) # Flask app is initialized correctly

# Assuming static and template folders are in the same directory as app.py
# Flask automatically configures this if 'templates' and 'static' directories exist at the root.

# --- Configuration via Environment Variables ---
# For database connection
DB_HOST_ENV = os.environ.get('DB_HOST', 'localhost')
DB_PORT_ENV = os.environ.get('DB_PORT', '5432')
DB_USER_ENV = os.environ.get('DB_USER', 'your_db_user') # Changed default
DB_PASSWORD_ENV = os.environ.get('DB_PASSWORD', 'your_db_password') # Changed default
DB_NAME_ENV = os.environ.get('DB_NAME', 'fitgent_db')

# For News API (if used, e.g., in the news_feed route)
NEWS_API_KEY_ENV = os.environ.get('NEWS_API_KEY', 'your_default_news_api_key_here_or_empty')
# Note: The News API key is defined here but not currently used in active code.
# It would be used if the news_feed() function were to fetch news from newsapi.org.

def get_db_connection():
    """Establishes a connection to the PostgreSQL database using environment variables."""
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME_ENV,
            user=DB_USER_ENV,
            password=DB_PASSWORD_ENV,
            host=DB_HOST_ENV,
            port=DB_PORT_ENV
        )
    except psycopg2.OperationalError as e:
        # This error is common if the database server is not running or accessible
        print(f"Error connecting to database: {e}. Check if PostgreSQL is running and accessible.")
    except psycopg2.Error as e:
        print(f"General database connection error: {e}")
    return conn

def validate_date_format(date_str):
    """Validates if the date string is in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

@app.route('/api/health-data', methods=['POST'])
def receive_health_data():
    """
    Receives health data from a smartwatch, validates it, and stores it in the database.
    """
    if not request.is_json:
        return jsonify({"error": "Invalid request: Content-Type must be application/json"}), 400

    data = request.get_json()

    # Validate required fields
    required_fields = ['user_id', 'date', 'steps', 'sleep_hours', 'heart_rate_avg', 'stress_score', 'calories_burned']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Basic data type and format validation
    try:
        user_id = int(data['user_id'])
        date_str = str(data['date'])
        if not validate_date_format(date_str):
             return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400
        steps = int(data['steps'])
        sleep_hours = float(data['sleep_hours'])
        heart_rate_avg = float(data['heart_rate_avg'])
        stress_score = int(data['stress_score']) # Assuming stress_score is an integer
        calories_burned = float(data['calories_burned'])
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid data type for one or more fields: {e}"}), 400
    
    # Further validation (e.g., range checks)
    if user_id <= 0:
        return jsonify({"error": "user_id must be a positive integer."}), 400
    if steps < 0 :
        return jsonify({"error": "steps cannot be negative."}), 400
    if sleep_hours < 0:
        return jsonify({"error": "sleep_hours cannot be negative."}), 400
    if heart_rate_avg < 0:
         return jsonify({"error": "heart_rate_avg cannot be negative."}), 400
    if not (0 <= stress_score <= 100): # Assuming stress score is within a defined range
         return jsonify({"error": "stress_score must be between 0 and 100 (inclusive)."}), 400
    if calories_burned < 0:
        return jsonify({"error": "calories_burned cannot be negative."}), 400


    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            # Specific error for db connection failure
            return jsonify({"error": "Failed to connect to the database. Please ensure the database server is running and accessible."}), 503 # Service Unavailable

        cur = conn.cursor()
        insert_query = """
        INSERT INTO user_health_data 
            (user_id, date, steps, sleep_hours, heart_rate_avg, stress_score, calories_burned)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        cur.execute(insert_query, (
            user_id, date_str, steps, sleep_hours, heart_rate_avg, stress_score, calories_burned
        ))
        conn.commit()
        cur.close()
        return jsonify({"message": "Health data successfully received and stored."}), 201

    except psycopg2.Error as e:
        # Log the detailed error on the server
        print(f"Database operational error: {e}")
        # Check for specific error codes if needed, e.g., unique constraint violation
        # For now, a generic error is returned to the client for database issues.
        return jsonify({"error": "A database error occurred while storing the data."}), 500
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected server error occurred: {e}")
        return jsonify({"error": "An unexpected server error occurred."}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # Ensure PostgreSQL service is running.
    # For development, run this directly.
    # For production, use a WSGI server like Gunicorn: gunicorn -w 4 -b 0.0.0.0:5000 app:app
    print("Starting Flask app...")

    # Import the suggestion function
    from health_suggestions import get_health_suggestions
    # Import the food recommendation function
    from food_recommender import get_food_recommendation
    # Import Google Fit integration functions
    import google_fit_integration as gfit # Using an alias for brevity
    # Import Notification Manager functions
    from notification_manager import check_notification_triggers

    # Check initial DB connection to provide early feedback if DB is down
    initial_conn = get_db_connection()
    if initial_conn:
        print("Successfully connected to database on startup.")
        initial_conn.close()
    else:
        print("CRITICAL: Could not connect to database on startup. Ensure PostgreSQL is running and configured.")
        # Optionally, exit if DB connection is critical for startup:
        # import sys
        # sys.exit("Exiting due to database connection failure.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)


@app.route('/api/health-suggestions', methods=['POST'])
def get_suggestions_api():
    """
    API endpoint to get health suggestions for a user based on their latest health data.
    Expects a JSON payload with 'user_id'.
    """
    if not request.is_json:
        return jsonify({"error": "Invalid request: Content-Type must be application/json"}), 400

    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "Missing 'user_id' in request body"}), 400
    
    try:
        user_id = int(user_id)
        if user_id <= 0:
            return jsonify({"error": "user_id must be a positive integer."}), 400
    except ValueError:
        return jsonify({"error": "Invalid user_id format. Must be an integer."}), 400

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Failed to connect to the database."}), 503

        cur = conn.cursor()
        # Fetch the most recent health data entry for the user
        # Orders by date descending, then by a primary key or unique timestamp if date is not enough
        # Assuming 'date' column is sufficient for "latest" for now.
        # If multiple entries can exist for the same date, add another ordering column (e.g., an auto-incrementing ID or a timestamp column)
        # For this example, we'll assume 'date' is sufficient for defining "latest".
        # A more robust way would be to have an 'entry_timestamp' or an auto-incrementing 'id'
        # and order by that DESC.
        # Let's assume the table has an implicit row ordering or we fetch based on the latest 'date'.
        # For this example, we fetch the record with the most recent 'date'.
        # Note: The table schema in the previous subtask did not specify a primary key or a timestamp
        # for unique ordering of records on the same day. We will assume the latest by date is sufficient.
        
        # Query to fetch the latest health data for the user
        # The columns are: user_id, date, steps, sleep_hours, heart_rate_avg, stress_score, calories_burned
        fetch_query = """
        SELECT steps, sleep_hours, heart_rate_avg, stress_score, calories_burned
        FROM user_health_data
        WHERE user_id = %s
        ORDER BY date DESC
        LIMIT 1;
        """
        cur.execute(fetch_query, (user_id,))
        latest_health_data_row = cur.fetchone()
        cur.close()

        if not latest_health_data_row:
            return jsonify({"message": f"No health data found for user_id {user_id}."}), 404

        # Column names must match what get_health_suggestions expects
        health_data_dict = {
            'steps': latest_health_data_row[0],
            'sleep_hours': latest_health_data_row[1],
            'heart_rate_avg': latest_health_data_row[2],
            'stress_score': latest_health_data_row[3],
            'calories_burned': latest_health_data_row[4]
        }
        
        suggestions = get_health_suggestions(health_data_dict)
        return jsonify({"user_id": user_id, "suggestions": suggestions}), 200

    except psycopg2.Error as e:
        print(f"Database error in /api/health-suggestions: {e}")
        return jsonify({"error": "A database error occurred while fetching health data."}), 500
    except Exception as e:
        print(f"Unexpected error in /api/health-suggestions: {e}")
        return jsonify({"error": "An unexpected server error occurred."}), 500
    finally:
        if conn:
            conn.close()


@app.route('/api/food-recommendation', methods=['POST'])
def food_recommendation_api():
    """
    API endpoint to get food recommendations based on activity and time of day.
    Expects a JSON payload with 'user_id', 'steps', 'calories_burned', and 'time_of_day'.
    """
    if not request.is_json:
        return jsonify({"error": "Invalid request: Content-Type must be application/json"}), 400

    data = request.get_json()
    
    # Validate required fields
    required_fields = ['user_id', 'steps', 'calories_burned', 'time_of_day']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    try:
        user_id = int(data['user_id'])
        steps = int(data['steps'])
        calories_burned = float(data['calories_burned'])
        time_of_day = str(data['time_of_day']).strip().lower()
        
        if user_id <= 0:
            return jsonify({"error": "user_id must be a positive integer."}), 400
        if steps < 0:
            return jsonify({"error": "steps cannot be negative."}), 400
        if calories_burned < 0:
            return jsonify({"error": "calories_burned cannot be negative."}), 400
        if not time_of_day: # Check for empty string
             return jsonify({"error": "time_of_day cannot be empty."}), 400
        # Basic validation for time_of_day, could be more strict (e.g., enum)
        allowed_times = ["morning", "afternoon", "evening"]
        if time_of_day not in allowed_times:
            return jsonify({"error": f"Invalid time_of_day. Allowed values are: {', '.join(allowed_times)}."}), 400

    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid data type for one or more fields: {e}"}), 400

    try:
        recommendation = get_food_recommendation(steps, calories_burned, time_of_day)
        return jsonify({
            "user_id": user_id,
            "recommendation": recommendation
        }), 200
    except Exception as e:
        # Log the error for debugging
        print(f"Error in food recommendation logic: {e}")
        return jsonify({"error": "An unexpected error occurred while generating food recommendation."}), 500

# Route for the News Feed page (previously index.html at root)
@app.route('/')
def news_feed():
    # Assuming 'index.html' is the news feed page and is now in the 'templates' folder
    # If this page were to fetch news dynamically, it would use NEWS_API_KEY_ENV
    # Example:
    # if NEWS_API_KEY_ENV and NEWS_API_KEY_ENV != 'your_default_news_api_key_here_or_empty':
    #     # news_data = fetch_news_from_api(NEWS_API_KEY_ENV) # Hypothetical function
    #     # return render_template('index.html', news=news_data)
    # else:
    #     # return render_template('index.html', news_error="News API key not configured.")
    return render_template('index.html')

# Route for the Health Dashboard
@app.route('/dashboard')
def health_dashboard_view():
    # This route serves the health_dashboard.html page.
    # For now, it serves static content. Dynamic data can be passed later.
    # Example placeholder data (can be expanded or fetched from DB in future tasks)
    dashboard_data = {
        "sleep_avg": "7.5 hours",
        "activity_level": "Moderate",
        "food_orders": "3 meals tracked",
        "wellness_score": "78/100",
        "badges": [
            {"name": "Morning Mover", "img": "https://via.placeholder.com/80?text=Morning"},
            {"name": "Step Star", "img": "https://via.placeholder.com/80?text=Steps"}
        ]
    }
    return render_template('health_dashboard.html', data=dashboard_data)

# --- Google Fit Integration Endpoints ---

@app.route('/connect/google-fit', methods=['GET'])
def connect_google_fit():
    """
    Initiates the OAuth 2.0 flow for Google Fit.
    In a real scenario, this would redirect the user to Google's OAuth consent screen.
    """
    # For now, we call the placeholder function from our integration module
    # In a real app, this would likely generate a state, store it in the session,
    # and redirect to an authorization URL constructed with client_id, redirect_uri, scope, etc.
    # from flask import redirect
    # auth_url = gfit.generate_google_auth_url(session) # Assuming gfit module has such a function
    # return redirect(auth_url)
    
    message = gfit.initiate_google_fit_auth()
    # Typically, you'd redirect the user to Google's auth URL.
    # For this placeholder, we just return a message.
    return jsonify({"message": message, "note": "User should be redirected to Google OAuth screen."}), 200

@app.route('/auth/google-fit/callback', methods=['GET'])
def google_fit_callback():
    """
    Handles the callback from Google after user authorization.
    Receives an authorization code (or an error) from Google.
    """
    authorization_code = request.args.get('code')
    error = request.args.get('error')

    if error:
        return jsonify({"error": f"Google Fit auth error: {error}"}), 400
    
    if not authorization_code:
        return jsonify({"error": "Missing authorization code from Google Fit callback."}), 400

    # In a real app, exchange the authorization_code for tokens (access_token, refresh_token)
    # and store them securely, associating them with the user_id.
    # user_id = session.get('user_id') # Example: get user_id from session
    # if not user_id:
    #    return jsonify({"error": "User session not found or expired."}), 400
    # tokens = gfit.exchange_code_for_tokens(authorization_code)
    # gfit.store_tokens_for_user(user_id, tokens)
    
    message = gfit.handle_google_fit_callback(authorization_code)
    
    # After successful token exchange, you might redirect the user to their dashboard
    # or trigger a data fetch.
    # For now, just return a success message.
    return jsonify({
        "message": message,
        "authorization_code_received": authorization_code,
        "note": "Tokens would be exchanged and stored. Data fetch could be triggered."
    }), 200

# Example of a conceptual endpoint to trigger data fetch after auth (not directly part of this subtask's UI)
@app.route('/api/google-fit/fetch-data/<int:user_id>', methods=['POST'])
def trigger_google_fit_fetch(user_id):
    """
    Conceptual endpoint to trigger fetching data from Google Fit for a user
    and then sending it to our /api/health-data endpoint.
    This assumes the user has already authenticated and we have an access token.
    """
    # In a real app:
    # 1. Retrieve the stored access_token for the user_id.
    #    access_token = gfit.get_access_token_for_user(user_id) # This might involve checking expiry and using refresh_token
    #    if not access_token:
    #        return jsonify({"error": "User not authenticated with Google Fit or token expired."}), 401
    
    # For this placeholder, we'll use a dummy access token.
    dummy_access_token = "DUMMY_ACCESS_TOKEN_FOR_USER_" + str(user_id)
    
    fetched_data = gfit.fetch_google_fit_data(user_id, dummy_access_token)

    if not fetched_data:
        return jsonify({"error": "Could not fetch data from Google Fit or no new data."}), 500

    # Now, we need to send this fetched data to our own /api/health-data endpoint.
    # This would typically be an internal request or direct function call to the data processing logic.
    # For simplicity, let's simulate the structure of data expected by /api/health-data
    
    # Assuming fetched_data contains: {'steps': ..., 'sleep_hours': ..., 'heart_rate_avg': ..., 'calories_burned': ...}
    # We need to add 'user_id' and 'date'.
    health_data_payload = {
        "user_id": user_id,
        "date": date.today().isoformat(),  # Use current date as an example
        "steps": fetched_data.get('steps'),
        "sleep_hours": fetched_data.get('sleep_hours'),
        "heart_rate_avg": fetched_data.get('heart_rate_avg'),
        "stress_score": fetched_data.get('stress_score', 0), # Google Fit might not provide stress score directly
        "calories_burned": fetched_data.get('calories_burned')
    }

    # Option 1: Internal HTTP POST request to /api/health-data (less ideal for same-app communication)
    # try:
    #     internal_api_url = request.url_root + 'api/health-data' # Construct full URL
    #     response = requests.post(internal_api_url, json=health_data_payload)
    #     response.raise_for_status() # Raise an exception for HTTP errors
    #     return jsonify({"message": "Google Fit data fetched and sent to /api/health-data successfully.", "details": response.json()}), 200
    # except requests.exceptions.RequestException as e:
    #     print(f"Error making internal call to /api/health-data: {e}")
    #     return jsonify({"error": f"Failed to submit fetched Google Fit data internally: {e}"}), 500

    # Option 2: Direct function call to the logic that /api/health-data uses (better)
    # This requires refactoring receive_health_data or its core logic into a callable function.
    # For now, we'll just describe this as the preferred method.
    # Example:
    # success, message_or_error = process_and_store_health_data(health_data_payload) # Hypothetical function
    # if success:
    #    return jsonify({"message": "Google Fit data fetched and processed successfully.", "details": message_or_error}), 200
    # else:
    #    return jsonify({"error": f"Failed to process fetched Google Fit data: {message_or_error}"}), 500

    return jsonify({
        "message": "Conceptual: Google Fit data fetched.",
        "fetched_data": fetched_data,
        "payload_for_internal_processing": health_data_payload,
        "next_step": "This data would be processed and stored, similar to /api/health-data."
    }), 200

# --- Smart Notifications Endpoint ---

@app.route('/api/user-notifications/<int:user_id>', methods=['GET'])
def get_user_notifications(user_id):
    """
    Checks and returns a list of smart notifications for the given user_id.
    """
    if user_id <= 0:
        return jsonify({"error": "Invalid user_id. Must be a positive integer."}), 400
    
    try:
        notifications = check_notification_triggers(user_id)
        if notifications is None: # Indicates a problem like DB connection failure in notification_manager
            return jsonify({"error": "Could not retrieve notifications due to an internal issue."}), 500
            
        return jsonify({"user_id": user_id, "notifications": notifications}), 200
        
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error in /api/user-notifications/{user_id}: {e}")
        # Return a generic error message to the client
        return jsonify({"error": "An unexpected error occurred while checking for notifications."}), 500

# --- Eco-Friendly Features: BYOB Reward System (Conceptual) ---

# This is a conceptual in-memory store for BYOB points for demonstration.
# In a real application, this would be stored in a database table (e.g., user_rewards).
byob_points_store = {} 

@app.route('/api/user-rewards/byob/<int:user_id>', methods=['POST'])
def record_byob_point(user_id):
    """
    Simulates recording a 'Bring Your Own Bottle' (BYOB) point for a user.
    """
    if user_id <= 0:
        return jsonify({"error": "Invalid user_id. Must be a positive integer."}), 400

    # Conceptually, increment BYOB points in a database for the user_id.
    # For now, we simulate this with an in-memory dictionary.
    if user_id not in byob_points_store:
        byob_points_store[user_id] = 0
    byob_points_store[user_id] += 1
    
    simulated_points = byob_points_store[user_id]
    
    # Log message indicating where DB interaction would occur
    print(f"BYOB point recorded for user_id: {user_id}. Total points: {simulated_points}. (DB update would occur here)")
    
    return jsonify({
        "message": f"BYOB point successfully recorded for user_id {user_id}.",
        "user_id": user_id,
        "simulated_byob_points": simulated_points
    }), 201

@app.route('/api/user-rewards/byob/<int:user_id>', methods=['GET'])
def get_byob_points(user_id):
    """
    Simulates fetching a user's 'Bring Your Own Bottle' (BYOB) points.
    """
    if user_id <= 0:
        return jsonify({"error": "Invalid user_id. Must be a positive integer."}), 400

    # Conceptually, fetch BYOB points from a database for the user_id.
    # For now, we retrieve from the in-memory dictionary.
    simulated_points = byob_points_store.get(user_id, 0) # Default to 0 if user not found
    
    # Log message indicating where DB interaction would occur
    print(f"Fetched BYOB points for user_id: {user_id}. Points: {simulated_points}. (DB query would occur here)")
    
    return jsonify({
        "user_id": user_id,
        "simulated_byob_points": simulated_points
    }), 200
