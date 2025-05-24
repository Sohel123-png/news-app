# notification_manager.py
import psycopg2
import os
from datetime import datetime # Required for fetching data if we were to use date logic

# Database connection details (copied from app.py for now, consider a shared config/db module later)
DB_NAME = "fitgent_db"
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")

def get_db_connection_for_notifications(): # Renamed to avoid conflict if imported into app.py
    """Establishes a connection to the PostgreSQL database."""
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database in notification_manager: {e}.")
    except psycopg2.Error as e:
        print(f"General database connection error in notification_manager: {e}")
    return conn

def check_notification_triggers(user_id: int) -> list:
    """
    Checks for conditions that should trigger notifications for a given user.

    Args:
        user_id: The ID of the user.

    Returns:
        A list of notification message strings.
    """
    notifications = []
    latest_health_data = None

    conn = None
    try:
        conn = get_db_connection_for_notifications()
        if conn is None:
            # If DB connection fails, we can't fetch data, so maybe return a default or error indication
            # For now, we'll just proceed, and it will likely result in fewer notifications
            print(f"Notification Manager: DB connection failed for user {user_id}. Cannot fetch data.")
            # Potentially add a generic "check app" notification if DB is down for a while?
            # notifications.append("Could not fetch latest data. Please check the app.")
            # return notifications # Early exit if no DB
        else:
            cur = conn.cursor()
            # Fetch the most recent health data entry for the user
            # We need 'steps' and 'stress_score'.
            # Assuming 'date' column is used for ordering to get the latest.
            # If multiple entries per day, a timestamp or auto-increment ID would be better.
            fetch_query = """
            SELECT steps, stress_score 
            FROM user_health_data
            WHERE user_id = %s
            ORDER BY date DESC
            LIMIT 1;
            """
            cur.execute(fetch_query, (user_id,))
            latest_health_data = cur.fetchone()
            cur.close()

    except psycopg2.Error as e:
        print(f"Database error in check_notification_triggers for user {user_id}: {e}")
        # Decide if we want to send a notification about data fetch issues
    except Exception as e:
        print(f"Unexpected error in check_notification_triggers for user {user_id}: {e}")
    finally:
        if conn:
            conn.close()

    # --- Notification Logic ---

    # 1. Low water intake
    # SIMPLIFICATION: We don't have water intake data in user_health_data.
    # Returning a static reminder for demonstration.
    # Ideally, we'd check `last_water_intake_time`.
    notifications.append("Time to hydrate 💧")

    if latest_health_data:
        steps, stress_score = latest_health_data[0], latest_health_data[1]

        # 2. Long sitting / No activity in 2hr
        # SIMPLIFICATION: We don't have activity timestamps or steps for the "last 2 hours".
        # We'll use the latest 'steps' count as a proxy. If it's very low,
        # it might indicate prolonged inactivity *leading up to* this data point.
        # This is a significant simplification.
        # A more accurate system would query steps within a rolling 2-hour window.
        if steps is not None and steps < 100: # Assuming a daily step entry, this implies very low activity for that day so far.
            notifications.append("Been sitting for a while? Stand up for 2 mins 🚶‍♂️")
            notifications.append("Consider doing a quick stretch!")
        
        # 3. High stress
        if stress_score is not None and stress_score > 70:
            notifications.append("Feeling stressed? Take 3 deep breaths 🧘")
            
    else:
        # If no health data is found for the user, perhaps a generic reminder.
        notifications.append("Don't forget to log your health data today!")

    # Ensure no duplicate messages if logic overlaps (not an issue with current rules)
    return list(set(notifications)) # Return unique notifications

if __name__ == '__main__':
    # Example Usage (requires database to be running and populated for meaningful results)
    sample_user_id = 1 # Assume user 1 exists
    
    print(f"--- Checking notifications for user_id: {sample_user_id} ---")
    
    # To test effectively, you'd need to insert some data for user_id 1 first.
    # E.g., high stress, low steps.
    # For now, this will likely hit the "no data" or "low steps" conditions if DB is empty for user 1.
    
    # Example: Manually create a dummy connection and cursor for local testing if DB is not set up
    # This part is for standalone testing and would not be in production code.
    try:
        # Ensure you have a user_health_data table and potentially insert a test row:
        # INSERT INTO user_health_data (user_id, date, steps, sleep_hours, heart_rate_avg, stress_score, calories_burned) 
        # VALUES (1, '2024-07-31', 50, 6.0, 70, 75, 200);
        
        user_notifications = check_notification_triggers(sample_user_id)
        if user_notifications:
            print("Notifications to send:")
            for notif in user_notifications:
                print(f"- {notif}")
        else:
            print("No specific notifications triggered based on current data.")
            
    except Exception as e:
        print(f"Error during example run: {e}")
        print("Please ensure your database is set up and accessible, and the user_health_data table exists.")
        print("You might need to insert sample data for the user_id being tested.")

    # Test with a non-existent user or user with no data (if DB is accessible)
    # print("\n--- Checking notifications for user_id: 999 (likely no data) ---")
    # user_notifications_no_data = check_notification_triggers(999)
    # if user_notifications_no_data:
    #     print("Notifications to send:")
    #     for notif in user_notifications_no_data:
    #         print(f"- {notif}")
    # else:
    #     print("No specific notifications triggered based on current data.")
