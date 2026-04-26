import sqlite3
from datetime import datetime, timedelta
import numpy as np

DB_NAME = 'fitness_diet.db'

class DataScienceEngine:

    # ---------------------------
    # 1. Health Score (0–100)
    # ---------------------------
    def calculate_health_score(self, user_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        # workouts count
        c.execute("SELECT COUNT(*) FROM workouts WHERE user_id=?", (user_id,))
        workouts = c.fetchone()[0]

        # avg calories intake
        c.execute("SELECT AVG(calories) FROM meals WHERE user_id=?", (user_id,))
        avg_calories = c.fetchone()[0] or 0

        # weight consistency
        c.execute("SELECT weight FROM weight_log WHERE user_id=? ORDER BY date DESC LIMIT 5", (user_id,))
        weights = [w[0] for w in c.fetchall()]

        conn.close()

        score = 50

        # workout scoring
        if workouts > 10:
            score += 20
        elif workouts > 5:
            score += 10

        # calorie balance
        if 1500 < avg_calories < 2500:
            score += 15

        # weight stability
        if len(weights) >= 2:
            diff = abs(weights[0] - weights[-1])
            if diff < 2:
                score += 15

        return min(score, 100)

    # ---------------------------
    # 2. Weight Prediction
    # ---------------------------
    def predict_weight(self, user_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        c.execute("SELECT weight FROM weight_log WHERE user_id=? ORDER BY date ASC", (user_id,))
        weights = [w[0] for w in c.fetchall()]

        conn.close()

        if len(weights) < 2:
            return None

        trend = np.polyfit(range(len(weights)), weights, 1)
        slope = trend[0]

        predicted = weights[-1] + slope * 14  # 2 weeks prediction

        return round(predicted, 1)

    # ---------------------------
    # 3. Insights Generator
    # ---------------------------
    def generate_insights(self, user_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        insights = []

        # workouts
        c.execute("SELECT COUNT(*) FROM workouts WHERE user_id=?", (user_id,))
        workouts = c.fetchone()[0]

        if workouts < 3:
            insights.append("⚠️ Low workout frequency detected")
        else:
            insights.append("✅ Good workout consistency")

        # meals
        c.execute("SELECT AVG(protein) FROM meals WHERE user_id=?", (user_id,))
        protein = c.fetchone()[0] or 0

        if protein < 50:
            insights.append("⚠️ Protein intake is low")
        else:
            insights.append("✅ Protein intake is good")

        conn.close()
        return insights


ds_engine = DataScienceEngine()