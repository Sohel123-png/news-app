# food_recommender.py
import random

def get_food_recommendation(steps: int, calories_burned: float, time_of_day: str) -> str:
    """
    Recommends food items based on activity level and time of day,
    including eco-ratings and eco-friendly suggestions.

    Args:
        steps: Number of steps taken.
        calories_burned: Calories burned.
        time_of_day: A string indicating the time of day ("morning", "afternoon", "evening").

    Returns:
        A string with the food recommendation, including price, eco-rating, and eco-suggestions.
    """
    time_of_day = time_of_day.lower() # Normalize to lowercase
    recommendation_text = ""
    eco_suggestion_appended = False

    # Eco-ratings are conceptual (1-5, 5 is best).
    # Format: "Food Item (Price, Eco-Rating: X/5)"
    # Eco-suggestions are added contextually.

    # High activity / High calorie burn
    if calories_burned > 300 and steps > 5000:
        if time_of_day == "morning":
            recommendation_text = "Paneer Sandwich + Banana Shake (₹60, Eco-Rating: 3/5), a great start for an active day!"
            if random.random() < 0.5: # 50% chance to add eco suggestion
                recommendation_text += " Consider using a reusable cup for your shake!"
                eco_suggestion_appended = True
        elif time_of_day == "afternoon":
            recommendation_text = "Rajma Chawal + Lassi (₹70, Eco-Rating: 4/5), a wholesome meal to refuel."
        elif time_of_day == "evening":
            recommendation_text = "Vegetable Pulao + Curd (₹65, Eco-Rating: 4/5), light yet satisfying for the evening."
        else: # Generic high activity
            recommendation_text = "Consider a balanced meal like Dal Makhani with Roti (₹80, Eco-Rating: 3/5) to recover."

    # Moderate activity / Moderate calorie burn
    elif 100 <= calories_burned <= 300 and 2000 <= steps <= 5000:
        if time_of_day == "morning":
            recommendation_text = "Oats with Fruits and Nuts (₹50, Eco-Rating: 5/5), a healthy and energizing breakfast."
            if random.random() < 0.5:
                recommendation_text += " Choose seasonal fruits from local vendors for an extra eco-boost!"
                eco_suggestion_appended = True
        elif time_of_day == "afternoon":
            recommendation_text = "Dal Roti with a side of Salad (₹55, Eco-Rating: 4/5), a balanced and light lunch."
        elif time_of_day == "evening":
            recommendation_text = "Vegetable Soup with a slice of Brown Bread (₹45, Eco-Rating: 3/5), light and easy to digest."
        else: # Generic moderate activity
            recommendation_text = "A serving of Idli Sambar (₹60, Eco-Rating: 4/5) could be a good choice."
            
    # Low activity / Low calorie burn
    elif calories_burned < 100:
        if time_of_day == "morning":
            recommendation_text = "A piece of Fruit (e.g., Apple or Banana) (₹20, Eco-Rating: 5/5) or a glass of Milk (₹25, Eco-Rating: 3/5)."
        elif time_of_day == "afternoon":
            recommendation_text = "Light snack like a Fruit Salad (₹40, Eco-Rating: 5/5) or Coconut Water (₹30, Eco-Rating: 5/5)."
            if random.random() < 0.7: # Higher chance for this suggestion
                recommendation_text += " If it's coconut water, try to get it directly from a vendor to avoid packaging."
                eco_suggestion_appended = True
        elif time_of_day == "evening":
            recommendation_text = "A cup of Green Tea with a few Almonds (₹35, Eco-Rating: 4/5)."
        else: # Generic low activity
            recommendation_text = "Consider a light snack like Sprout Salad (₹30, Eco-Rating: 5/5) or a small bowl of Yogurt (₹25, Eco-Rating: 3/5)."

    # Default fallback if no specific rule is met
    else:
        if time_of_day == "morning":
            recommendation_text = "Poha with a glass of Juice (₹40, Eco-Rating: 3/5) is a popular choice for breakfast."
        elif time_of_day == "afternoon":
            recommendation_text = "Consider a Thali meal for a variety of options (₹90-₹150, Eco-Rating: Varies)."
        elif time_of_day == "evening":
            recommendation_text = "Khichdi with a dollop of Ghee (₹50, Eco-Rating: 4/5) is a comforting and healthy dinner."
        else: # Generic fallback
            recommendation_text = "Water is always a good choice! For food, consider your hunger level and preferences. Opt for less packaging where possible."
            eco_suggestion_appended = True # Default suggestion is eco-friendly

    # Generic eco-friendly suggestion if no specific one was added and it's not the default fallback
    if not eco_suggestion_appended and "Water is always a good choice!" not in recommendation_text:
        if random.random() < 0.3: # 30% chance to add a generic eco suggestion
            generic_suggestions = [
                " Consider a local organic version if available!",
                " Pair this with a fresh juice – even better if it's from a local vendor!",
                " Remember to minimize food waste with your meal!"
            ]
            recommendation_text += random.choice(generic_suggestions)

    return recommendation_text

if __name__ == '__main__':
    # Test cases
    print("--- Eco-Friendly Food Recommendations ---")
    print(f"High activity, Morning: {get_food_recommendation(6000, 350, 'Morning')}")
    print(f"High activity, Afternoon: {get_food_recommendation(5500, 400, 'Afternoon')}")
    print(f"High activity, Evening: {get_food_recommendation(7000, 320, 'Evening')}")
    
    print(f"\nModerate activity, Morning: {get_food_recommendation(3000, 150, 'morning')}")
    print(f"Moderate activity, Afternoon: {get_food_recommendation(2500, 200, 'AFTERNOON')}")
    print(f"Moderate activity, Evening: {get_food_recommendation(4000, 280, 'evening')}")

    print(f"\nLow activity, Morning: {get_food_recommendation(500, 50, 'morning')}")
    print(f"Low activity, Afternoon (high chance of specific suggestion): {get_food_recommendation(800, 80, 'afternoon')}")
    print(f"Low activity, Evening: {get_food_recommendation(300, 40, 'evening')}")
    
    print(f"\nDefault, Morning: {get_food_recommendation(1500, 120, 'morning')}")
    print(f"Default, Unknown time: {get_food_recommendation(100, 10, 'anytime')}")
    print(f"Edge case, very low activity: {get_food_recommendation(10, 5, 'afternoon')}")
    print(f"Another moderate case: {get_food_recommendation(2200, 220, 'afternoon')}") # Check generic suggestions
    print(f"Another high activity: {get_food_recommendation(6000, 400, 'evening')}") # Check generic suggestions
