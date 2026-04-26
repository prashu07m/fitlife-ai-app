#!/usr/bin/env python3
"""
Test script for ML Fitness Recommendations
Demonstrates personalized workout and diet plans based on user inputs
"""

from ml_recommendations import recommendation_engine

def test_recommendations():
    """Test the ML recommendation system with sample user data"""
    
    print("🤖 ML FITNESS RECOMMENDATION SYSTEM TEST")
    print("=" * 50)
    
    # Test Case 1: Asian Female, Low Budget, Nut Allergy, Normal BMI
    print("\n📋 TEST CASE 1:")
    print("Region: Asia")
    print("Budget: Low")
    print("Allergies: Nuts")
    print("Gender: Female")
    print("BMI: Normal (22.5)")
    
    user_data_1 = {
        'age': 28,
        'gender': 'female',
        'height': 165,  # cm
        'weight': 61,   # kg (BMI = 22.5 - Normal)
        'activity_level': 'moderately_active',
        'fitness_goal': 'weight_loss',
        'region': 'asia',
        'budget': 'low',
        'allergies': 'nuts'
    }
    
    print("\n🏋️ WORKOUT RECOMMENDATIONS:")
    workout_plan_1 = recommendation_engine.generate_workout_plan(user_data_1)
    print(f"Fitness Level: {workout_plan_1['fitness_level'].title()}")
    print(f"BMI Category: {workout_plan_1['bmi_category'].title()}")
    print(f"Frequency: {workout_plan_1['recommendations']['frequency']}")
    print(f"Duration: {workout_plan_1['recommendations']['duration']}")
    print(f"Intensity: {workout_plan_1['recommendations']['intensity']}")
    
    print("\nCardio Exercises:")
    for exercise in workout_plan_1['recommendations']['cardio']:
        print(f"  ✅ {exercise}")
    
    print("\nStrength Exercises:")
    for exercise in workout_plan_1['recommendations']['strength']:
        print(f"  ✅ {exercise}")
    
    print("\n🍎 DIET RECOMMENDATIONS:")
    diet_plan_1 = recommendation_engine.generate_diet_plan(user_data_1)
    print(f"Daily Calories: {diet_plan_1['daily_calories']}")
    print(f"Diet Type: {diet_plan_1['diet_type'].replace('_', ' ').title()}")
    print(f"BMI Category: {diet_plan_1['bmi_category'].title()}")
    
    print(f"\nMacro Distribution:")
    print(f"  Protein: {diet_plan_1['recommendations']['protein_ratio']*100:.0f}%")
    print(f"  Carbs: {diet_plan_1['recommendations']['carbs_ratio']*100:.0f}%")
    print(f"  Fat: {diet_plan_1['recommendations']['fat_ratio']*100:.0f}%")
    
    print(f"\nRegional Foods (Asia):")
    for food in diet_plan_1['recommendations']['regional_foods']:
        print(f"  ✅ {food}")
    
    print(f"\nBudget-Friendly Proteins:")
    for food in diet_plan_1['recommendations']['budget_foods']['protein']:
        print(f"  ✅ {food}")
    
    print(f"\nSafe Foods (No Nuts):")
    for food in diet_plan_1['recommendations']['safe_foods']:
        print(f"  ✅ {food}")
    
    # Test Case 2: Mediterranean Male, High Budget, No Allergies, Overweight BMI
    print("\n" + "=" * 50)
    print("\n📋 TEST CASE 2:")
    print("Region: Mediterranean")
    print("Budget: High")
    print("Allergies: None")
    print("Gender: Male")
    print("BMI: Overweight (27.5)")
    
    user_data_2 = {
        'age': 35,
        'gender': 'male',
        'height': 180,  # cm
        'weight': 89,   # kg (BMI = 27.5 - Overweight)
        'activity_level': 'sedentary',
        'fitness_goal': 'weight_loss',
        'region': 'mediterranean',
        'budget': 'high',
        'allergies': ''
    }
    
    print("\n🏋️ WORKOUT RECOMMENDATIONS:")
    workout_plan_2 = recommendation_engine.generate_workout_plan(user_data_2)
    print(f"Fitness Level: {workout_plan_2['fitness_level'].title()}")
    print(f"BMI Category: {workout_plan_2['bmi_category'].title()}")
    print(f"Frequency: {workout_plan_2['recommendations']['frequency']}")
    print(f"Duration: {workout_plan_2['recommendations']['duration']}")
    print(f"Intensity: {workout_plan_2['recommendations']['intensity']}")
    
    print("\nCardio Exercises:")
    for exercise in workout_plan_2['recommendations']['cardio']:
        print(f"  ✅ {exercise}")
    
    print("\nStrength Exercises:")
    for exercise in workout_plan_2['recommendations']['strength']:
        print(f"  ✅ {exercise}")
    
    print("\n🍎 DIET RECOMMENDATIONS:")
    diet_plan_2 = recommendation_engine.generate_diet_plan(user_data_2)
    print(f"Daily Calories: {diet_plan_2['daily_calories']}")
    print(f"Diet Type: {diet_plan_2['diet_type'].replace('_', ' ').title()}")
    print(f"BMI Category: {diet_plan_2['bmi_category'].title()}")
    
    print(f"\nMacro Distribution:")
    print(f"  Protein: {diet_plan_2['recommendations']['protein_ratio']*100:.0f}%")
    print(f"  Carbs: {diet_plan_2['recommendations']['carbs_ratio']*100:.0f}%")
    print(f"  Fat: {diet_plan_2['recommendations']['fat_ratio']*100:.0f}%")
    
    print(f"\nRegional Foods (Mediterranean):")
    for food in diet_plan_2['recommendations']['regional_foods']:
        print(f"  ✅ {food}")
    
    print(f"\nPremium Proteins:")
    for food in diet_plan_2['recommendations']['budget_foods']['protein']:
        print(f"  ✅ {food}")
    
    # Test Case 3: North American Female, Medium Budget, Dairy Allergy, Underweight BMI
    print("\n" + "=" * 50)
    print("\n📋 TEST CASE 3:")
    print("Region: North America")
    print("Budget: Medium")
    print("Allergies: Dairy")
    print("Gender: Female")
    print("BMI: Underweight (17.5)")
    
    user_data_3 = {
        'age': 22,
        'gender': 'female',
        'height': 170,  # cm
        'weight': 51,   # kg (BMI = 17.5 - Underweight)
        'activity_level': 'very_active',
        'fitness_goal': 'muscle_gain',
        'region': 'north_america',
        'budget': 'medium',
        'allergies': 'dairy'
    }
    
    print("\n🏋️ WORKOUT RECOMMENDATIONS:")
    workout_plan_3 = recommendation_engine.generate_workout_plan(user_data_3)
    print(f"Fitness Level: {workout_plan_3['fitness_level'].title()}")
    print(f"BMI Category: {workout_plan_3['bmi_category'].title()}")
    print(f"Frequency: {workout_plan_3['recommendations']['frequency']}")
    print(f"Duration: {workout_plan_3['recommendations']['duration']}")
    print(f"Intensity: {workout_plan_3['recommendations']['intensity']}")
    
    print("\nCardio Exercises:")
    for exercise in workout_plan_3['recommendations']['cardio']:
        print(f"  ✅ {exercise}")
    
    print("\nStrength Exercises:")
    for exercise in workout_plan_3['recommendations']['strength']:
        print(f"  ✅ {exercise}")
    
    print("\n🍎 DIET RECOMMENDATIONS:")
    diet_plan_3 = recommendation_engine.generate_diet_plan(user_data_3)
    print(f"Daily Calories: {diet_plan_3['daily_calories']}")
    print(f"Diet Type: {diet_plan_3['diet_type'].replace('_', ' ').title()}")
    print(f"BMI Category: {diet_plan_3['bmi_category'].title()}")
    
    print(f"\nMacro Distribution:")
    print(f"  Protein: {diet_plan_3['recommendations']['protein_ratio']*100:.0f}%")
    print(f"  Carbs: {diet_plan_3['recommendations']['carbs_ratio']*100:.0f}%")
    print(f"  Fat: {diet_plan_3['recommendations']['fat_ratio']*100:.0f}%")
    
    print(f"\nRegional Foods (North America):")
    for food in diet_plan_3['recommendations']['regional_foods']:
        print(f"  ✅ {food}")
    
    print(f"\nSafe Foods (No Dairy):")
    for food in diet_plan_3['recommendations']['safe_foods']:
        print(f"  ✅ {food}")
    
    print("\n" + "=" * 50)
    print("🎉 ML RECOMMENDATION SYSTEM TEST COMPLETED!")
    print("✅ All recommendations generated successfully")
    print("✅ No API keys required - 100% offline functionality")
    print("✅ Personalized based on Region, Budget, Allergies, Gender, and BMI")

if __name__ == "__main__":
    test_recommendations() 