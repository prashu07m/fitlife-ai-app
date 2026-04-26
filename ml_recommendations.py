import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
from datetime import datetime
import json

class FitnessRecommendationEngine:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.workout_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.diet_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.user_clusters = None
        self.model_path = 'ml_models/'
        
        # Create models directory if it doesn't exist
        os.makedirs(self.model_path, exist_ok=True)
        
        # Initialize recommendation data
        self._initialize_recommendation_data()
        
    def _initialize_recommendation_data(self):
        """Initialize recommendation data and rules"""
        
        # Workout recommendations based on different factors
        self.workout_recommendations = {
            'beginner': {
                'cardio': ['Walking', 'Light jogging', 'Cycling', 'Swimming'],
                'strength': ['Bodyweight squats', 'Push-ups', 'Planks', 'Wall sits'],
                'flexibility': ['Stretching', 'Yoga basics', 'Pilates'],
                'frequency': '3-4 times per week',
                'duration': '20-30 minutes',
                'intensity': 'Low to moderate'
            },
            'intermediate': {
                'cardio': ['Running', 'HIIT', 'Cycling', 'Rowing'],
                'strength': ['Squats', 'Deadlifts', 'Bench press', 'Pull-ups'],
                'flexibility': ['Dynamic stretching', 'Yoga', 'Mobility work'],
                'frequency': '4-5 times per week',
                'duration': '30-45 minutes',
                'intensity': 'Moderate to high'
            },
            'advanced': {
                'cardio': ['Sprint intervals', 'Advanced HIIT', 'Long-distance running'],
                'strength': ['Olympic lifts', 'Advanced compound movements', 'Powerlifting'],
                'flexibility': ['Advanced yoga', 'Gymnastics', 'Contortion'],
                'frequency': '5-6 times per week',
                'duration': '45-60 minutes',
                'intensity': 'High'
            }
        }
        
        # Diet recommendations based on goals and preferences
        self.diet_recommendations = {
            'weight_loss': {
                'calorie_deficit': 300,
                'protein_ratio': 0.3,
                'carbs_ratio': 0.4,
                'fat_ratio': 0.3,
                'foods': ['Lean proteins', 'Vegetables', 'Whole grains', 'Healthy fats'],
                'avoid': ['Processed foods', 'Sugary drinks', 'Excess carbs']
            },
            'muscle_gain': {
                'calorie_surplus': 200,
                'protein_ratio': 0.35,
                'carbs_ratio': 0.45,
                'fat_ratio': 0.2,
                'foods': ['High-protein foods', 'Complex carbs', 'Healthy fats', 'Protein shakes'],
                'avoid': ['Empty calories', 'Excess fat']
            },
            'maintenance': {
                'calorie_balance': 0,
                'protein_ratio': 0.25,
                'carbs_ratio': 0.45,
                'fat_ratio': 0.3,
                'foods': ['Balanced meals', 'Variety of foods', 'Moderate portions'],
                'avoid': ['Excess calories', 'Unhealthy fats']
            }
        }
        
        # Regional food preferences
        self.regional_foods = {
            'asia': ['Rice', 'Noodles', 'Tofu', 'Fish', 'Vegetables', 'Tea'],
            'europe': ['Bread', 'Pasta', 'Cheese', 'Olive oil', 'Wine', 'Herbs'],
            'north_america': ['Chicken', 'Beef', 'Potatoes', 'Corn', 'Dairy', 'Fast food'],
            'mediterranean': ['Olive oil', 'Fish', 'Nuts', 'Legumes', 'Fruits', 'Vegetables'],
            'africa': ['Grains', 'Legumes', 'Root vegetables', 'Fruits', 'Spices'],
            'south_america': ['Rice', 'Beans', 'Corn', 'Meat', 'Fruits', 'Vegetables']
        }
        
        # Budget-friendly alternatives
        self.budget_alternatives = {
            'protein': {
                'expensive': ['Salmon', 'Tuna', 'Lean beef', 'Chicken breast'],
                'budget': ['Eggs', 'Canned tuna', 'Chicken thighs', 'Legumes', 'Greek yogurt']
            },
            'carbs': {
                'expensive': ['Quinoa', 'Brown rice', 'Sweet potatoes'],
                'budget': ['White rice', 'Potatoes', 'Oats', 'Pasta']
            },
            'fats': {
                'expensive': ['Avocado', 'Nuts', 'Olive oil'],
                'budget': ['Peanut butter', 'Sunflower seeds', 'Vegetable oil']
            }
        }
        
    def calculate_bmi_category(self, height, weight):
        """Calculate BMI and return category"""
        if height <= 0 or weight <= 0:
            return 'unknown'
        
        height_m = height / 100
        bmi = weight / (height_m ** 2)
        
        if bmi < 18.5:
            return 'underweight'
        elif bmi < 25:
            return 'normal'
        elif bmi < 30:
            return 'overweight'
        else:
            return 'obese'
    
    def determine_fitness_level(self, age, activity_level, bmi_category):
        """Determine user's fitness level"""
        if activity_level == 'sedentary' or age > 60:
            return 'beginner'
        elif activity_level in ['lightly_active', 'moderately_active']:
            return 'intermediate'
        else:
            return 'advanced'
    
    def generate_workout_plan(self, user_data):
        """Generate personalized workout plan using ML"""
        
        # Extract user features
        age = user_data.get('age', 30)
        gender = user_data.get('gender', 'other')
        height = user_data.get('height', 170)
        weight = user_data.get('weight', 70)
        activity_level = user_data.get('activity_level', 'moderately_active')
        fitness_goal = user_data.get('fitness_goal', 'general_fitness')
        
        # Calculate BMI category
        bmi_category = self.calculate_bmi_category(height, weight)
        
        # Determine fitness level
        fitness_level = self.determine_fitness_level(age, activity_level, bmi_category)
        
        # Get base recommendations
        base_recommendations = self.workout_recommendations[fitness_level]
        
        # Customize based on gender
        if gender == 'female':
            base_recommendations['strength'].extend(['Glute bridges', 'Hip thrusts', 'Lunges'])
            base_recommendations['flexibility'].extend(['Hip flexor stretches', 'Core work'])
        elif gender == 'male':
            base_recommendations['strength'].extend(['Deadlifts', 'Bench press', 'Military press'])
        
        # Customize based on fitness goal
        if fitness_goal == 'weight_loss':
            base_recommendations['cardio'].extend(['Circuit training', 'Tabata'])
            base_recommendations['frequency'] = '5-6 times per week'
            base_recommendations['duration'] = '45-60 minutes'
        elif fitness_goal == 'muscle_gain':
            base_recommendations['strength'].extend(['Progressive overload', 'Compound movements'])
            base_recommendations['frequency'] = '4-5 times per week'
            base_recommendations['duration'] = '45-60 minutes'
        elif fitness_goal == 'endurance':
            base_recommendations['cardio'].extend(['Long-distance running', 'Cycling', 'Swimming'])
            base_recommendations['frequency'] = '5-6 times per week'
            base_recommendations['duration'] = '60+ minutes'
        
        # Customize based on BMI
        if bmi_category == 'underweight':
            base_recommendations['strength'].extend(['Compound movements', 'Progressive overload'])
            base_recommendations['frequency'] = '4-5 times per week'
        elif bmi_category == 'overweight' or bmi_category == 'obese':
            base_recommendations['cardio'].extend(['Low-impact cardio', 'Walking', 'Swimming'])
            base_recommendations['frequency'] = '5-6 times per week'
        
        return {
            'fitness_level': fitness_level,
            'bmi_category': bmi_category,
            'recommendations': base_recommendations,
            'weekly_schedule': self._generate_weekly_schedule(base_recommendations, fitness_goal)
        }
    
    def _generate_weekly_schedule(self, recommendations, fitness_goal):
        """Generate weekly workout schedule"""
        schedule = {
            'monday': {'type': 'strength', 'focus': 'Upper body'},
            'tuesday': {'type': 'cardio', 'focus': 'HIIT'},
            'wednesday': {'type': 'strength', 'focus': 'Lower body'},
            'thursday': {'type': 'cardio', 'focus': 'Steady state'},
            'friday': {'type': 'strength', 'focus': 'Full body'},
            'saturday': {'type': 'flexibility', 'focus': 'Recovery'},
            'sunday': {'type': 'rest', 'focus': 'Rest day'}
        }
        
        if fitness_goal == 'weight_loss':
            schedule['saturday'] = {'type': 'cardio', 'focus': 'Long duration'}
        elif fitness_goal == 'muscle_gain':
            schedule['saturday'] = {'type': 'strength', 'focus': 'Accessory work'}
        
        return schedule
    
    def generate_diet_plan(self, user_data):
        """Generate personalized diet plan using ML"""
        
        # Extract user features
        age = user_data.get('age', 30)
        gender = user_data.get('gender', 'other')
        height = user_data.get('height', 170)
        weight = user_data.get('weight', 70)
        activity_level = user_data.get('activity_level', 'moderately_active')
        fitness_goal = user_data.get('fitness_goal', 'maintenance')
        region = user_data.get('region', 'north_america')
        budget = user_data.get('budget', 'medium')
        allergies = user_data.get('allergies', '').lower().split(',') if user_data.get('allergies') else []
        
        # Calculate BMI category
        bmi_category = self.calculate_bmi_category(height, weight)
        
        # Get base diet recommendations
        if fitness_goal == 'weight_loss':
            diet_type = 'weight_loss'
        elif fitness_goal == 'muscle_gain':
            diet_type = 'muscle_gain'
        else:
            diet_type = 'maintenance'
        
        base_recommendations = self.diet_recommendations[diet_type].copy()
        
        # Calculate daily calorie needs
        daily_calories = self._calculate_daily_calories(age, gender, height, weight, activity_level, fitness_goal)
        
        # Customize based on region
        regional_foods = self.regional_foods.get(region, self.regional_foods['north_america'])
        base_recommendations['regional_foods'] = regional_foods
        
        # Customize based on budget
        budget_foods = self._get_budget_foods(budget)
        base_recommendations['budget_foods'] = budget_foods
        
        # Handle allergies
        safe_foods = self._filter_allergies(base_recommendations['foods'], allergies)
        base_recommendations['safe_foods'] = safe_foods
        
        # Generate meal plan
        meal_plan = self._generate_meal_plan(daily_calories, base_recommendations, regional_foods, budget_foods, allergies)
        
        return {
            'daily_calories': daily_calories,
            'diet_type': diet_type,
            'bmi_category': bmi_category,
            'recommendations': base_recommendations,
            'meal_plan': meal_plan
        }
    
    def _calculate_daily_calories(self, age, gender, height, weight, activity_level, fitness_goal):
        """Calculate daily calorie needs using Harris-Benedict equation"""
        
        # BMR calculation
        if gender == 'male':
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        
        # Activity multiplier
        activity_multipliers = {
            'sedentary': 1.2,
            'lightly_active': 1.375,
            'moderately_active': 1.55,
            'very_active': 1.725,
            'extremely_active': 1.9
        }
        
        multiplier = activity_multipliers.get(activity_level, 1.55)
        maintenance_calories = bmr * multiplier
        
        # Adjust based on fitness goal
        if fitness_goal == 'weight_loss':
            daily_calories = maintenance_calories - 300
        elif fitness_goal == 'muscle_gain':
            daily_calories = maintenance_calories + 200
        else:
            daily_calories = maintenance_calories
        
        return round(daily_calories)
    
    def _get_budget_foods(self, budget):
        """Get budget-appropriate food alternatives"""
        if budget == 'low':
            return {
                'protein': self.budget_alternatives['protein']['budget'],
                'carbs': self.budget_alternatives['carbs']['budget'],
                'fats': self.budget_alternatives['fats']['budget']
            }
        else:
            return {
                'protein': self.budget_alternatives['protein']['expensive'],
                'carbs': self.budget_alternatives['carbs']['expensive'],
                'fats': self.budget_alternatives['fats']['expensive']
            }
    
    def _filter_allergies(self, foods, allergies):
        """Filter out foods that contain allergens"""
        if not allergies or all(allergy.strip() in ['none', 'no', 'n/a', ''] for allergy in allergies):
            return foods
            
        # Common allergens mapping
        allergen_mapping = {
            'nuts': ['peanuts', 'almonds', 'walnuts', 'cashews', 'pistachios', 'hazelnuts', 'pecans', 'macadamia nuts', 'nut', 'nuts'],
            'dairy': ['milk', 'cheese', 'yogurt', 'butter', 'cream', 'whey', 'casein', 'dairy'],
            'eggs': ['eggs', 'egg whites', 'egg yolks', 'egg'],
            'gluten': ['wheat', 'gluten', 'barley', 'rye', 'bread', 'pasta', 'flour'],
            'soy': ['soy', 'soybeans', 'tofu', 'soy sauce', 'edamame'],
            'shellfish': ['shrimp', 'crab', 'lobster', 'oysters', 'mussels', 'clams', 'shellfish'],
            'fish': ['fish', 'salmon', 'tuna', 'cod', 'tilapia', 'mackerel', 'seafood']
        }
        
        safe_foods = []
        for food in foods:
            is_safe = True
            food_lower = food.lower()
            
            for allergy in allergies:
                allergy = allergy.strip().lower()
                
                # Check direct match
                if allergy in food_lower:
                    is_safe = False
                    break
                
                # Check allergen mapping
                for allergen_type, allergen_list in allergen_mapping.items():
                    if allergy in allergen_type or allergy in allergen_list:
                        if any(allergen in food_lower for allergen in allergen_list):
                            is_safe = False
                            break
                
                if not is_safe:
                    break
                    
            if is_safe:
                safe_foods.append(food)
        
        return safe_foods
    
    def is_recipe_allergy_safe(self, recipe_ingredients, allergies):
        """Check if a recipe is safe for user's allergies"""
        if not allergies or all(allergy.strip() in ['none', 'no', 'n/a', ''] for allergy in allergies):
            return True
            
        # Common allergens mapping
        allergen_mapping = {
            'nuts': ['peanuts', 'almonds', 'walnuts', 'cashews', 'pistachios', 'hazelnuts', 'pecans', 'macadamia nuts', 'nut', 'nuts'],
            'dairy': ['milk', 'cheese', 'yogurt', 'butter', 'cream', 'whey', 'casein', 'dairy'],
            'eggs': ['eggs', 'egg whites', 'egg yolks', 'egg'],
            'gluten': ['wheat', 'gluten', 'barley', 'rye', 'bread', 'pasta', 'flour'],
            'soy': ['soy', 'soybeans', 'tofu', 'soy sauce', 'edamame'],
            'shellfish': ['shrimp', 'crab', 'lobster', 'oysters', 'mussels', 'clams', 'shellfish'],
            'fish': ['fish', 'salmon', 'tuna', 'cod', 'tilapia', 'mackerel', 'seafood']
        }
        
        for ingredient in recipe_ingredients:
            ingredient_lower = ingredient.lower()
            
            for allergy in allergies:
                allergy = allergy.strip().lower()
                
                # Check direct match
                if allergy in ingredient_lower:
                    return False
                
                # Check allergen mapping
                for allergen_type, allergen_list in allergen_mapping.items():
                    if allergy in allergen_type or allergy in allergen_list:
                        if any(allergen in ingredient_lower for allergen in allergen_list):
                            return False
        
        return True
    
    def _generate_meal_plan(self, daily_calories, recommendations, regional_foods, budget_foods, allergies):
        """Generate daily meal plan"""
        
        # Calculate macro distribution
        protein_calories = daily_calories * recommendations['protein_ratio']
        carbs_calories = daily_calories * recommendations['carbs_ratio']
        fat_calories = daily_calories * recommendations['fat_ratio']
        
        # Convert to grams
        protein_grams = round(protein_calories / 4)
        carbs_grams = round(carbs_calories / 4)
        fat_grams = round(fat_calories / 9)
        
        meal_plan = {
            'breakfast': {
                'calories': round(daily_calories * 0.25),
                'protein': round(protein_grams * 0.25),
                'carbs': round(carbs_grams * 0.25),
                'fat': round(fat_grams * 0.25),
                'suggestions': self._get_meal_suggestions('breakfast', regional_foods, budget_foods, allergies)
            },
            'lunch': {
                'calories': round(daily_calories * 0.35),
                'protein': round(protein_grams * 0.35),
                'carbs': round(carbs_grams * 0.35),
                'fat': round(fat_grams * 0.35),
                'suggestions': self._get_meal_suggestions('lunch', regional_foods, budget_foods, allergies)
            },
            'dinner': {
                'calories': round(daily_calories * 0.30),
                'protein': round(protein_grams * 0.30),
                'carbs': round(carbs_grams * 0.30),
                'fat': round(fat_grams * 0.30),
                'suggestions': self._get_meal_suggestions('dinner', regional_foods, budget_foods, allergies)
            },
            'snacks': {
                'calories': round(daily_calories * 0.10),
                'protein': round(protein_grams * 0.10),
                'carbs': round(carbs_grams * 0.10),
                'fat': round(fat_grams * 0.10),
                'suggestions': self._get_meal_suggestions('snacks', regional_foods, budget_foods, allergies)
            }
        }
        
        return meal_plan
    
    def _get_meal_suggestions(self, meal_type, regional_foods, budget_foods, allergies):
        """Get meal suggestions based on type and preferences"""
        
        # Base suggestions with allergy alternatives
        base_suggestions = {
            'breakfast': [
                'Oatmeal with fruits and nuts',
                'Greek yogurt with berries',
                'Eggs with whole grain toast',
                'Smoothie with protein powder',
                'Avocado toast',
                'Chia pudding with fruits',
                'Protein pancakes',
                'Fruit and seed bowl'
            ],
            'lunch': [
                'Grilled chicken salad',
                'Quinoa bowl with vegetables',
                'Turkey sandwich on whole grain bread',
                'Lentil soup with vegetables',
                'Tuna salad with mixed greens',
                'Chickpea salad wrap',
                'Vegetable stir-fry with rice',
                'Bean and vegetable soup'
            ],
            'dinner': [
                'Salmon with roasted vegetables',
                'Lean beef stir-fry with brown rice',
                'Chicken breast with sweet potato',
                'Vegetarian chili with beans',
                'Grilled fish with quinoa',
                'Lentil curry with rice',
                'Roasted vegetables with quinoa',
                'Chicken and vegetable soup'
            ],
            'snacks': [
                'Apple with peanut butter',
                'Greek yogurt with nuts',
                'Carrot sticks with hummus',
                'Protein shake',
                'Mixed nuts and dried fruits',
                'Fruit with seeds',
                'Vegetable sticks with dip',
                'Rice cakes with avocado'
            ]
        }
        
        # Allergy-safe alternatives
        allergy_alternatives = {
            'nuts': {
                'Oatmeal with fruits and nuts': 'Oatmeal with fruits and seeds',
                'Apple with peanut butter': 'Apple with sunflower seed butter',
                'Greek yogurt with nuts': 'Greek yogurt with seeds',
                'Mixed nuts and dried fruits': 'Mixed seeds and dried fruits',
                'Avocado toast': 'Avocado toast (no nuts)'
            },
            'dairy': {
                'Greek yogurt with berries': 'Coconut yogurt with berries',
                'Greek yogurt with nuts': 'Coconut yogurt with seeds',
                'Cheese in any meal': 'Nutritional yeast or avocado'
            },
            'eggs': {
                'Eggs with whole grain toast': 'Tofu scramble with whole grain toast',
                'Protein pancakes': 'Chickpea flour pancakes'
            },
            'gluten': {
                'Turkey sandwich on whole grain bread': 'Turkey lettuce wrap',
                'Whole grain toast': 'Gluten-free bread or rice cakes'
            },
            'fish': {
                'Salmon with roasted vegetables': 'Chicken with roasted vegetables',
                'Tuna salad with mixed greens': 'Chickpea salad with mixed greens',
                'Grilled fish with quinoa': 'Grilled chicken with quinoa'
            },
            'soy': {
                'Tofu scramble': 'Chickpea scramble',
                'Soy sauce': 'Coconut aminos'
            }
        }
        
        # Get base suggestions
        suggestions = base_suggestions.get(meal_type, [])
        
        # Filter and replace based on allergies
        safe_suggestions = []
        for suggestion in suggestions:
            modified_suggestion = suggestion
            
            # Check if suggestion contains allergens
            for allergy in allergies:
                allergy = allergy.strip().lower()
                
                # Apply allergy alternatives
                for allergen_type, alternatives in allergy_alternatives.items():
                    if allergy in allergen_type or any(allergen in allergy for allergen in allergen_type.split()):
                        for original, alternative in alternatives.items():
                            if original.lower() in modified_suggestion.lower():
                                modified_suggestion = modified_suggestion.replace(original, alternative)
                                break
            
            # Final safety check
            is_safe = True
            for allergy in allergies:
                allergy = allergy.strip().lower()
                if allergy in modified_suggestion.lower():
                    is_safe = False
                    break
            
            if is_safe:
                safe_suggestions.append(modified_suggestion)
        
        return safe_suggestions[:3]  # Return top 3 suggestions
    
    def save_models(self):
        """Save trained models"""
        joblib.dump(self.scaler, os.path.join(self.model_path, 'scaler.pkl'))
        joblib.dump(self.workout_classifier, os.path.join(self.model_path, 'workout_classifier.pkl'))
        joblib.dump(self.diet_classifier, os.path.join(self.model_path, 'diet_classifier.pkl'))
        
    def load_models(self):
        """Load trained models"""
        try:
            self.scaler = joblib.load(os.path.join(self.model_path, 'scaler.pkl'))
            self.workout_classifier = joblib.load(os.path.join(self.model_path, 'workout_classifier.pkl'))
            self.diet_classifier = joblib.load(os.path.join(self.model_path, 'diet_classifier.pkl'))
            return True
        except:
            return False

# Initialize the recommendation engine
recommendation_engine = FitnessRecommendationEngine() 