import requests
import json
import os
from datetime import datetime
import sqlite3

class AIEnhancements:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        
    def generate_fitness_coaching(self, user_data, workout_history=None, meal_history=None):
        """Generate personalized fitness coaching using AI"""
        
        # Prepare context for AI
        context = f"""
        You are a professional fitness coach. Create personalized coaching advice for this user:
        
        User Profile:
        - Age: {user_data.get('age', 'N/A')}
        - Gender: {user_data.get('gender', 'N/A')}
        - Height: {user_data.get('height', 'N/A')} cm
        - Weight: {user_data.get('weight', 'N/A')} kg
        - Activity Level: {user_data.get('activity_level', 'N/A')}
        - Fitness Goal: {user_data.get('fitness_goal', 'N/A')}
        - Region: {user_data.get('region', 'N/A')}
        - Budget: {user_data.get('budget', 'N/A')}
        - Allergies: {user_data.get('allergies', 'None')}
        
        Recent Workouts: {workout_history or 'No recent workouts'}
        Recent Meals: {meal_history or 'No recent meals'}
        
        Provide:
        1. Motivational message (2-3 sentences)
        2. 3 specific tips for their fitness journey
        3. 1 challenge for the week
        4. Encouragement based on their progress
        
        Keep it friendly, motivating, and actionable. Format as JSON with keys: motivation, tips, challenge, encouragement
        """
        
        try:
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                json={
                    "contents": [{
                        "parts": [{"text": context}]
                    }]
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    # Try to parse as JSON, fallback to text
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        print(f"Failed to parse AI coaching response as JSON: {content[:200]}...")
                        return self._get_fallback_coaching(user_data)
            else:
                print(f"AI coaching API error: {response.status_code} - {response.text}")
                return self._get_fallback_coaching(user_data)
            
            return self._get_fallback_coaching(user_data)
        except Exception as e:
            print(f"AI coaching error: {e}")
            return self._get_fallback_coaching(user_data)
    
    def _get_fallback_coaching(self, user_data):
        """Provide fallback coaching when AI is unavailable"""
        fitness_goal = user_data.get('fitness_goal', 'general_fitness')
        
        if fitness_goal == 'weight_loss':
            return {
                "motivation": "Your weight loss journey is a marathon, not a sprint. Every healthy choice you make brings you closer to your goals. Remember, consistency beats perfection every time!",
                "tips": [
                    "Focus on creating a sustainable calorie deficit through diet and exercise",
                    "Prioritize protein-rich foods to maintain muscle mass while losing fat",
                    "Track your progress with measurements and photos, not just the scale"
                ],
                "challenge": "This week, try to log every meal and workout, and aim for 7 days of consistent healthy eating.",
                "encouragement": "You're building healthy habits that will last a lifetime. Keep pushing forward!"
            }
        elif fitness_goal == 'muscle_gain':
            return {
                "motivation": "Building muscle is a journey of patience and persistence. Your body is capable of amazing transformations when you give it the right fuel and training!",
                "tips": [
                    "Focus on progressive overload in your strength training",
                    "Ensure adequate protein intake (1.6-2.2g per kg body weight)",
                    "Prioritize compound movements like squats, deadlifts, and bench press"
                ],
                "challenge": "This week, try to increase the weight or reps in at least one exercise for each muscle group.",
                "encouragement": "Every rep counts towards building the stronger version of yourself!"
            }
        else:  # General fitness
            return {
                "motivation": "Your commitment to fitness is inspiring! Every workout, every healthy meal, and every step forward is building a stronger, healthier you.",
                "tips": [
                    "Find activities you enjoy to make fitness sustainable",
                    "Balance cardio, strength training, and flexibility work",
                    "Listen to your body and prioritize recovery"
                ],
                "challenge": "This week, try a new type of exercise or workout that you've never done before.",
                "encouragement": "You're creating a lifestyle that will benefit you for years to come!"
            }
    
    def generate_recipe_suggestions(self, user_data, available_ingredients=None):
        """Generate personalized recipe suggestions"""
        
        allergies = user_data.get('allergies', 'None')
        if allergies and allergies.lower() not in ['none', 'no', 'n/a', '']:
            allergy_warning = f"CRITICAL: User has allergies to: {allergies}. DO NOT include any of these ingredients in ANY recipe. This is a safety requirement."
        else:
            allergy_warning = "User has no known allergies."
        
        context = f"""
        Suggest 3 healthy recipes for this user:
        
        User Preferences:
        - Region: {user_data.get('region', 'N/A')}
        - Budget: {user_data.get('budget', 'N/A')}
        - Allergies: {allergies}
        - Fitness Goal: {user_data.get('fitness_goal', 'N/A')}
        - Available ingredients: {available_ingredients or 'Any ingredients'}
        
        {allergy_warning}
        
        Requirements:
        - Recipes should be healthy and align with their fitness goal
        - Consider their budget and regional preferences
        - ABSOLUTELY AVOID any allergens listed above - this is a safety requirement
        - Include nutritional information (calories, protein, carbs, fat)
        - Provide cooking instructions
        - If user has allergies, suggest alternative ingredients that are safe
        
        Format as JSON with array of recipes, each containing: name, ingredients, instructions, nutrition, prep_time, difficulty
        """
        
        try:
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                json={
                    "contents": [{
                        "parts": [{"text": context}]
                    }]
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    try:
                        parsed_content = json.loads(content)
                        if 'recipes' in parsed_content:
                            return parsed_content
                        elif isinstance(parsed_content, list):
                            return {"recipes": parsed_content}
                        else:
                            return self._get_fallback_recipes(user_data)
                    except json.JSONDecodeError:
                        print(f"Failed to parse AI recipe response as JSON: {content[:200]}...")
                        return self._get_fallback_recipes(user_data)
            else:
                print(f"AI recipe API error: {response.status_code} - {response.text}")
                return self._get_fallback_recipes(user_data)
            
            return self._get_fallback_recipes(user_data)
        except Exception as e:
            print(f"AI recipe error: {e}")
            return self._get_fallback_recipes(user_data)
    
    def _get_fallback_recipes(self, user_data):
        """Provide fallback recipes when AI is unavailable"""
        fitness_goal = user_data.get('fitness_goal', 'general_fitness')
        region = user_data.get('region', 'general').lower()
        allergies = user_data.get('allergies', '').lower()
        
        # Common allergens to check for
        common_allergens = {
            'nuts': ['peanuts', 'almonds', 'walnuts', 'cashews', 'pistachios', 'hazelnuts', 'pecans', 'macadamia nuts'],
            'dairy': ['milk', 'cheese', 'yogurt', 'butter', 'cream', 'whey', 'casein'],
            'eggs': ['eggs', 'egg whites', 'egg yolks'],
            'gluten': ['wheat', 'gluten', 'barley', 'rye', 'bread', 'pasta'],
            'soy': ['soy', 'soybeans', 'tofu', 'soy sauce', 'edamame'],
            'shellfish': ['shrimp', 'crab', 'lobster', 'oysters', 'mussels', 'clams'],
            'fish': ['fish', 'salmon', 'tuna', 'cod', 'tilapia', 'mackerel']
        }
        
        def is_allergen_safe(ingredients):
            """Check if ingredients are safe for user's allergies"""
            if not allergies or allergies in ['none', 'no', 'n/a', '']:
                return True
            
            for ingredient in ingredients:
                ingredient_lower = ingredient.lower()
                for allergen_type, allergen_list in common_allergens.items():
                    if any(allergen in ingredient_lower for allergen in allergen_list):
                        # Check if user is allergic to this type
                        if allergen_type in allergies or any(allergen in allergies for allergen in allergen_list):
                            return False
            return True
        
        if fitness_goal == 'weight_loss':
            # Base recipes that can be modified based on allergies
            base_recipes = [
                {
                    "name": "Grilled Chicken Salad",
                    "ingredients": ["Chicken breast", "Mixed greens", "Cherry tomatoes", "Cucumber", "Olive oil", "Lemon juice"],
                    "instructions": ["Season chicken with herbs", "Grill for 6-8 minutes per side", "Chop vegetables", "Mix with olive oil and lemon"],
                    "nutrition": {"calories": 350, "protein": 35, "carbs": 8, "fat": 20},
                    "prep_time": "20 minutes",
                    "difficulty": "Easy"
                },
                {
                    "name": "Quinoa Bowl",
                    "ingredients": ["Quinoa", "Broccoli", "Carrots", "Tofu", "Soy sauce", "Sesame oil"],
                    "instructions": ["Cook quinoa according to package", "Steam vegetables", "Pan-fry tofu", "Combine with sauce"],
                    "nutrition": {"calories": 400, "protein": 18, "carbs": 45, "fat": 15},
                    "prep_time": "25 minutes",
                    "difficulty": "Medium"
                },
                {
                    "name": "Greek Yogurt Parfait",
                    "ingredients": ["Greek yogurt", "Berries", "Honey", "Nuts", "Granola"],
                    "instructions": ["Layer yogurt in glass", "Add berries and honey", "Top with nuts and granola"],
                    "nutrition": {"calories": 280, "protein": 20, "carbs": 25, "fat": 12},
                    "prep_time": "5 minutes",
                    "difficulty": "Easy"
                }
            ]
            
            # Filter recipes based on allergies
            recipes = []
            for recipe in base_recipes:
                if is_allergen_safe(recipe["ingredients"]):
                    recipes.append(recipe)
                else:
                    # Create allergy-safe alternative
                    safe_recipe = recipe.copy()
                    if "nuts" in allergies or "peanuts" in allergies:
                        if "Nuts" in safe_recipe["ingredients"]:
                            safe_recipe["ingredients"].remove("Nuts")
                            safe_recipe["ingredients"].append("Seeds (sunflower/pumpkin)")
                        if "Granola" in safe_recipe["ingredients"]:
                            safe_recipe["ingredients"].remove("Granola")
                            safe_recipe["ingredients"].append("Oats")
                    if "dairy" in allergies or "milk" in allergies:
                        if "Greek yogurt" in safe_recipe["ingredients"]:
                            safe_recipe["ingredients"].remove("Greek yogurt")
                            safe_recipe["ingredients"].append("Coconut yogurt")
                    if "soy" in allergies:
                        if "Tofu" in safe_recipe["ingredients"]:
                            safe_recipe["ingredients"].remove("Tofu")
                            safe_recipe["ingredients"].append("Chickpeas")
                        if "Soy sauce" in safe_recipe["ingredients"]:
                            safe_recipe["ingredients"].remove("Soy sauce")
                            safe_recipe["ingredients"].append("Coconut aminos")
                    
                    recipes.append(safe_recipe)
        elif fitness_goal == 'muscle_gain':
            # Base recipes that can be modified based on allergies
            base_recipes = [
                {
                    "name": "Protein Power Bowl",
                    "ingredients": ["Salmon", "Brown rice", "Sweet potato", "Spinach", "Avocado", "Eggs"],
                    "instructions": ["Bake salmon with herbs", "Cook rice and sweet potato", "Sauté spinach", "Top with avocado and eggs"],
                    "nutrition": {"calories": 550, "protein": 45, "carbs": 55, "fat": 25},
                    "prep_time": "30 minutes",
                    "difficulty": "Medium"
                },
                {
                    "name": "Lean Beef Stir-Fry",
                    "ingredients": ["Lean beef", "Broccoli", "Bell peppers", "Brown rice", "Soy sauce", "Ginger"],
                    "instructions": ["Slice beef thinly", "Stir-fry with vegetables", "Add sauce and ginger", "Serve over rice"],
                    "nutrition": {"calories": 480, "protein": 40, "carbs": 40, "fat": 18},
                    "prep_time": "25 minutes",
                    "difficulty": "Medium"
                },
                {
                    "name": "Cottage Cheese Protein Bowl",
                    "ingredients": ["Cottage cheese", "Banana", "Almonds", "Chia seeds", "Cinnamon"],
                    "instructions": ["Mix cottage cheese with banana", "Top with almonds and chia seeds", "Sprinkle with cinnamon"],
                    "nutrition": {"calories": 320, "protein": 25, "carbs": 20, "fat": 15},
                    "prep_time": "5 minutes",
                    "difficulty": "Easy"
                }
            ]
            
            # Filter recipes based on allergies
            recipes = []
            for recipe in base_recipes:
                if is_allergen_safe(recipe["ingredients"]):
                    recipes.append(recipe)
                else:
                    # Create allergy-safe alternative
                    safe_recipe = recipe.copy()
                    if "fish" in allergies or "salmon" in allergies:
                        if "Salmon" in safe_recipe["ingredients"]:
                            safe_recipe["ingredients"].remove("Salmon")
                            safe_recipe["ingredients"].append("Chicken breast")
                    if "eggs" in allergies:
                        if "Eggs" in safe_recipe["ingredients"]:
                            safe_recipe["ingredients"].remove("Eggs")
                            safe_recipe["ingredients"].append("Tempeh")
                    if "nuts" in allergies or "almonds" in allergies:
                        if "Almonds" in safe_recipe["ingredients"]:
                            safe_recipe["ingredients"].remove("Almonds")
                            safe_recipe["ingredients"].append("Sunflower seeds")
                    if "dairy" in allergies or "cottage cheese" in allergies:
                        if "Cottage cheese" in safe_recipe["ingredients"]:
                            safe_recipe["ingredients"].remove("Cottage cheese")
                            safe_recipe["ingredients"].append("Silken tofu")
                    if "soy" in allergies:
                        if "Soy sauce" in safe_recipe["ingredients"]:
                            safe_recipe["ingredients"].remove("Soy sauce")
                            safe_recipe["ingredients"].append("Coconut aminos")
                    
                    recipes.append(safe_recipe)
        else:  # General fitness
            # Base recipes that can be modified based on allergies
            base_recipes = [
                {
                    "name": "Mediterranean Wrap",
                    "ingredients": ["Whole wheat tortilla", "Hummus", "Cucumber", "Tomato", "Feta cheese", "Olives"],
                    "instructions": ["Spread hummus on tortilla", "Add vegetables and feta", "Roll tightly", "Cut diagonally"],
                    "nutrition": {"calories": 380, "protein": 15, "carbs": 45, "fat": 18},
                    "prep_time": "10 minutes",
                    "difficulty": "Easy"
                },
                {
                    "name": "Vegetable Soup",
                    "ingredients": ["Carrots", "Celery", "Onion", "Tomatoes", "Vegetable broth", "Herbs"],
                    "instructions": ["Sauté vegetables", "Add broth and tomatoes", "Simmer for 20 minutes", "Season with herbs"],
                    "nutrition": {"calories": 150, "protein": 8, "carbs": 25, "fat": 5},
                    "prep_time": "35 minutes",
                    "difficulty": "Easy"
                },
                {
                    "name": "Oatmeal with Berries",
                    "ingredients": ["Oats", "Milk", "Berries", "Honey", "Cinnamon", "Nuts"],
                    "instructions": ["Cook oats with milk", "Top with berries and honey", "Sprinkle with cinnamon and nuts"],
                    "nutrition": {"calories": 320, "protein": 12, "carbs": 45, "fat": 12},
                    "prep_time": "15 minutes",
                    "difficulty": "Easy"
                }
            ]
            
            # Filter recipes based on allergies
            recipes = []
            for recipe in base_recipes:
                if is_allergen_safe(recipe["ingredients"]):
                    recipes.append(recipe)
                else:
                    # Create allergy-safe alternative
                    safe_recipe = recipe.copy()
                    if "gluten" in allergies or "wheat" in allergies:
                        if "Whole wheat tortilla" in safe_recipe["ingredients"]:
                            safe_recipe["ingredients"].remove("Whole wheat tortilla")
                            safe_recipe["ingredients"].append("Gluten-free tortilla")
                    if "dairy" in allergies or "feta cheese" in allergies:
                        if "Feta cheese" in safe_recipe["ingredients"]:
                            safe_recipe["ingredients"].remove("Feta cheese")
                            safe_recipe["ingredients"].append("Nutritional yeast")
                    if "dairy" in allergies or "milk" in allergies:
                        if "Milk" in safe_recipe["ingredients"]:
                            safe_recipe["ingredients"].remove("Milk")
                            safe_recipe["ingredients"].append("Almond milk")
                    if "nuts" in allergies or "almonds" in allergies:
                        if "Nuts" in safe_recipe["ingredients"]:
                            safe_recipe["ingredients"].remove("Nuts")
                            safe_recipe["ingredients"].append("Seeds (sunflower/pumpkin)")
                        if "Almond milk" in safe_recipe["ingredients"]:
                            safe_recipe["ingredients"].remove("Almond milk")
                            safe_recipe["ingredients"].append("Oat milk")
                    
                    recipes.append(safe_recipe)
        
        return {"recipes": recipes}
    
    def generate_workout_plan_ai(self, user_data, available_equipment=None):
        """Generate AI-enhanced workout plan"""
        
        context = f"""
        Create a detailed 7-day workout plan for this user:
        
        User Profile:
        - Age: {user_data.get('age', 'N/A')}
        - Gender: {user_data.get('gender', 'N/A')}
        - Fitness Level: {user_data.get('activity_level', 'N/A')}
        - Goal: {user_data.get('fitness_goal', 'N/A')}
        - Available Equipment: {available_equipment or 'Basic home equipment'}
        
        Requirements:
        - 7 days of workouts
        - Each day should include: day, focus, exercises (with sets/reps), duration, intensity
        - Progressive difficulty
        - Rest days included
        - Equipment considerations
        - Safety tips
        
        Format as JSON with array of workout days, each containing: day, focus, duration, intensity, exercises, instructions, safety_tips
        """
        
        try:
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                json={
                    "contents": [{
                        "parts": [{"text": context}]
                    }]
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    try:
                        parsed_content = json.loads(content)
                        # Ensure we have the workouts array
                        if 'workouts' in parsed_content:
                            return parsed_content
                        elif isinstance(parsed_content, list):
                            return {"workouts": parsed_content}
                        else:
                            return {"workouts": []}
                    except json.JSONDecodeError:
                        print(f"Failed to parse AI response as JSON: {content[:200]}...")
                        return self._get_fallback_workout_plan(user_data)
            else:
                print(f"AI API error: {response.status_code} - {response.text}")
                return self._get_fallback_workout_plan(user_data)
            
            return self._get_fallback_workout_plan(user_data)
        except Exception as e:
            print(f"AI workout error: {e}")
            return self._get_fallback_workout_plan(user_data)
    
    def _get_fallback_workout_plan(self, user_data):
        """Provide fallback workout plan when AI is unavailable"""
        fitness_goal = user_data.get('fitness_goal', 'general_fitness')
        activity_level = user_data.get('activity_level', 'moderate')
        
        if fitness_goal == 'weight_loss':
            focus_areas = ['Cardio', 'Full Body', 'Cardio', 'Strength', 'Cardio', 'Rest', 'Active Recovery']
        elif fitness_goal == 'muscle_gain':
            focus_areas = ['Upper Body', 'Lower Body', 'Rest', 'Full Body', 'Upper Body', 'Lower Body', 'Rest']
        elif fitness_goal == 'endurance':
            focus_areas = ['Cardio', 'Strength', 'Cardio', 'Rest', 'Cardio', 'Strength', 'Active Recovery']
        else:
            focus_areas = ['Full Body', 'Cardio', 'Strength', 'Rest', 'Full Body', 'Cardio', 'Rest']
        
        workouts = []
        for i, focus in enumerate(focus_areas, 1):
            if focus == 'Rest':
                workout = {
                    "day": f"Day {i}",
                    "focus": "Rest Day",
                    "duration": "0 minutes",
                    "intensity": "None",
                    "exercises": ["Complete rest or light stretching"],
                    "instructions": ["Take a complete rest day to allow your body to recover", "Optional: 10-15 minutes of light stretching"],
                    "safety_tips": ["Listen to your body", "Stay hydrated"]
                }
            elif focus == 'Active Recovery':
                workout = {
                    "day": f"Day {i}",
                    "focus": "Active Recovery",
                    "duration": "30 minutes",
                    "intensity": "Low",
                    "exercises": ["Light walking", "Gentle stretching", "Yoga poses"],
                    "instructions": ["Keep intensity very low", "Focus on mobility and flexibility", "No strenuous activity"],
                    "safety_tips": ["Move slowly and mindfully", "Stop if you feel any pain"]
                }
            elif focus == 'Cardio':
                workout = {
                    "day": f"Day {i}",
                    "focus": "Cardiovascular Training",
                    "duration": "45 minutes",
                    "intensity": "Moderate to High",
                    "exercises": ["Running or brisk walking", "Cycling", "Jump rope", "High knees"],
                    "instructions": ["Start with 5-10 minute warm-up", "Maintain steady pace for 25-30 minutes", "Cool down with 5-10 minutes of light activity"],
                    "safety_tips": ["Maintain proper form", "Stay hydrated", "Listen to your body"]
                }
            elif focus == 'Strength':
                workout = {
                    "day": f"Day {i}",
                    "focus": "Strength Training",
                    "duration": "60 minutes",
                    "intensity": "Moderate",
                    "exercises": ["Push-ups", "Squats", "Lunges", "Planks", "Dumbbell rows"],
                    "instructions": ["3 sets of 10-15 reps for each exercise", "Rest 60-90 seconds between sets", "Focus on proper form"],
                    "safety_tips": ["Maintain proper form", "Breathe steadily", "Don't rush through exercises"]
                }
            else:  # Full Body
                workout = {
                    "day": f"Day {i}",
                    "focus": "Full Body Workout",
                    "duration": "45 minutes",
                    "intensity": "Moderate",
                    "exercises": ["Squats", "Push-ups", "Lunges", "Planks", "Burpees", "Mountain climbers"],
                    "instructions": ["2-3 sets of 10-15 reps for each exercise", "Circuit style: move from one exercise to the next", "Rest 30 seconds between circuits"],
                    "safety_tips": ["Maintain proper form", "Modify exercises as needed", "Stay hydrated"]
                }
            
            workouts.append(workout)
        
        return {"workouts": workouts}
    
    def analyze_progress(self, user_data, progress_data):
        """Analyze user progress and provide insights"""
        
        context = f"""
        Analyze this user's fitness progress and provide insights:
        
        User: {user_data.get('age', 'N/A')} year old {user_data.get('gender', 'N/A')}
        Goal: {user_data.get('fitness_goal', 'N/A')}
        
        Progress Data: {progress_data}
        
        Provide:
        1. Progress summary (2-3 sentences)
        2. 2-3 specific insights about their progress
        3. 2 recommendations for improvement
        4. 1 celebration of their achievements
        
        Format as JSON with keys: summary, insights, recommendations, celebration
        """
        
        try:
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                json={
                    "contents": [{
                        "parts": [{"text": context}]
                    }]
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        print(f"Failed to parse AI progress response as JSON: {content[:200]}...")
                        return self._get_fallback_progress(user_data)
            else:
                print(f"AI progress API error: {response.status_code} - {response.text}")
                return self._get_fallback_progress(user_data)
            
            return self._get_fallback_progress(user_data)
        except Exception as e:
            print(f"AI progress analysis error: {e}")
            return self._get_fallback_progress(user_data)
    
    def _get_fallback_progress(self, user_data):
        """Provide fallback progress analysis when AI is unavailable"""
        fitness_goal = user_data.get('fitness_goal', 'general_fitness')
        
        if fitness_goal == 'weight_loss':
            return {
                "summary": "You're making great progress on your weight loss journey! Your consistent efforts are paying off, but remember, gradual and sustainable change is key.",
                "insights": [
                    "Your calorie deficit is well-managed, but consider adjusting your macros slightly for more sustainable results.",
                    "Your strength training is helping to maintain muscle mass, which is crucial for a healthy metabolism.",
                    "Your cardio workouts are effective for burning calories and improving cardiovascular health."
                ],
                "recommendations": [
                    "Continue tracking your food intake and exercise logs to fine-tune your plan.",
                    "Consider incorporating more variety in your workouts to prevent boredom and plateaus.",
                    "Focus on quality sleep and stress management to support your weight loss efforts."
                ],
                "celebration": "You're on the right track! Keep up the great work and celebrate your small victories."
            }
        elif fitness_goal == 'muscle_gain':
            return {
                "summary": "Your muscle gain journey is progressing well! Your strength training and protein intake are working together to build muscle mass.",
                "insights": [
                    "Your progressive overload is effective, but don't forget to allow for adequate recovery.",
                    "Your diet is supporting your muscle growth, but consider increasing your protein intake slightly.",
                    "Your cardio workouts are helping to burn calories and improve overall fitness."
                ],
                "recommendations": [
                    "Continue tracking your progress and adjust your training intensity as needed.",
                    "Focus on proper form and technique to maximize gains.",
                    "Ensure you're getting enough sleep and recovery time."
                ],
                "celebration": "You're doing amazing! Keep pushing towards your muscle gain goals."
            }
        else:  # General fitness
            return {
                "summary": "Your fitness journey is going well! You're consistently working towards your goals and making progress.",
                "insights": [
                    "Your workouts are varied and challenging, which is great for overall fitness.",
                    "Your nutrition is on point, but consider adding more variety to your meals.",
                    "Your recovery is important, so don't push yourself too hard."
                ],
                "recommendations": [
                    "Continue tracking your workouts and nutrition to ensure consistency.",
                    "Focus on finding activities you enjoy to make fitness sustainable.",
                    "Remember to prioritize recovery and listen to your body."
                ],
                "celebration": "You're doing great! Keep up the good work and celebrate your achievements."
            }
    
    def generate_nutrition_advice(self, user_data, recent_meals=None):
        """Generate personalized nutrition advice"""
        
        context = f"""
        Provide personalized nutrition advice for this user:
        
        User Profile:
        - Age: {user_data.get('age', 'N/A')}
        - Gender: {user_data.get('gender', 'N/A')}
        - Height: {user_data.get('height', 'N/A')} cm
        - Weight: {user_data.get('weight', 'N/A')} kg
        - Goal: {user_data.get('fitness_goal', 'N/A')}
        - Allergies: {user_data.get('allergies', 'None')}
        - Region: {user_data.get('region', 'N/A')}
        - Budget: {user_data.get('budget', 'N/A')}
        
        Recent Meals: {recent_meals or 'No recent meal data'}
        
        Provide:
        1. Daily calorie target recommendation
        2. Macro distribution (protein/carbs/fat percentages)
        3. 3 specific nutrition tips
        4. 3 foods to include more of
        5. 3 foods to limit
        6. Meal timing advice
        
        Format as JSON with appropriate keys
        """
        
        try:
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                json={
                    "contents": [{
                        "parts": [{"text": context}]
                    }]
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        print(f"Failed to parse AI nutrition response as JSON: {content[:200]}...")
                        return self._get_fallback_nutrition(user_data)
            else:
                print(f"AI nutrition API error: {response.status_code} - {response.text}")
                return self._get_fallback_nutrition(user_data)
            
            return self._get_fallback_nutrition(user_data)
        except Exception as e:
            print(f"AI nutrition error: {e}")
            return self._get_fallback_nutrition(user_data)
    
    def _get_fallback_nutrition(self, user_data):
        """Provide fallback nutrition advice when AI is unavailable"""
        fitness_goal = user_data.get('fitness_goal', 'general_fitness')
        region = user_data.get('region', 'general').lower()
        
        if fitness_goal == 'weight_loss':
            return {
                "advice": "For weight loss, focus on a moderate calorie deficit and prioritize protein-rich foods. Include plenty of vegetables and lean meats. Avoid processed foods and sugary drinks. Meal timing is important, try to eat smaller, more frequent meals throughout the day."
            }
        elif fitness_goal == 'muscle_gain':
            return {
                "advice": "For muscle gain, prioritize a calorie surplus and focus on high-quality protein sources. Include complex carbs and healthy fats. Incorporate a variety of vegetables and fruits. Meal timing is crucial, aim to consume protein within 30 minutes of waking and carbs within 45 minutes of training."
            }
        else:  # General fitness
            return {
                "advice": "For general fitness, aim for a balanced diet with moderate calories. Include a mix of protein, carbs, and fats. Focus on whole foods and variety. Meal timing is flexible, but try to eat regularly to maintain energy levels."
            }

# Initialize AI enhancements with the provided API key
ai_enhancements = AIEnhancements("AIzaSyCpWlzKyCf4viwjnZjeftqSPtG9O9nnlyY") 