# Fitgent 2.0 - Future AI Expansion Ideas

This document outlines potential future AI-driven capabilities for Fitgent 2.0, aimed at enhancing user well-being, productivity, and engagement.

## A. Predict Fatigue & Suggest Breaks

*   **1. Goal:**
    *   Proactively identify when a student is likely to experience fatigue based on their health data and activity patterns.
    *   Suggest timely breaks to help maintain cognitive performance, improve productivity, and support overall well-being.

*   **2. Potential Data Inputs:**
    *   **Existing:**
        *   `sleep_hours` (from `user_health_data`): Insufficient sleep is a primary contributor to fatigue.
        *   `stress_score` (from `user_health_data`): High stress can exacerbate fatigue.
        *   `heart_rate_avg` (from `user_health_data`): Anomalies or sustained high resting heart rates could indicate strain.
        *   `steps` / activity levels over time (from `user_health_data`): Both very low (sedentary) and excessively high activity without adequate rest can lead to fatigue.
    *   **New/Conceptual:**
        *   `time_spent_on_study_tasks`: Data from a potential integrated study timer or calendar indicating duration of focused work.
        *   `task_switching_frequency`: High frequency might indicate difficulty concentrating, a symptom of fatigue.
        *   `user_reported_alertness_levels`: Optional, periodic self-reported scores (e.g., on a 1-5 scale) could be used for training a predictive model or personalizing a rule-based system.
        *   `time_of_day`: Circadian rhythms influence alertness.

*   **3. Possible Approach (Conceptual):**
    *   **Phase 1 (Advanced Rule-Based System):**
        *   Develop a scoring system combining weighted factors: e.g., `(low_sleep_score + high_stress_score + prolonged_inactivity_score + high_study_duration_score) > fatigue_threshold`.
        *   Rules could be personalized based on user baselines or preferences. For example, "prolonged inactivity" could be defined as < X steps in the last Y hours.
    *   **Phase 2 (Machine Learning Model):**
        *   Train a classifier (e.g., Logistic Regression, Decision Tree, Support Vector Machine, or a simple Neural Network) on historical data.
        *   **Features:** The "Potential Data Inputs" listed above.
        *   **Target Variable:** Could be user-reported fatigue, or a proxy like a significant drop in study performance (if measurable), or meeting a combination of fatigue-indicating rule conditions.
        *   The model would learn patterns that typically precede fatigue for individual users or user segments.

*   **4. Integration Points:**
    *   **Health AI Suggestion Module (`health_suggestions.py`):** The fatigue prediction logic could be a new function within this module, or the module could call out to a dedicated fatigue prediction service. Generated suggestions ("Time for a 15-min power nap!") would be added to the list of health suggestions.
    *   **Smart Notifications Module (`notification_manager.py`):** Fatigue predictions could trigger proactive notifications (e.g., "You've been working hard, and your sleep was low. Consider a short break soon.").
    *   **Health Dashboard UI (`health_dashboard.html`):** Could display a "Fatigue Risk" indicator or prompt for breaks.
    *   **(New) Study Timer/Planner Module:** Could directly receive signals to pause timers or suggest re-evaluating the study schedule.

## B. Auto-adjust Study Sessions based on Stress

*   **1. Goal:**
    *   Dynamically adapt study session lengths, intensity, or content based on a user's real-time or recent stress levels.
    *   Aim to optimize learning by preventing cognitive overload and burnout, making study more effective and sustainable.

*   **2. Potential Data Inputs:**
    *   **Existing:**
        *   `stress_score` (from `user_health_data`): Primary input, ideally updated frequently or in near real-time if possible via smartwatch sync.
    *   **New/Conceptual:**
        *   `current_study_task_subject`: Different subjects might have different cognitive loads.
        *   `task_difficulty_rating`: User-defined or AI-estimated difficulty of the current task.
        *   `predefined_user_preferences`: User-set ideal session lengths, preferred break times, or subject order.
        *   `upcoming_deadlines_urgency`: From a calendar or task list integration.
        *   `user_feedback_on_session_effectiveness`: Post-session rating of how productive they felt.

*   **3. Possible Approach (Conceptual):**
    *   **Rule-Based System:**
        *   If `stress_score` > threshold_high:
            *   Suggest immediate short break (e.g., 5-10 minutes).
            *   Recommend reducing current study session length by X%.
            *   Suggest switching to a lower-intensity task/subject (if multiple are planned).
            *   Offer a mindfulness exercise or breathing technique.
        *   If `stress_score` is consistently moderate:
            *   Ensure regular breaks are being taken (e.g., Pomodoro technique).
        *   If `stress_score` is low:
            *   Potentially suggest extending a session if the user is "in the zone" (with caution, and user opt-in).
    *   **Adaptive Algorithm (More Advanced):**
        *   Could use reinforcement learning where the "agent" learns the best study session adjustment strategy based on user feedback (e.g., did stress decrease? did productivity improve?). This is complex but offers high personalization.

*   **4. Integration Points:**
    *   **(New) Study Session Management Module:** This would be a core new module responsible for tracking study sessions (timers, tasks). It would be the primary consumer of this AI feature.
    *   **Health AI Suggestion Module (`health_suggestions.py`):** Could provide advice like "Your stress levels are rising. Let's adjust your study plan for today."
    *   **Smart Notifications Module (`notification_manager.py`):** Can send alerts like "High stress detected! Time to shorten this session or take a break."
    *   **Health Dashboard UI (`health_dashboard.html`):** Could include a section for managing study sessions and seeing stress-based adjustments.
    *   **External Calendar/To-Do List Integration:** To fetch task information and potentially modify session blocks.

## C. AI Food Recommendation Engine with Macros

*   **1. Goal:**
    *   Provide highly personalized and nutritionally detailed food recommendations.
    *   Include macronutrient breakdowns (protein, carbohydrates, fats) and align with user's specific dietary goals (e.g., weight loss, muscle gain, balanced diet).

*   **2. Potential Data Inputs:**
    *   **Existing:**
        *   `calories_burned`, `steps` (from `user_health_data`): To estimate daily energy expenditure.
        *   `time_of_day` (from API request to food recommender).
    *   **New/Conceptual:**
        *   `user_dietary_goals`: (e.g., target daily calories, macro ratio like 40% carbs, 30% protein, 30% fat, weight loss/gain/maintenance). Set up during profile creation.
        *   `user_food_preferences`: Likes, dislikes, cuisines.
        *   `user_allergies_restrictions`: (e.g., gluten-free, vegetarian, nut allergy).
        *   `detailed_food_database`: A comprehensive database containing food items with detailed nutritional information (macros, micros, ingredients, portion sizes, eco-ratings).
        *   `user_meal_history_feedback`: What the user ate previously, and their ratings for those meals/recommendations.

*   **3. Possible Approach (Conceptual):**
    *   **Knowledge-Based System / Constraint Satisfaction:**
        *   Define user requirements (goals, preferences, restrictions) as constraints.
        *   Query the food database for items/meals that satisfy these constraints for a given mealtime (breakfast, lunch, dinner, snack).
        *   Rank results based on how well they meet macro targets, calorie goals, and user preferences.
    *   **Machine Learning for Personalization:**
        *   **Collaborative Filtering:** Recommend foods that similar users (with similar goals and preferences) liked.
        *   **Content-Based Filtering:** Recommend foods similar to what the user has liked in the past, based on ingredients, cuisine type, macro profile.
        *   **Reinforcement Learning:** The system suggests meals, the user provides feedback (e.g., "ate it and liked it", "skipped", "disliked"), and the model adjusts its future recommendations to maximize positive feedback.
    *   **Integration with Nutritional Database APIs:** Utilize external APIs (e.g., Edamam, Spoonacular, USDA FoodData Central) to access comprehensive food data instead of building/maintaining a massive internal database.

*   **4. Integration Points:**
    *   **Food Recommender Module (`food_recommender.py`):** This module would be significantly overhauled or replaced by the new engine. The existing `get_food_recommendation` function would call this new, more advanced logic.
    *   **Database:** Requires new tables for user dietary profiles, preferences, restrictions, and potentially a cached/customized version of the food database or links to external food IDs.
    *   **(New) User Profile/Settings UI:** For users to input their goals, preferences, and restrictions.
    *   **Health Dashboard UI (`health_dashboard.html`):** The food recommendation section would display these more detailed suggestions.
    *   **(New) Meal Planning/Tracking Module:** Users could plan meals based on recommendations and track their intake.

## D. Gamify with Health + Study XP System

*   **1. Goal:**
    *   Increase user engagement, motivation, and adherence to positive health and study habits.
    *   Provide a sense of achievement and progress through experience points (XP), levels, and badges.

*   **2. Potential Data Inputs:**
    *   **Existing (or derivable):**
        *   Daily steps, sleep duration, stress levels (from `user_health_data`).
        *   Usage of features like food logging (if implemented), BYOB points.
    *   **New/Conceptual:**
        *   `study_session_completion`: Successful completion of planned study blocks.
        *   `task_completion_rate`: From an integrated to-do list or study planner.
        *   `break_adherence`: Taking breaks when suggested by the fatigue prediction system.
        *   `eco_friendly_choices_made`: (e.g., selecting meals with high eco-ratings, logging BYOB).
        *   `badge_unlock_criteria_met`: Specific achievements (e.g., "7-day streak of 8000+ steps").
        *   `daily_app_engagement`: Logging in, interacting with modules.

*   **3. Possible Approach (Conceptual):**
    *   **Rule-Based XP and Badge Awarding System:**
        *   Define specific actions and the XP awarded for each (e.g., 100 XP for 8000 steps, 50 XP for completing a study session, 20 XP for logging BYOB).
        *   Define criteria for badges (e.g., "Early Riser Badge" for logging 7 hours of sleep before 7 AM for 5 consecutive days).
        *   Leaderboards (optional, could be by friend group or anonymous).
    *   **Database Schema Additions:**
        *   `user_xp` table (user\_id, current\_xp, current\_level, total\_xp).
        *   `user_badges` table (user\_id, badge\_id, date\_earned).
        *   `badge_definitions` table (badge\_id, name, description, criteria, image\_url).
        *   `xp_rules` table (action\_id, xp\_value, description).
    *   **Streaks and Challenges:** Implement logic for daily/weekly streaks (e.g., consistent sleep) or special challenges for bonus XP.

*   **4. Integration Points:**
    *   **(New) Gamification Engine/Module:** This would be a central module that:
        *   Receives events/data from other modules (e.g., "user X completed 10k steps", "user Y finished a study session").
        *   Applies XP rules and updates user XP/levels in the database.
        *   Checks for and awards badges.
    *   **All other Modules:**
        *   `Smartwatch Sync / Health Data API (`/api/health-data`): Would feed data into the gamification engine.
        *   `(New) Study Session Module`: Would report session completions.
        *   `Food Recommender / Eco-Friendly Module`: Would report BYOB points, possibly choices of eco-friendly meals.
        *   `Health AI Suggestion / Fatigue Prediction Modules`: Could award XP for adhering to suggestions (e.g., taking a recommended break).
    *   **Health Dashboard UI (`health_dashboard.html`):**
        *   Prominently display user's XP, level, and earned badges.
        *   Show progress towards next level or unearned badges.
        *   Possibly display leaderboards.
    *   **Smart Notifications Module (`notification_manager.py`):** Could send notifications for new badges, level-ups, or daily XP summaries.
