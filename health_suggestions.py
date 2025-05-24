# health_suggestions.py

def get_health_suggestions(health_data: dict) -> list:
    """
    Generates health suggestions based on a dictionary of health data.

    Args:
        health_data: A dictionary containing health metrics like:
            'steps': int,
            'sleep_hours': float,
            'heart_rate_avg': float,
            'stress_score': int (0-100),
            'calories_burned': float

    Returns:
        A list of suggestion strings.
    """
    suggestions = []

    # Rule for Steps
    if health_data.get('steps', 0) > 10000:
        suggestions.append("High activity today! Consider a protein-rich snack.")

    # Rule for Sleep Hours
    if health_data.get('sleep_hours', 8) < 6: # Assuming 8 is a neutral default if data is missing
        suggestions.append("You had less than 6 hours of sleep. Try to take a short break or do some stretching.")

    # Rule for Heart Rate (Resting/Non-exercise average)
    # Note: This is a simplistic rule. Real-world scenarios need more context (e.g., activity level).
    if health_data.get('heart_rate_avg', 70) > 100: # Assuming 70 is a neutral default
        suggestions.append("Your average heart rate seems a bit high. Avoid heavy meals for now and consider a fruit juice.")

    # Rule for Stress Score (Assuming a scale of 0-100)
    if health_data.get('stress_score', 30) > 60: # Assuming 30 is a neutral default
        suggestions.append("Feeling stressed? Try some deep breathing exercises or a short mindfulness session.")

    # Rule for Calories Burned
    if health_data.get('calories_burned', 0) > 500:
        suggestions.append("You've burned a significant amount of calories. Ensure your next meal helps you recover.")
    
    if not suggestions:
        suggestions.append("Looking good! Keep up the healthy habits.")

    return suggestions

if __name__ == '__main__':
    # Example Usage:
    sample_data_1 = {
        'steps': 12000,
        'sleep_hours': 5.5,
        'heart_rate_avg': 105, # bpm
        'stress_score': 70, # 0-100 scale
        'calories_burned': 600 
    }
    print(f"Suggestions for sample_data_1: {get_health_suggestions(sample_data_1)}")

    sample_data_2 = {
        'steps': 5000,
        'sleep_hours': 7,
        'heart_rate_avg': 65,
        'stress_score': 40,
        'calories_burned': 250
    }
    print(f"Suggestions for sample_data_2: {get_health_suggestions(sample_data_2)}")
    
    sample_data_3 = {
        'steps': 15000,
        'sleep_hours': 8,
        'heart_rate_avg': 70,
        'stress_score': 20,
        'calories_burned': 700
    }
    print(f"Suggestions for sample_data_3 (high activity, low stress): {get_health_suggestions(sample_data_3)}")

    sample_data_no_issues = {
        'steps': 8000,
        'sleep_hours': 7.5,
        'heart_rate_avg': 70,
        'stress_score': 50,
        'calories_burned': 400
    }
    print(f"Suggestions for no specific issues: {get_health_suggestions(sample_data_no_issues)}")
