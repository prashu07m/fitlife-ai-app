from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from data_science import ds_engine
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json

# Import ML recommendation engine
try:
    from ml_recommendations import recommendation_engine
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("ML recommendations not available. Install scikit-learn for advanced features.")

# Import AI enhancements
try:
    from ai_enhancements import ai_enhancements
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("AI enhancements not available. Install requests for advanced AI features.")

def check_recipe_allergy_safety(recipe_ingredients, user_allergies):
    """Check if a recipe is safe for user's allergies and return safety status"""
    if not user_allergies or user_allergies.lower() in ['none', 'no', 'n/a', '']:
        return {'safe': True, 'warnings': [], 'allergens_found': []}
    
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
    
    user_allergies_lower = user_allergies.lower()
    allergens_found = []
    warnings = []
    
    for ingredient in recipe_ingredients:
        ingredient_lower = ingredient.lower()
        
        # Check direct match
        if user_allergies_lower in ingredient_lower:
            allergens_found.append(ingredient)
            warnings.append(f"Contains {ingredient} (allergen: {user_allergies_lower})")
        
        # Check allergen mapping
        for allergen_type, allergen_list in allergen_mapping.items():
            if any(allergen in user_allergies_lower for allergen in allergen_list):
                if any(allergen in ingredient_lower for allergen in allergen_list):
                    allergens_found.append(ingredient)
                    warnings.append(f"Contains {ingredient} (allergen: {allergen_type})")
    
    return {
        'safe': len(allergens_found) == 0,
        'warnings': warnings,
        'allergens_found': allergens_found
    }

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure random value
DB_NAME = 'fitness_diet.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Enhanced users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT,
        region TEXT,
        budget TEXT,
        allergies TEXT,
        gender TEXT,
        height REAL,
        weight REAL,
        age INTEGER,
        activity_level TEXT,
        fitness_goal TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Enhanced workouts table
    c.execute('''CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        workout_type TEXT,
        duration INTEGER,
        calories_burned INTEGER,
        exercises TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # Enhanced meals table
    c.execute('''CREATE TABLE IF NOT EXISTS meals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        meal_type TEXT,
        food_name TEXT,
        calories INTEGER,
        protein REAL,
        carbs REAL,
        fat REAL,
        fiber REAL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # New goals table
    c.execute('''CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        goal_type TEXT,
        target_value REAL,
        current_value REAL,
        target_date TEXT,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # New achievements table
    c.execute('''CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        achievement_type TEXT,
        title TEXT,
        description TEXT,
        earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # New weight tracking table
    c.execute('''CREATE TABLE IF NOT EXISTS weight_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        weight REAL,
        date TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    conn.commit()
    conn.close()

def ensure_db_compatibility():
    """Ensure database is compatible with current schema"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Check if users table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not c.fetchone():
            # Table doesn't exist, create it
            init_db()
        else:
            # Check if all required columns exist
            c.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in c.fetchall()]
            required_columns = ['id', 'username', 'password', 'email', 'region', 'budget', 'allergies', 'gender', 'height', 'weight', 'age', 'activity_level', 'fitness_goal', 'created_at']
            
            for column in required_columns:
                if column not in columns:
                    if column == 'email':
                        c.execute('ALTER TABLE users ADD COLUMN email TEXT')
                    elif column == 'age':
                        c.execute('ALTER TABLE users ADD COLUMN age INTEGER')
                    elif column == 'activity_level':
                        c.execute('ALTER TABLE users ADD COLUMN activity_level TEXT')
                    elif column == 'fitness_goal':
                        c.execute('ALTER TABLE users ADD COLUMN fitness_goal TEXT')
                    elif column == 'created_at':
                        c.execute('ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
                    conn.commit()
    except Exception as e:
        print(f"Database compatibility error: {e}")
        # If there's an error, recreate the database
        c.execute("DROP TABLE IF EXISTS users")
        c.execute("DROP TABLE IF EXISTS workouts")
        c.execute("DROP TABLE IF EXISTS meals")
        c.execute("DROP TABLE IF EXISTS goals")
        c.execute("DROP TABLE IF EXISTS achievements")
        c.execute("DROP TABLE IF EXISTS weight_log")
        conn.commit()
        init_db()
    finally:
        conn.close()

def check_and_fix_database_schema():
    """Check and fix database schema to ensure all required columns exist"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Check if users table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not c.fetchone():
            print("Users table doesn't exist, creating it...")
            init_db()
            return
        
        # Get current columns
        c.execute("PRAGMA table_info(users)")
        current_columns = [column[1] for column in c.fetchall()]
        print(f"Current columns in users table: {current_columns}")
        
        # Required columns
        required_columns = {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'username': 'TEXT UNIQUE NOT NULL',
            'password': 'TEXT NOT NULL',
            'email': 'TEXT',
            'region': 'TEXT',
            'budget': 'TEXT',
            'allergies': 'TEXT',
            'gender': 'TEXT',
            'height': 'REAL',
            'weight': 'REAL',
            'age': 'INTEGER',
            'activity_level': 'TEXT',
            'fitness_goal': 'TEXT',
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        }
        
        # Check for missing columns and add them
        for column_name, column_type in required_columns.items():
            if column_name not in current_columns:
                print(f"Adding missing column: {column_name}")
                try:
                    c.execute(f'ALTER TABLE users ADD COLUMN {column_name} {column_type}')
                    conn.commit()
                    print(f"Successfully added column: {column_name}")
                except Exception as e:
                    print(f"Error adding column {column_name}: {e}")
        
        # Verify final schema
        c.execute("PRAGMA table_info(users)")
        final_columns = [column[1] for column in c.fetchall()]
        print(f"Final columns in users table: {final_columns}")
        
    except Exception as e:
        print(f"Database schema check error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

# Call this function after init_db
init_db()
ensure_db_compatibility()
check_and_fix_database_schema()

@app.route('/debug_user_data')
def debug_user_data():
    """Debug route to check current user data"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'})
    
    user_id = session['user_id']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Get all user data
        c.execute('SELECT * FROM users WHERE id=?', (user_id,))
        user_data = c.fetchone()
        
        # Get column names
        c.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in c.fetchall()]
        
        # Create a dictionary with column names and values
        user_dict = {}
        if user_data:
            for i, column in enumerate(columns):
                user_dict[column] = user_data[i]
        
        # Also get the specific fields used in AI validation
        c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
        ai_fields = c.fetchone()
        
        return jsonify({
            'user_id': user_id,
            'columns': columns,
            'user_data': user_dict,
            'ai_fields': ai_fields,
            'ai_field_names': ['region', 'budget', 'allergies', 'gender', 'height', 'weight', 'age', 'activity_level', 'fitness_goal']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access your dashboard.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Get user stats
    c.execute('SELECT height, weight, gender, age FROM users WHERE id = ?', (user_id,))
    user_data = c.fetchone()
    
    # Get recent workouts
    c.execute('''SELECT date, workout_type, duration, calories_burned 
                 FROM workouts WHERE user_id = ? ORDER BY date DESC LIMIT 5''', (user_id,))
    recent_workouts = c.fetchall()
    
    # Get recent meals
    c.execute('''SELECT date, meal_type, food_name, calories 
                 FROM meals WHERE user_id = ? ORDER BY date DESC LIMIT 5''', (user_id,))
    recent_meals = c.fetchall()
    
    # Get weight progress (last 7 entries)
    c.execute('''SELECT date, weight FROM weight_log 
                 WHERE user_id = ? ORDER BY date DESC LIMIT 7''', (user_id,))
    weight_data = c.fetchall()
    
    # Calculate stats
    total_workouts = c.execute('SELECT COUNT(*) FROM workouts WHERE user_id = ?', (user_id,)).fetchone()[0]
    total_calories_burned = c.execute('SELECT SUM(calories_burned) FROM workouts WHERE user_id = ?', (user_id,)).fetchone()[0] or 0
    total_meals = c.execute('SELECT COUNT(*) FROM meals WHERE user_id = ?', (user_id,)).fetchone()[0]
    total_calories_consumed = c.execute('SELECT SUM(calories) FROM meals WHERE user_id = ?', (user_id,)).fetchone()[0] or 0
    
    # Get active goals
    c.execute('''SELECT goal_type, target_value, current_value, target_date 
                 FROM goals WHERE user_id = ? AND status = 'active' ''', (user_id,))
    active_goals = c.fetchall()
    
    conn.close()
    
    # Calculate BMI
    bmi = None
    if user_data and user_data[0] and user_data[1]:
        try:
            bmi = round(float(user_data[1]) / ((float(user_data[0])/100) ** 2), 1)
        except:
            bmi = None
    
    return render_template('dashboard.html', 
                         user_data=user_data, 
                         recent_workouts=recent_workouts,
                         recent_meals=recent_meals,
                         weight_data=weight_data,
                         total_workouts=total_workouts,
                         total_calories_burned=total_calories_burned,
                         total_meals=total_meals,
                         total_calories_consumed=total_calories_consumed,
                         active_goals=active_goals,
                         bmi=bmi)

@app.route('/fitness', methods=['GET', 'POST'])
def fitness():
    if 'user_id' not in session:
        flash('Please log in to access fitness tracking.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        workout_type = request.form['workout_type']
        duration = int(request.form['duration'])
        calories_burned = int(request.form['calories_burned'])
        exercises = request.form.get('exercises', '')
        notes = request.form.get('notes', '')
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''INSERT INTO workouts (user_id, date, workout_type, duration, calories_burned, exercises, notes)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                  (user_id, date, workout_type, duration, calories_burned, exercises, notes))
        conn.commit()
        conn.close()
        
        flash('Workout logged successfully!', 'success')
        return redirect(url_for('fitness'))
    
    # Get workout history
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT date, workout_type, duration, calories_burned, exercises, notes 
                 FROM workouts WHERE user_id = ? ORDER BY date DESC''', (user_id,))
    workouts = c.fetchall()
    conn.close()
    
    return render_template('fitness.html', workouts=workouts, today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/diet', methods=['GET', 'POST'])
def diet():
    if 'user_id' not in session:
        flash('Please log in to access diet tracking.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        meal_type = request.form['meal_type']
        food_name = request.form['food_name']
        calories = int(request.form['calories'])
        protein = float(request.form.get('protein', 0))
        carbs = float(request.form.get('carbs', 0))
        fat = float(request.form.get('fat', 0))
        fiber = float(request.form.get('fiber', 0))
        notes = request.form.get('notes', '')
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''INSERT INTO meals (user_id, date, meal_type, food_name, calories, protein, carbs, fat, fiber, notes)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                  (user_id, date, meal_type, food_name, calories, protein, carbs, fat, fiber, notes))
        conn.commit()
        conn.close()
        
        flash('Meal logged successfully!', 'success')
        return redirect(url_for('diet'))
    
    # Get meal history
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT date, meal_type, food_name, calories, protein, carbs, fat, fiber, notes 
                 FROM meals WHERE user_id = ? ORDER BY date DESC''', (user_id,))
    meals = c.fetchall()
    conn.close()
    
    return render_template('diet.html', meals=meals, today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/goals', methods=['GET', 'POST'])
def goals():
    if 'user_id' not in session:
        flash('Please log in to access goals.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        try:
            goal_type = request.form['goal_type']
            target_value = float(request.form['target_value'])
            current_value = float(request.form.get('current_value', 0))
            target_date = request.form['target_date']
            
            # Validate inputs
            if target_value <= 0:
                flash('Target value must be greater than 0.', 'danger')
                return redirect(url_for('goals'))
            
            if current_value < 0:
                flash('Current value cannot be negative.', 'danger')
                return redirect(url_for('goals'))
            
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute('''INSERT INTO goals (user_id, goal_type, target_value, current_value, target_date)
                         VALUES (?, ?, ?, ?, ?)''', 
                      (user_id, goal_type, target_value, current_value, target_date))
            conn.commit()
            conn.close()
            
            flash('Goal set successfully!', 'success')
            return redirect(url_for('goals'))
        except ValueError:
            flash('Please enter valid numbers for target and current values.', 'danger')
            return redirect(url_for('goals'))
        except Exception as e:
            flash(f'Error setting goal: {str(e)}', 'danger')
            return redirect(url_for('goals'))
    
    # Get goals
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''SELECT id, goal_type, target_value, current_value, target_date, status 
                     FROM goals WHERE user_id = ? ORDER BY created_at DESC''', (user_id,))
        goals = c.fetchall()
        conn.close()
    except Exception as e:
        flash(f'Error loading goals: {str(e)}', 'danger')
        goals = []
    
    return render_template('goals.html', goals=goals)

@app.route('/update_goal/<int:goal_id>', methods=['POST'])
def update_goal(goal_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        user_id = session['user_id']
        current_value = float(request.form['current_value'])
        
        # Validate input
        if current_value < 0:
            return jsonify({'error': 'Current value cannot be negative'}), 400
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Check if goal exists and belongs to user
        c.execute('SELECT id FROM goals WHERE id = ? AND user_id = ?', (goal_id, user_id))
        if not c.fetchone():
            conn.close()
            return jsonify({'error': 'Goal not found'}), 404
        
        # Update the goal
        c.execute('UPDATE goals SET current_value = ? WHERE id = ? AND user_id = ?', 
                  (current_value, goal_id, user_id))
        
        # Check if goal is completed
        c.execute('SELECT target_value FROM goals WHERE id = ? AND user_id = ?', (goal_id, user_id))
        target_value = c.fetchone()[0]
        
        if current_value >= target_value:
            c.execute('UPDATE goals SET status = ? WHERE id = ? AND user_id = ?', 
                      ('completed', goal_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except ValueError:
        return jsonify({'error': 'Invalid current value'}), 400
    except Exception as e:
        return jsonify({'error': f'Update failed: {str(e)}'}), 500

@app.route('/weight_log', methods=['GET', 'POST'])
def weight_log():
    if 'user_id' not in session:
        flash('Please log in to access weight tracking.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        weight = float(request.form['weight'])
        notes = request.form.get('notes', '')
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('INSERT INTO weight_log (user_id, weight, date, notes) VALUES (?, ?, ?, ?)', 
                  (user_id, weight, date, notes))
        conn.commit()
        conn.close()
        
        flash('Weight logged successfully!', 'success')
        return redirect(url_for('weight_log'))
    
    # Get weight history
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT date, weight, notes FROM weight_log WHERE user_id = ? ORDER BY date DESC', (user_id,))
    weight_logs = c.fetchall()
    conn.close()
    
    return render_template('weight_log.html', weight_logs=weight_logs, today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email', '')
        hashed_pw = generate_password_hash(password)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', (username, hashed_pw, email))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'danger')
        except Exception as e:
            flash(f'Registration error: {str(e)}', 'danger')
            print(f"Registration error: {e}")
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT id, password FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Please log in to access your profile.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    print(f"Profile route accessed for user {user_id}")
    
    if request.method == 'POST':
        print("Profile POST request received")
        print(f"Form data: {request.form}")
        
        try:
            # Get form data with proper validation
            region = request.form.get('region', '').strip()
            budget = request.form.get('budget', '').strip()
            allergies = request.form.get('allergies', '').strip()
            gender = request.form.get('gender', '').strip()
            
            # Validate numeric inputs
            try:
                height = float(request.form.get('height', 0)) if request.form.get('height') else 0
                weight = float(request.form.get('weight', 0)) if request.form.get('weight') else 0
                age = int(request.form.get('age', 0)) if request.form.get('age') else 0
            except (ValueError, TypeError) as e:
                print(f"Validation error: {e}")
                flash('Please enter valid numbers for height, weight, and age.', 'danger')
                return redirect(url_for('profile'))
            
            activity_level = request.form.get('activity_level', '').strip()
            fitness_goal = request.form.get('fitness_goal', '').strip()
            
            print(f"Processed form data:")
            print(f"  Region: {region}")
            print(f"  Budget: {budget}")
            print(f"  Allergies: {allergies}")
            print(f"  Gender: {gender}")
            print(f"  Height: {height}")
            print(f"  Weight: {weight}")
            print(f"  Age: {age}")
            print(f"  Activity Level: {activity_level}")
            print(f"  Fitness Goal: {fitness_goal}")
            
            # Validate required fields
            required_fields = {
                'gender': gender,
                'age': age,
                'height': height,
                'weight': weight,
                'activity_level': activity_level,
                'fitness_goal': fitness_goal,
                'region': region,
                'budget': budget
            }
            
            missing_fields = [field for field, value in required_fields.items() if not value]
            if missing_fields:
                print(f"Missing fields: {missing_fields}")
                flash(f'Please fill in all required fields: {", ".join(missing_fields)}', 'danger')
                return redirect(url_for('profile'))
            
            # Validate ranges
            if age < 13 or age > 120:
                flash('Age must be between 13 and 120.', 'danger')
                return redirect(url_for('profile'))
            
            if height < 100 or height > 250:
                flash('Height must be between 100 and 250 cm.', 'danger')
                return redirect(url_for('profile'))
            
            if weight < 30 or weight > 300:
                flash('Weight must be between 30 and 300 kg.', 'danger')
                return redirect(url_for('profile'))
            
            # Connect to database and update
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            
            # First, let's check current data
            c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
            current_data = c.fetchone()
            print(f"Current data in database: {current_data}")
            
            # Update the user profile
            update_query = '''UPDATE users SET 
                             region=?, budget=?, allergies=?, gender=?, height=?, weight=?, age=?, activity_level=?, fitness_goal=? 
                             WHERE id=?'''
            update_values = (region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal, user_id)
            
            print(f"Executing update query: {update_query}")
            print(f"Update values: {update_values}")
            
            c.execute(update_query, update_values)
            
            # Check if update was successful
            rows_affected = c.rowcount
            print(f"Rows affected by update: {rows_affected}")
            
            if rows_affected > 0:
                conn.commit()
                print("Database commit successful")
                
                # Verify the update
                c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
                updated_data = c.fetchone()
                print(f"Data after update: {updated_data}")
                
                flash('Profile updated successfully!', 'success')
                print(f"Profile updated for user {user_id}: {region}, {budget}, {gender}, {age}, {height}, {weight}, {activity_level}, {fitness_goal}")
            else:
                print("No rows were affected by the update")
                flash('No changes were made to your profile. Please check your input.', 'info')
            
            conn.close()
            
            # Check if user wants to go to AI sections after profile update
            redirect_to = request.form.get('redirect_to', 'dashboard')
            print(f"Redirect target: {redirect_to}")
            
            if redirect_to in ['ai_coaching', 'ai_recipes', 'ai_workout_plan', 'ai_progress_analysis']:
                print(f"Redirecting to AI section: {redirect_to}")
                flash('Profile updated successfully! Now generating personalized AI recommendations...', 'success')
                return redirect(url_for(redirect_to, updated='true'))
            else:
                print(f"Redirecting to dashboard")
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('dashboard'))
            
        except Exception as e:
            print(f"Profile update error: {e}")
            import traceback
            traceback.print_exc()
            flash(f'Error updating profile: {str(e)}', 'danger')
            return redirect(url_for('profile'))
    
    # GET request - display current profile
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
        user = c.fetchone()
        conn.close()
        
        print(f"GET request - Current user data: {user}")
        
        if user is None:
            flash('User profile not found.', 'danger')
            return redirect(url_for('dashboard'))
        
        return render_template('profile.html', user=user)
        
    except Exception as e:
        print(f"Profile retrieval error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading profile: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/recommendations')
def recommendations():
    if 'user_id' not in session:
        flash('Please log in to see recommendations.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
    user = c.fetchone()
    conn.close()
    
    if not user or not all(user):
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('profile'))
    
    region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal = user
    
    # Calculate BMI
    bmi = None
    try:
        bmi = round(float(weight) / ((float(height)/100) ** 2), 1)
    except Exception:
        bmi = None
    
    # Use ML recommendations if available
    if ML_AVAILABLE:
        try:
            # Prepare user data for ML engine
            user_data = {
                'age': age,
                'gender': gender,
                'height': height,
                'weight': weight,
                'activity_level': activity_level,
                'fitness_goal': fitness_goal,
                'region': region,
                'budget': budget,
                'allergies': allergies
            }
            
            # Generate ML-based recommendations
            workout_recommendations = recommendation_engine.generate_workout_plan(user_data)
            diet_recommendations = recommendation_engine.generate_diet_plan(user_data)
            
            return render_template('ml_recommendations.html', 
                                 bmi=bmi,
                                 workout_recommendations=workout_recommendations,
                                 diet_recommendations=diet_recommendations,
                                 user={'region': region, 'budget': budget, 'allergies': allergies, 'gender': gender, 'height': height, 'weight': weight, 'age': age, 'activity_level': activity_level, 'fitness_goal': fitness_goal},
                                 ml_available=True)
        except Exception as e:
            print(f"ML recommendation error: {e}")
            # Fall back to basic recommendations
    
    # Basic recommendations (fallback)
    workout_plan = []
    diet_plan = []
    
    # BMI-based recommendations
    if bmi and bmi < 18.5:
        workout_plan.append('Focus on strength training 3-4 times per week')
        workout_plan.append('Include compound exercises like squats, deadlifts, and bench press')
        diet_plan.append('High-calorie, protein-rich foods (lean meats, eggs, dairy)')
        diet_plan.append('Healthy fats from nuts, avocados, and olive oil')
    elif bmi and bmi < 25:
        workout_plan.append('Mix of cardio and strength training 4-5 times per week')
        workout_plan.append('Include HIIT workouts for maximum efficiency')
        diet_plan.append('Balanced diet with lean protein, vegetables, and whole grains')
        diet_plan.append('Moderate portion sizes with regular meal timing')
    else:
        workout_plan.append('Cardio 3-4 times per week (30-45 minutes)')
        workout_plan.append('Strength training 2-3 times per week')
        diet_plan.append('Calorie deficit with high-fiber, low-calorie foods')
        diet_plan.append('Focus on vegetables, lean proteins, and complex carbs')
    
    # Gender-specific recommendations
    if gender == 'female':
        workout_plan.append('Include flexibility and core exercises')
        workout_plan.append('Consider yoga or pilates for overall fitness')
    elif gender == 'male':
        workout_plan.append('Focus on progressive overload in strength training')
        workout_plan.append('Include compound movements for muscle building')
    
    # Activity level recommendations
    if activity_level == 'sedentary':
        workout_plan.append('Start with 10-15 minute walks daily')
        workout_plan.append('Gradually increase intensity and duration')
    elif activity_level == 'moderate':
        workout_plan.append('Maintain current activity level')
        workout_plan.append('Add 1-2 high-intensity sessions per week')
    elif activity_level == 'active':
        workout_plan.append('Focus on recovery and preventing overtraining')
        workout_plan.append('Consider cross-training to prevent plateaus')
    
    # Fitness goal specific recommendations
    if fitness_goal == 'weight_loss':
        workout_plan.append('Prioritize cardio and full-body workouts')
        diet_plan.append('Create a 300-500 calorie daily deficit')
    elif fitness_goal == 'muscle_gain':
        workout_plan.append('Focus on progressive overload and compound movements')
        diet_plan.append('Increase protein intake to 1.6-2.2g per kg body weight')
    elif fitness_goal == 'endurance':
        workout_plan.append('Include long-distance cardio and interval training')
        diet_plan.append('Focus on complex carbohydrates for sustained energy')
    
    # Allergy considerations
    if allergies:
        allergy_list = allergies.lower().split(',')
        if 'nuts' in allergy_list:
            diet_plan.append('Avoid nuts and nut-based products')
        if 'dairy' in allergy_list:
            diet_plan.append('Use plant-based milk alternatives')
        if 'gluten' in allergy_list:
            diet_plan.append('Choose gluten-free grains like quinoa and rice')
    
    # Regional considerations
    if region and region.lower() == 'asia':
        diet_plan.append('Incorporate local grains like rice, millet, and quinoa')
        diet_plan.append('Include fermented foods for gut health')
    elif region and region.lower() == 'mediterranean':
        diet_plan.append('Embrace Mediterranean diet principles')
        diet_plan.append('Use olive oil and include fish regularly')
    
    # Budget considerations
    if budget and budget.lower() == 'low':
        diet_plan.append('Choose affordable protein sources like lentils, eggs, and beans')
        diet_plan.append('Buy seasonal vegetables and fruits')
        workout_plan.append('Use bodyweight exercises and minimal equipment')
    
    return render_template('recommendations.html', 
                         bmi=bmi, 
                         workout_plan=workout_plan, 
                         diet_plan=diet_plan, 
                         user={'region': region, 'budget': budget, 'allergies': allergies, 'gender': gender, 'height': height, 'weight': weight, 'age': age, 'activity_level': activity_level, 'fitness_goal': fitness_goal},
                         ml_available=False)

@app.route('/ai_coaching')
def ai_coaching():
    """AI-powered fitness coaching"""
    if 'user_id' not in session:
        flash('Please log in to access AI coaching.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    try:
        # Get user data with debugging
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
        user = c.fetchone()
        
        print(f"AI Coaching - User data for user {user_id}: {user}")
        
        if not user:
            flash('User profile not found. Please complete your profile first.', 'warning')
            conn.close()
            return redirect(url_for('profile'))
        
        # Check if all required fields are filled with better validation
        required_fields = ['region', 'budget', 'gender', 'height', 'weight', 'age', 'activity_level', 'fitness_goal']
        missing_fields = []
        
        print(f"AI Coaching - Validating user data: {user}")
        
        for i, field in enumerate(required_fields):
            value = user[i]
            print(f"Field {field}: value = {value}, type = {type(value)}")
            
            # More lenient validation - only check if field is completely empty
            if value is None or value == '' or (isinstance(value, str) and value.strip() == ''):
                missing_fields.append(field)
                print(f"Missing field: {field} (value: {value})")
        
        print(f"Missing fields: {missing_fields}")
        
        if missing_fields:
            flash(f'Please complete your profile first. Missing: {", ".join(missing_fields)}', 'warning')
            conn.close()
            return redirect(url_for('profile'))
        
        region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal = user
        
        # Get recent workouts and meals
        c.execute('''SELECT date, workout_type, duration, calories_burned 
                     FROM workouts WHERE user_id = ? ORDER BY date DESC LIMIT 5''', (user_id,))
        recent_workouts = c.fetchall()
        
        c.execute('''SELECT date, meal_type, food_name, calories 
                     FROM meals WHERE user_id = ? ORDER BY date DESC LIMIT 5''', (user_id,))
        recent_meals = c.fetchall()
        
        conn.close()
        
        user_data = {
            'age': age,
            'gender': gender,
            'height': height,
            'weight': weight,
            'activity_level': activity_level,
            'fitness_goal': fitness_goal,
            'region': region,
            'budget': budget,
            'allergies': allergies
        }
        
        print(f"AI Coaching - Processed user data: {user_data}")
        
        # Generate AI coaching if available
        ai_coaching_data = None
        if AI_AVAILABLE:
            try:
                ai_coaching_data = ai_enhancements.generate_fitness_coaching(
                    user_data, 
                    recent_workouts, 
                    recent_meals
                )
                print(f"AI Coaching - Generated data: {ai_coaching_data}")
            except Exception as e:
                print(f"AI coaching error: {e}")
        
        return render_template('ai_coaching.html', 
                             user_data=user_data,
                             ai_coaching=ai_coaching_data,
                             recent_workouts=recent_workouts,
                             recent_meals=recent_meals,
                             ai_available=AI_AVAILABLE)
                             
    except Exception as e:
        print(f"AI coaching route error: {e}")
        flash(f'Error loading AI coaching: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/ai_recipes')
def ai_recipes():
    """AI-powered recipe suggestions"""
    if 'user_id' not in session:
        flash('Please log in to access AI recipes.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    try:
        # Get user data with debugging
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
        user = c.fetchone()
        conn.close()
        
        print(f"AI Recipes - User data for user {user_id}: {user}")
        
        if not user:
            flash('User profile not found. Please complete your profile first.', 'warning')
            return redirect(url_for('profile'))
        
        # Check if all required fields are filled with better validation
        required_fields = ['region', 'budget', 'gender', 'height', 'weight', 'age', 'activity_level', 'fitness_goal']
        missing_fields = []
        
        print(f"AI Recipes - Validating user data: {user}")
        
        for i, field in enumerate(required_fields):
            value = user[i]
            print(f"Field {field}: value = {value}, type = {type(value)}")
            
            # More lenient validation - only check if field is completely empty
            if value is None or value == '' or (isinstance(value, str) and value.strip() == ''):
                missing_fields.append(field)
                print(f"Missing field: {field} (value: {value})")
        
        print(f"Missing fields: {missing_fields}")
        
        if missing_fields:
            flash(f'Please complete your profile first. Missing: {", ".join(missing_fields)}', 'warning')
            return redirect(url_for('profile'))
        
        region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal = user
        
        user_data = {
            'age': age,
            'gender': gender,
            'height': height,
            'weight': weight,
            'activity_level': activity_level,
            'fitness_goal': fitness_goal,
            'region': region,
            'budget': budget,
            'allergies': allergies
        }
        
        print(f"AI Recipes - Processed user data: {user_data}")
        
        # Generate AI recipes if available
        ai_recipes_data = None
        if AI_AVAILABLE:
            try:
                ai_recipes_data = ai_enhancements.generate_recipe_suggestions(user_data)
                print(f"AI Recipes - Generated data: {ai_recipes_data}")
                
                # Check allergy safety for each recipe
                if ai_recipes_data and 'recipes' in ai_recipes_data:
                    for recipe in ai_recipes_data['recipes']:
                        if 'ingredients' in recipe:
                            allergy_check = check_recipe_allergy_safety(recipe['ingredients'], allergies)
                            recipe['allergy_safety'] = allergy_check
                            recipe['is_safe'] = allergy_check['safe']
                            recipe['allergy_warnings'] = allergy_check['warnings']
                
            except Exception as e:
                print(f"AI recipes error: {e}")
        
        return render_template('ai_recipes.html', 
                             user_data=user_data,
                             ai_recipes=ai_recipes_data,
                             ai_available=AI_AVAILABLE,
                             user_allergies=allergies)
                             
    except Exception as e:
        print(f"AI recipes route error: {e}")
        flash(f'Error loading AI recipes: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/ai_workout_plan')
def ai_workout_plan():
    """AI-powered workout plan"""
    if 'user_id' not in session:
        flash('Please log in to access AI workout plans.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    try:
        # Get user data with debugging
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
        user = c.fetchone()
        conn.close()
        
        print(f"AI Workout Plan - User data for user {user_id}: {user}")
        
        if not user:
            flash('User profile not found. Please complete your profile first.', 'warning')
            return redirect(url_for('profile'))
        
        # Check if all required fields are filled with better validation
        required_fields = ['region', 'budget', 'gender', 'height', 'weight', 'age', 'activity_level', 'fitness_goal']
        missing_fields = []
        
        print(f"AI Workout Plan - Validating user data: {user}")
        
        for i, field in enumerate(required_fields):
            value = user[i]
            print(f"Field {field}: value = {value}, type = {type(value)}")
            
            # More lenient validation - only check if field is completely empty
            if value is None or value == '' or (isinstance(value, str) and value.strip() == ''):
                missing_fields.append(field)
                print(f"Missing field: {field} (value: {value})")
        
        print(f"Missing fields: {missing_fields}")
        
        if missing_fields:
            flash(f'Please complete your profile first. Missing: {", ".join(missing_fields)}', 'warning')
            return redirect(url_for('profile'))
        
        region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal = user
        
        user_data = {
            'age': age,
            'gender': gender,
            'height': height,
            'weight': weight,
            'activity_level': activity_level,
            'fitness_goal': fitness_goal,
            'region': region,
            'budget': budget,
            'allergies': allergies
        }
        
        print(f"AI Workout Plan - Processed user data: {user_data}")
        
        # Generate AI workout plan if available
        ai_workout_data = None
        if AI_AVAILABLE:
            try:
                ai_workout_data = ai_enhancements.generate_workout_plan_ai(user_data)
                print(f"AI Workout Plan - Generated data: {ai_workout_data}")
            except Exception as e:
                print(f"AI workout plan error: {e}")
        
        return render_template('ai_workout_plan.html', 
                             user_data=user_data,
                             ai_workout=ai_workout_data,
                             ai_available=AI_AVAILABLE)
                             
    except Exception as e:
        print(f"AI workout plan route error: {e}")
        flash(f'Error loading AI workout plan: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/ai_progress_analysis')
def ai_progress_analysis():
    """AI-powered progress analysis"""
    if 'user_id' not in session:
        flash('Please log in to access AI progress analysis.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    try:
        # Get user data and progress with debugging
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
        user = c.fetchone()
        
        print(f"AI Progress Analysis - User data for user {user_id}: {user}")
        
        if not user:
            flash('User profile not found. Please complete your profile first.', 'warning')
            conn.close()
            return redirect(url_for('profile'))
        
        # Check if all required fields are filled with better validation
        required_fields = ['region', 'budget', 'gender', 'height', 'weight', 'age', 'activity_level', 'fitness_goal']
        missing_fields = []
        
        print(f"AI Progress Analysis - Validating user data: {user}")
        
        for i, field in enumerate(required_fields):
            value = user[i]
            print(f"Field {field}: value = {value}, type = {type(value)}")
            
            # More lenient validation - only check if field is completely empty
            if value is None or value == '' or (isinstance(value, str) and value.strip() == ''):
                missing_fields.append(field)
                print(f"Missing field: {field} (value: {value})")
        
        print(f"Missing fields: {missing_fields}")
        
        if missing_fields:
            flash(f'Please complete your profile first. Missing: {", ".join(missing_fields)}', 'warning')
            conn.close()
            return redirect(url_for('profile'))
        
        # Get progress data
        c.execute('SELECT COUNT(*) FROM workouts WHERE user_id = ?', (user_id,))
        total_workouts = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM meals WHERE user_id = ?', (user_id,))
        total_meals = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM goals WHERE user_id = ? AND status = "completed"', (user_id,))
        completed_goals = c.fetchone()[0]
        
        c.execute('SELECT weight FROM weight_log WHERE user_id = ? ORDER BY date DESC LIMIT 2', (user_id,))
        weight_data = c.fetchall()
        
        conn.close()
        
        region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal = user
        
        user_data = {
            'age': age,
            'gender': gender,
            'height': height,
            'weight': weight,
            'activity_level': activity_level,
            'fitness_goal': fitness_goal,
            'region': region,
            'budget': budget,
            'allergies': allergies
        }
        
        progress_data = {
            'total_workouts': total_workouts,
            'total_meals': total_meals,
            'completed_goals': completed_goals,
            'weight_data': weight_data,
            'current_weight': weight
        }
        
        print(f"AI Progress Analysis - Processed user data: {user_data}")
        print(f"AI Progress Analysis - Progress data: {progress_data}")
        
        # Generate AI progress analysis if available
        ai_analysis_data = None
        if AI_AVAILABLE:
            try:
                ai_analysis_data = ai_enhancements.analyze_progress(user_data, progress_data)
                print(f"AI Progress Analysis - Generated data: {ai_analysis_data}")
            except Exception as e:
                print(f"AI progress analysis error: {e}")
        
        return render_template('ai_progress_analysis.html', 
                             user_data=user_data,
                             progress_data=progress_data,
                             ai_analysis=ai_analysis_data,
                             ai_available=AI_AVAILABLE)
                             
    except Exception as e:
        print(f"AI progress analysis route error: {e}")
        flash(f'Error loading AI progress analysis: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/test_profile_update')
def test_profile_update():
    """Test route to check profile update functionality"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'})
    
    user_id = session['user_id']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Get current profile data
        c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
        user_data = c.fetchone()
        
        # Check if profile is complete
        required_fields = ['region', 'budget', 'gender', 'height', 'weight', 'age', 'activity_level', 'fitness_goal']
        missing_fields = []
        
        for i, field in enumerate(required_fields):
            value = user_data[i] if user_data else None
            if value is None or value == '' or (isinstance(value, str) and value.strip() == ''):
                missing_fields.append(field)
        
        return jsonify({
            'user_id': user_id,
            'profile_data': user_data,
            'missing_fields': missing_fields,
            'is_complete': len(missing_fields) == 0,
            'field_names': required_fields
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        conn.close()

@app.route('/force_update_profile', methods=['POST'])
def force_update_profile():
    """Force update profile with test data"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'})
    
    user_id = session['user_id']
    
    try:
        # Test data
        test_data = {
            'region': 'asia',
            'budget': 'medium',
            'allergies': 'none',
            'gender': 'male',
            'height': 175.0,
            'weight': 70.0,
            'age': 25,
            'activity_level': 'moderately_active',
            'fitness_goal': 'weight_loss'
        }
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Update the user profile
        update_query = '''UPDATE users SET 
                         region=?, budget=?, allergies=?, gender=?, height=?, weight=?, age=?, activity_level=?, fitness_goal=? 
                         WHERE id=?'''
        update_values = (
            test_data['region'], test_data['budget'], test_data['allergies'], 
            test_data['gender'], test_data['height'], test_data['weight'], 
            test_data['age'], test_data['activity_level'], test_data['fitness_goal'], 
            user_id
        )
        
        c.execute(update_query, update_values)
        conn.commit()
        
        # Verify the update
        c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
        updated_data = c.fetchone()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Profile force updated with test data',
            'updated_data': updated_data,
            'test_data': test_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/test_ai_coaching')
def test_ai_coaching():
    """Test route to bypass profile validation for AI coaching"""
    if 'user_id' not in session:
        flash('Please log in to access AI coaching.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    try:
        # Get user data
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
        user = c.fetchone()
        
        if not user:
            flash('User profile not found.', 'warning')
            conn.close()
            return redirect(url_for('profile'))
        
        region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal = user
        
        # Use default values if fields are empty
        user_data = {
            'age': age if age and age > 0 else 25,
            'gender': gender if gender else 'not specified',
            'height': height if height and height > 0 else 170,
            'weight': weight if weight and weight > 0 else 70,
            'activity_level': activity_level if activity_level else 'moderate',
            'fitness_goal': fitness_goal if fitness_goal else 'general fitness',
            'region': region if region else 'global',
            'budget': budget if budget else 'moderate',
            'allergies': allergies if allergies else 'none'
        }
        
        # Get recent workouts and meals
        c.execute('''SELECT date, workout_type, duration, calories_burned 
                     FROM workouts WHERE user_id = ? ORDER BY date DESC LIMIT 5''', (user_id,))
        recent_workouts = c.fetchall()
        
        c.execute('''SELECT date, meal_type, food_name, calories 
                     FROM meals WHERE user_id = ? ORDER BY date DESC LIMIT 5''', (user_id,))
        recent_meals = c.fetchall()
        
        conn.close()
        
        # Generate AI coaching if available
        ai_coaching_data = None
        if AI_AVAILABLE:
            try:
                ai_coaching_data = ai_enhancements.generate_fitness_coaching(
                    user_data, 
                    recent_workouts, 
                    recent_meals
                )
            except Exception as e:
                print(f"AI coaching error: {e}")
        
        return render_template('ai_coaching.html', 
                             user_data=user_data,
                             ai_coaching=ai_coaching_data,
                             recent_workouts=recent_workouts,
                             recent_meals=recent_meals,
                             ai_available=AI_AVAILABLE)
                             
    except Exception as e:
        print(f"Test AI coaching route error: {e}")
        flash(f'Error loading AI coaching: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from data_science import ds_engine
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json

# Import ML recommendation engine
try:
    from ml_recommendations import recommendation_engine
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("ML recommendations not available. Install scikit-learn for advanced features.")

# Import AI enhancements
try:
    from ai_enhancements import ai_enhancements
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("AI enhancements not available. Install requests for advanced AI features.")

def check_recipe_allergy_safety(recipe_ingredients, user_allergies):
    """Check if a recipe is safe for user's allergies and return safety status"""
    if not user_allergies or user_allergies.lower() in ['none', 'no', 'n/a', '']:
        return {'safe': True, 'warnings': [], 'allergens_found': []}
    
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
    
    user_allergies_lower = user_allergies.lower()
    allergens_found = []
    warnings = []
    
    for ingredient in recipe_ingredients:
        ingredient_lower = ingredient.lower()
        
        # Check direct match
        if user_allergies_lower in ingredient_lower:
            allergens_found.append(ingredient)
            warnings.append(f"Contains {ingredient} (allergen: {user_allergies_lower})")
        
        # Check allergen mapping
        for allergen_type, allergen_list in allergen_mapping.items():
            if any(allergen in user_allergies_lower for allergen in allergen_list):
                if any(allergen in ingredient_lower for allergen in allergen_list):
                    allergens_found.append(ingredient)
                    warnings.append(f"Contains {ingredient} (allergen: {allergen_type})")
    
    return {
        'safe': len(allergens_found) == 0,
        'warnings': warnings,
        'allergens_found': allergens_found
    }

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure random value
DB_NAME = 'fitness_diet.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Enhanced users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT,
        region TEXT,
        budget TEXT,
        allergies TEXT,
        gender TEXT,
        height REAL,
        weight REAL,
        age INTEGER,
        activity_level TEXT,
        fitness_goal TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Enhanced workouts table
    c.execute('''CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        workout_type TEXT,
        duration INTEGER,
        calories_burned INTEGER,
        exercises TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # Enhanced meals table
    c.execute('''CREATE TABLE IF NOT EXISTS meals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        meal_type TEXT,
        food_name TEXT,
        calories INTEGER,
        protein REAL,
        carbs REAL,
        fat REAL,
        fiber REAL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # New goals table
    c.execute('''CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        goal_type TEXT,
        target_value REAL,
        current_value REAL,
        target_date TEXT,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # New achievements table
    c.execute('''CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        achievement_type TEXT,
        title TEXT,
        description TEXT,
        earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # New weight tracking table
    c.execute('''CREATE TABLE IF NOT EXISTS weight_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        weight REAL,
        date TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    conn.commit()
    conn.close()

def ensure_db_compatibility():
    """Ensure database is compatible with current schema"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Check if users table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not c.fetchone():
            # Table doesn't exist, create it
            init_db()
        else:
            # Check if all required columns exist
            c.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in c.fetchall()]
            required_columns = ['id', 'username', 'password', 'email', 'region', 'budget', 'allergies', 'gender', 'height', 'weight', 'age', 'activity_level', 'fitness_goal', 'created_at']
            
            for column in required_columns:
                if column not in columns:
                    if column == 'email':
                        c.execute('ALTER TABLE users ADD COLUMN email TEXT')
                    elif column == 'age':
                        c.execute('ALTER TABLE users ADD COLUMN age INTEGER')
                    elif column == 'activity_level':
                        c.execute('ALTER TABLE users ADD COLUMN activity_level TEXT')
                    elif column == 'fitness_goal':
                        c.execute('ALTER TABLE users ADD COLUMN fitness_goal TEXT')
                    elif column == 'created_at':
                        c.execute('ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
                    conn.commit()
    except Exception as e:
        print(f"Database compatibility error: {e}")
        # If there's an error, recreate the database
        c.execute("DROP TABLE IF EXISTS users")
        c.execute("DROP TABLE IF EXISTS workouts")
        c.execute("DROP TABLE IF EXISTS meals")
        c.execute("DROP TABLE IF EXISTS goals")
        c.execute("DROP TABLE IF EXISTS achievements")
        c.execute("DROP TABLE IF EXISTS weight_log")
        conn.commit()
        init_db()
    finally:
        conn.close()

def check_and_fix_database_schema():
    """Check and fix database schema to ensure all required columns exist"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Check if users table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not c.fetchone():
            print("Users table doesn't exist, creating it...")
            init_db()
            return
        
        # Get current columns
        c.execute("PRAGMA table_info(users)")
        current_columns = [column[1] for column in c.fetchall()]
        print(f"Current columns in users table: {current_columns}")
        
        # Required columns
        required_columns = {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'username': 'TEXT UNIQUE NOT NULL',
            'password': 'TEXT NOT NULL',
            'email': 'TEXT',
            'region': 'TEXT',
            'budget': 'TEXT',
            'allergies': 'TEXT',
            'gender': 'TEXT',
            'height': 'REAL',
            'weight': 'REAL',
            'age': 'INTEGER',
            'activity_level': 'TEXT',
            'fitness_goal': 'TEXT',
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        }
        
        # Check for missing columns and add them
        for column_name, column_type in required_columns.items():
            if column_name not in current_columns:
                print(f"Adding missing column: {column_name}")
                try:
                    c.execute(f'ALTER TABLE users ADD COLUMN {column_name} {column_type}')
                    conn.commit()
                    print(f"Successfully added column: {column_name}")
                except Exception as e:
                    print(f"Error adding column {column_name}: {e}")
        
        # Verify final schema
        c.execute("PRAGMA table_info(users)")
        final_columns = [column[1] for column in c.fetchall()]
        print(f"Final columns in users table: {final_columns}")
        
    except Exception as e:
        print(f"Database schema check error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

# Call this function after init_db
init_db()
ensure_db_compatibility()
check_and_fix_database_schema()

@app.route('/debug_user_data')
def debug_user_data():
    """Debug route to check current user data"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'})
    
    user_id = session['user_id']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Get all user data
        c.execute('SELECT * FROM users WHERE id=?', (user_id,))
        user_data = c.fetchone()
        
        # Get column names
        c.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in c.fetchall()]
        
        # Create a dictionary with column names and values
        user_dict = {}
        if user_data:
            for i, column in enumerate(columns):
                user_dict[column] = user_data[i]
        
        # Also get the specific fields used in AI validation
        c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
        ai_fields = c.fetchone()
        
        return jsonify({
            'user_id': user_id,
            'columns': columns,
            'user_data': user_dict,
            'ai_fields': ai_fields,
            'ai_field_names': ['region', 'budget', 'allergies', 'gender', 'height', 'weight', 'age', 'activity_level', 'fitness_goal']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access your dashboard.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Get user stats
    c.execute('SELECT height, weight, gender, age FROM users WHERE id = ?', (user_id,))
    user_data = c.fetchone()
    
    # Get recent workouts
    c.execute('''SELECT date, workout_type, duration, calories_burned 
                 FROM workouts WHERE user_id = ? ORDER BY date DESC LIMIT 5''', (user_id,))
    recent_workouts = c.fetchall()
    
    # Get recent meals
    c.execute('''SELECT date, meal_type, food_name, calories 
                 FROM meals WHERE user_id = ? ORDER BY date DESC LIMIT 5''', (user_id,))
    recent_meals = c.fetchall()
    
    # Get weight progress (last 7 entries)
    c.execute('''SELECT date, weight FROM weight_log 
                 WHERE user_id = ? ORDER BY date DESC LIMIT 7''', (user_id,))
    weight_data = c.fetchall()
    
    # Calculate stats
    total_workouts = c.execute('SELECT COUNT(*) FROM workouts WHERE user_id = ?', (user_id,)).fetchone()[0]
    total_calories_burned = c.execute('SELECT SUM(calories_burned) FROM workouts WHERE user_id = ?', (user_id,)).fetchone()[0] or 0
    total_meals = c.execute('SELECT COUNT(*) FROM meals WHERE user_id = ?', (user_id,)).fetchone()[0]
    total_calories_consumed = c.execute('SELECT SUM(calories) FROM meals WHERE user_id = ?', (user_id,)).fetchone()[0] or 0
    
    # Get active goals
    c.execute('''SELECT goal_type, target_value, current_value, target_date 
                 FROM goals WHERE user_id = ? AND status = 'active' ''', (user_id,))
    active_goals = c.fetchall()
    
    conn.close()
    
    # Calculate BMI
    bmi = None
    if user_data and user_data[0] and user_data[1]:
        try:
            bmi = round(float(user_data[1]) / ((float(user_data[0])/100) ** 2), 1)
        except:
            bmi = None
    
    return render_template('dashboard.html', 
                         user_data=user_data, 
                         recent_workouts=recent_workouts,
                         recent_meals=recent_meals,
                         weight_data=weight_data,
                         total_workouts=total_workouts,
                         total_calories_burned=total_calories_burned,
                         total_meals=total_meals,
                         total_calories_consumed=total_calories_consumed,
                         active_goals=active_goals,
                         bmi=bmi)

@app.route('/fitness', methods=['GET', 'POST'])
def fitness():
    if 'user_id' not in session:
        flash('Please log in to access fitness tracking.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        workout_type = request.form['workout_type']
        duration = int(request.form['duration'])
        calories_burned = int(request.form['calories_burned'])
        exercises = request.form.get('exercises', '')
        notes = request.form.get('notes', '')
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''INSERT INTO workouts (user_id, date, workout_type, duration, calories_burned, exercises, notes)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                  (user_id, date, workout_type, duration, calories_burned, exercises, notes))
        conn.commit()
        conn.close()
        
        flash('Workout logged successfully!', 'success')
        return redirect(url_for('fitness'))
    
    # Get workout history
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT date, workout_type, duration, calories_burned, exercises, notes 
                 FROM workouts WHERE user_id = ? ORDER BY date DESC''', (user_id,))
    workouts = c.fetchall()
    conn.close()
    
    return render_template('fitness.html', workouts=workouts, today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/diet', methods=['GET', 'POST'])
def diet():
    if 'user_id' not in session:
        flash('Please log in to access diet tracking.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        meal_type = request.form['meal_type']
        food_name = request.form['food_name']
        calories = int(request.form['calories'])
        protein = float(request.form.get('protein', 0))
        carbs = float(request.form.get('carbs', 0))
        fat = float(request.form.get('fat', 0))
        fiber = float(request.form.get('fiber', 0))
        notes = request.form.get('notes', '')
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''INSERT INTO meals (user_id, date, meal_type, food_name, calories, protein, carbs, fat, fiber, notes)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                  (user_id, date, meal_type, food_name, calories, protein, carbs, fat, fiber, notes))
        conn.commit()
        conn.close()
        
        flash('Meal logged successfully!', 'success')
        return redirect(url_for('diet'))
    
    # Get meal history
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT date, meal_type, food_name, calories, protein, carbs, fat, fiber, notes 
                 FROM meals WHERE user_id = ? ORDER BY date DESC''', (user_id,))
    meals = c.fetchall()
    conn.close()
    
    return render_template('diet.html', meals=meals, today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/goals', methods=['GET', 'POST'])
def goals():
    if 'user_id' not in session:
        flash('Please log in to access goals.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        try:
            goal_type = request.form['goal_type']
            target_value = float(request.form['target_value'])
            current_value = float(request.form.get('current_value', 0))
            target_date = request.form['target_date']
            
            # Validate inputs
            if target_value <= 0:
                flash('Target value must be greater than 0.', 'danger')
                return redirect(url_for('goals'))
            
            if current_value < 0:
                flash('Current value cannot be negative.', 'danger')
                return redirect(url_for('goals'))
            
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute('''INSERT INTO goals (user_id, goal_type, target_value, current_value, target_date)
                         VALUES (?, ?, ?, ?, ?)''', 
                      (user_id, goal_type, target_value, current_value, target_date))
            conn.commit()
            conn.close()
            
            flash('Goal set successfully!', 'success')
            return redirect(url_for('goals'))
        except ValueError:
            flash('Please enter valid numbers for target and current values.', 'danger')
            return redirect(url_for('goals'))
        except Exception as e:
            flash(f'Error setting goal: {str(e)}', 'danger')
            return redirect(url_for('goals'))
    
    # Get goals
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''SELECT id, goal_type, target_value, current_value, target_date, status 
                     FROM goals WHERE user_id = ? ORDER BY created_at DESC''', (user_id,))
        goals = c.fetchall()
        conn.close()
    except Exception as e:
        flash(f'Error loading goals: {str(e)}', 'danger')
        goals = []
    
    return render_template('goals.html', goals=goals)

@app.route('/update_goal/<int:goal_id>', methods=['POST'])
def update_goal(goal_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        user_id = session['user_id']
        current_value = float(request.form['current_value'])
        
        # Validate input
        if current_value < 0:
            return jsonify({'error': 'Current value cannot be negative'}), 400
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Check if goal exists and belongs to user
        c.execute('SELECT id FROM goals WHERE id = ? AND user_id = ?', (goal_id, user_id))
        if not c.fetchone():
            conn.close()
            return jsonify({'error': 'Goal not found'}), 404
        
        # Update the goal
        c.execute('UPDATE goals SET current_value = ? WHERE id = ? AND user_id = ?', 
                  (current_value, goal_id, user_id))
        
        # Check if goal is completed
        c.execute('SELECT target_value FROM goals WHERE id = ? AND user_id = ?', (goal_id, user_id))
        target_value = c.fetchone()[0]
        
        if current_value >= target_value:
            c.execute('UPDATE goals SET status = ? WHERE id = ? AND user_id = ?', 
                      ('completed', goal_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except ValueError:
        return jsonify({'error': 'Invalid current value'}), 400
    except Exception as e:
        return jsonify({'error': f'Update failed: {str(e)}'}), 500

@app.route('/weight_log', methods=['GET', 'POST'])
def weight_log():
    if 'user_id' not in session:
        flash('Please log in to access weight tracking.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        weight = float(request.form['weight'])
        notes = request.form.get('notes', '')
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('INSERT INTO weight_log (user_id, weight, date, notes) VALUES (?, ?, ?, ?)', 
                  (user_id, weight, date, notes))
        conn.commit()
        conn.close()
        
        flash('Weight logged successfully!', 'success')
        return redirect(url_for('weight_log'))
    
    # Get weight history
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT date, weight, notes FROM weight_log WHERE user_id = ? ORDER BY date DESC', (user_id,))
    weight_logs = c.fetchall()
    conn.close()
    
    return render_template('weight_log.html', weight_logs=weight_logs, today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email', '')
        hashed_pw = generate_password_hash(password)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', (username, hashed_pw, email))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'danger')
        except Exception as e:
            flash(f'Registration error: {str(e)}', 'danger')
            print(f"Registration error: {e}")
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT id, password FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Please log in to access your profile.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    print(f"Profile route accessed for user {user_id}")
    
    if request.method == 'POST':
        print("Profile POST request received")
        print(f"Form data: {request.form}")
        
        try:
            # Get form data with proper validation
            region = request.form.get('region', '').strip()
            budget = request.form.get('budget', '').strip()
            allergies = request.form.get('allergies', '').strip()
            gender = request.form.get('gender', '').strip()
            
            # Validate numeric inputs
            try:
                height = float(request.form.get('height', 0)) if request.form.get('height') else 0
                weight = float(request.form.get('weight', 0)) if request.form.get('weight') else 0
                age = int(request.form.get('age', 0)) if request.form.get('age') else 0
            except (ValueError, TypeError) as e:
                print(f"Validation error: {e}")
                flash('Please enter valid numbers for height, weight, and age.', 'danger')
                return redirect(url_for('profile'))
            
            activity_level = request.form.get('activity_level', '').strip()
            fitness_goal = request.form.get('fitness_goal', '').strip()
            
            print(f"Processed form data:")
            print(f"  Region: {region}")
            print(f"  Budget: {budget}")
            print(f"  Allergies: {allergies}")
            print(f"  Gender: {gender}")
            print(f"  Height: {height}")
            print(f"  Weight: {weight}")
            print(f"  Age: {age}")
            print(f"  Activity Level: {activity_level}")
            print(f"  Fitness Goal: {fitness_goal}")
            
            # Validate required fields
            required_fields = {
                'gender': gender,
                'age': age,
                'height': height,
                'weight': weight,
                'activity_level': activity_level,
                'fitness_goal': fitness_goal,
                'region': region,
                'budget': budget
            }
            
            missing_fields = [field for field, value in required_fields.items() if not value]
            if missing_fields:
                print(f"Missing fields: {missing_fields}")
                flash(f'Please fill in all required fields: {", ".join(missing_fields)}', 'danger')
                return redirect(url_for('profile'))
            
            # Validate ranges
            if age < 13 or age > 120:
                flash('Age must be between 13 and 120.', 'danger')
                return redirect(url_for('profile'))
            
            if height < 100 or height > 250:
                flash('Height must be between 100 and 250 cm.', 'danger')
                return redirect(url_for('profile'))
            
            if weight < 30 or weight > 300:
                flash('Weight must be between 30 and 300 kg.', 'danger')
                return redirect(url_for('profile'))
            
            # Connect to database and update
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            
            # First, let's check current data
            c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
            current_data = c.fetchone()
            print(f"Current data in database: {current_data}")
            
            # Update the user profile
            update_query = '''UPDATE users SET 
                             region=?, budget=?, allergies=?, gender=?, height=?, weight=?, age=?, activity_level=?, fitness_goal=? 
                             WHERE id=?'''
            update_values = (region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal, user_id)
            
            print(f"Executing update query: {update_query}")
            print(f"Update values: {update_values}")
            
            c.execute(update_query, update_values)
            
            # Check if update was successful
            rows_affected = c.rowcount
            print(f"Rows affected by update: {rows_affected}")
            
            if rows_affected > 0:
                conn.commit()
                print("Database commit successful")
                
                # Verify the update
                c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
                updated_data = c.fetchone()
                print(f"Data after update: {updated_data}")
                
                flash('Profile updated successfully!', 'success')
                print(f"Profile updated for user {user_id}: {region}, {budget}, {gender}, {age}, {height}, {weight}, {activity_level}, {fitness_goal}")
            else:
                print("No rows were affected by the update")
                flash('No changes were made to your profile. Please check your input.', 'info')
            
            conn.close()
            
            # Check if user wants to go to AI sections after profile update
            redirect_to = request.form.get('redirect_to', 'dashboard')
            print(f"Redirect target: {redirect_to}")
            
            if redirect_to in ['ai_coaching', 'ai_recipes', 'ai_workout_plan', 'ai_progress_analysis']:
                print(f"Redirecting to AI section: {redirect_to}")
                flash('Profile updated successfully! Now generating personalized AI recommendations...', 'success')
                return redirect(url_for(redirect_to, updated='true'))
            else:
                print(f"Redirecting to dashboard")
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('dashboard'))
            
        except Exception as e:
            print(f"Profile update error: {e}")
            import traceback
            traceback.print_exc()
            flash(f'Error updating profile: {str(e)}', 'danger')
            return redirect(url_for('profile'))
    
    # GET request - display current profile
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
        user = c.fetchone()
        conn.close()
        
        print(f"GET request - Current user data: {user}")
        
        if user is None:
            flash('User profile not found.', 'danger')
            return redirect(url_for('dashboard'))
        
        return render_template('profile.html', user=user)
        
    except Exception as e:
        print(f"Profile retrieval error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading profile: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/recommendations')
def recommendations():
    if 'user_id' not in session:
        flash('Please log in to see recommendations.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
    user = c.fetchone()
    conn.close()
    
    if not user or not all(user):
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('profile'))
    
    region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal = user
    
    # Calculate BMI
    bmi = None
    try:
        bmi = round(float(weight) / ((float(height)/100) ** 2), 1)
    except Exception:
        bmi = None
    
    # Use ML recommendations if available
    if ML_AVAILABLE:
        try:
            # Prepare user data for ML engine
            user_data = {
                'age': age,
                'gender': gender,
                'height': height,
                'weight': weight,
                'activity_level': activity_level,
                'fitness_goal': fitness_goal,
                'region': region,
                'budget': budget,
                'allergies': allergies
            }
            
            # Generate ML-based recommendations
            workout_recommendations = recommendation_engine.generate_workout_plan(user_data)
            diet_recommendations = recommendation_engine.generate_diet_plan(user_data)
            
            return render_template('ml_recommendations.html', 
                                 bmi=bmi,
                                 workout_recommendations=workout_recommendations,
                                 diet_recommendations=diet_recommendations,
                                 user={'region': region, 'budget': budget, 'allergies': allergies, 'gender': gender, 'height': height, 'weight': weight, 'age': age, 'activity_level': activity_level, 'fitness_goal': fitness_goal},
                                 ml_available=True)
        except Exception as e:
            print(f"ML recommendation error: {e}")
            # Fall back to basic recommendations
    
    # Basic recommendations (fallback)
    workout_plan = []
    diet_plan = []
    
    # BMI-based recommendations
    if bmi and bmi < 18.5:
        workout_plan.append('Focus on strength training 3-4 times per week')
        workout_plan.append('Include compound exercises like squats, deadlifts, and bench press')
        diet_plan.append('High-calorie, protein-rich foods (lean meats, eggs, dairy)')
        diet_plan.append('Healthy fats from nuts, avocados, and olive oil')
    elif bmi and bmi < 25:
        workout_plan.append('Mix of cardio and strength training 4-5 times per week')
        workout_plan.append('Include HIIT workouts for maximum efficiency')
        diet_plan.append('Balanced diet with lean protein, vegetables, and whole grains')
        diet_plan.append('Moderate portion sizes with regular meal timing')
    else:
        workout_plan.append('Cardio 3-4 times per week (30-45 minutes)')
        workout_plan.append('Strength training 2-3 times per week')
        diet_plan.append('Calorie deficit with high-fiber, low-calorie foods')
        diet_plan.append('Focus on vegetables, lean proteins, and complex carbs')
    
    # Gender-specific recommendations
    if gender == 'female':
        workout_plan.append('Include flexibility and core exercises')
        workout_plan.append('Consider yoga or pilates for overall fitness')
    elif gender == 'male':
        workout_plan.append('Focus on progressive overload in strength training')
        workout_plan.append('Include compound movements for muscle building')
    
    # Activity level recommendations
    if activity_level == 'sedentary':
        workout_plan.append('Start with 10-15 minute walks daily')
        workout_plan.append('Gradually increase intensity and duration')
    elif activity_level == 'moderate':
        workout_plan.append('Maintain current activity level')
        workout_plan.append('Add 1-2 high-intensity sessions per week')
    elif activity_level == 'active':
        workout_plan.append('Focus on recovery and preventing overtraining')
        workout_plan.append('Consider cross-training to prevent plateaus')
    
    # Fitness goal specific recommendations
    if fitness_goal == 'weight_loss':
        workout_plan.append('Prioritize cardio and full-body workouts')
        diet_plan.append('Create a 300-500 calorie daily deficit')
    elif fitness_goal == 'muscle_gain':
        workout_plan.append('Focus on progressive overload and compound movements')
        diet_plan.append('Increase protein intake to 1.6-2.2g per kg body weight')
    elif fitness_goal == 'endurance':
        workout_plan.append('Include long-distance cardio and interval training')
        diet_plan.append('Focus on complex carbohydrates for sustained energy')
    
    # Allergy considerations
    if allergies:
        allergy_list = allergies.lower().split(',')
        if 'nuts' in allergy_list:
            diet_plan.append('Avoid nuts and nut-based products')
        if 'dairy' in allergy_list:
            diet_plan.append('Use plant-based milk alternatives')
        if 'gluten' in allergy_list:
            diet_plan.append('Choose gluten-free grains like quinoa and rice')
    
    # Regional considerations
    if region and region.lower() == 'asia':
        diet_plan.append('Incorporate local grains like rice, millet, and quinoa')
        diet_plan.append('Include fermented foods for gut health')
    elif region and region.lower() == 'mediterranean':
        diet_plan.append('Embrace Mediterranean diet principles')
        diet_plan.append('Use olive oil and include fish regularly')
    
    # Budget considerations
    if budget and budget.lower() == 'low':
        diet_plan.append('Choose affordable protein sources like lentils, eggs, and beans')
        diet_plan.append('Buy seasonal vegetables and fruits')
        workout_plan.append('Use bodyweight exercises and minimal equipment')
    
    return render_template('recommendations.html', 
                         bmi=bmi, 
                         workout_plan=workout_plan, 
                         diet_plan=diet_plan, 
                         user={'region': region, 'budget': budget, 'allergies': allergies, 'gender': gender, 'height': height, 'weight': weight, 'age': age, 'activity_level': activity_level, 'fitness_goal': fitness_goal},
                         ml_available=False)

@app.route('/ai_coaching')
def ai_coaching():
    """AI-powered fitness coaching"""
    if 'user_id' not in session:
        flash('Please log in to access AI coaching.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    try:
        # Get user data with debugging
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
        user = c.fetchone()
        
        print(f"AI Coaching - User data for user {user_id}: {user}")
        
        if not user:
            flash('User profile not found. Please complete your profile first.', 'warning')
            conn.close()
            return redirect(url_for('profile'))
        
        # Check if all required fields are filled with better validation
        required_fields = ['region', 'budget', 'gender', 'height', 'weight', 'age', 'activity_level', 'fitness_goal']
        missing_fields = []
        
        print(f"AI Coaching - Validating user data: {user}")
        
        for i, field in enumerate(required_fields):
            value = user[i]
            print(f"Field {field}: value = {value}, type = {type(value)}")
            
            # More lenient validation - only check if field is completely empty
            if value is None or value == '' or (isinstance(value, str) and value.strip() == ''):
                missing_fields.append(field)
                print(f"Missing field: {field} (value: {value})")
        
        print(f"Missing fields: {missing_fields}")
        
        if missing_fields:
            flash(f'Please complete your profile first. Missing: {", ".join(missing_fields)}', 'warning')
            conn.close()
            return redirect(url_for('profile'))
        
        region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal = user
        
        # Get recent workouts and meals
        c.execute('''SELECT date, workout_type, duration, calories_burned 
                     FROM workouts WHERE user_id = ? ORDER BY date DESC LIMIT 5''', (user_id,))
        recent_workouts = c.fetchall()
        
        c.execute('''SELECT date, meal_type, food_name, calories 
                     FROM meals WHERE user_id = ? ORDER BY date DESC LIMIT 5''', (user_id,))
        recent_meals = c.fetchall()
        
        conn.close()
        
        user_data = {
            'age': age,
            'gender': gender,
            'height': height,
            'weight': weight,
            'activity_level': activity_level,
            'fitness_goal': fitness_goal,
            'region': region,
            'budget': budget,
            'allergies': allergies
        }
        
        print(f"AI Coaching - Processed user data: {user_data}")
        
        # Generate AI coaching if available
        ai_coaching_data = None
        if AI_AVAILABLE:
            try:
                ai_coaching_data = ai_enhancements.generate_fitness_coaching(
                    user_data, 
                    recent_workouts, 
                    recent_meals
                )
                print(f"AI Coaching - Generated data: {ai_coaching_data}")
            except Exception as e:
                print(f"AI coaching error: {e}")
        
        return render_template('ai_coaching.html', 
                             user_data=user_data,
                             ai_coaching=ai_coaching_data,
                             recent_workouts=recent_workouts,
                             recent_meals=recent_meals,
                             ai_available=AI_AVAILABLE)
                             
    except Exception as e:
        print(f"AI coaching route error: {e}")
        flash(f'Error loading AI coaching: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/ai_recipes')
def ai_recipes():
    """AI-powered recipe suggestions"""
    if 'user_id' not in session:
        flash('Please log in to access AI recipes.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    try:
        # Get user data with debugging
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
        user = c.fetchone()
        conn.close()
        
        print(f"AI Recipes - User data for user {user_id}: {user}")
        
        if not user:
            flash('User profile not found. Please complete your profile first.', 'warning')
            return redirect(url_for('profile'))
        
        # Check if all required fields are filled with better validation
        required_fields = ['region', 'budget', 'gender', 'height', 'weight', 'age', 'activity_level', 'fitness_goal']
        missing_fields = []
        
        print(f"AI Recipes - Validating user data: {user}")
        
        for i, field in enumerate(required_fields):
            value = user[i]
            print(f"Field {field}: value = {value}, type = {type(value)}")
            
            # More lenient validation - only check if field is completely empty
            if value is None or value == '' or (isinstance(value, str) and value.strip() == ''):
                missing_fields.append(field)
                print(f"Missing field: {field} (value: {value})")
        
        print(f"Missing fields: {missing_fields}")
        
        if missing_fields:
            flash(f'Please complete your profile first. Missing: {", ".join(missing_fields)}', 'warning')
            return redirect(url_for('profile'))
        
        region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal = user
        
        user_data = {
            'age': age,
            'gender': gender,
            'height': height,
            'weight': weight,
            'activity_level': activity_level,
            'fitness_goal': fitness_goal,
            'region': region,
            'budget': budget,
            'allergies': allergies
        }
        
        print(f"AI Recipes - Processed user data: {user_data}")
        
        # Generate AI recipes if available
        ai_recipes_data = None
        if AI_AVAILABLE:
            try:
                ai_recipes_data = ai_enhancements.generate_recipe_suggestions(user_data)
                print(f"AI Recipes - Generated data: {ai_recipes_data}")
                
                # Check allergy safety for each recipe
                if ai_recipes_data and 'recipes' in ai_recipes_data:
                    for recipe in ai_recipes_data['recipes']:
                        if 'ingredients' in recipe:
                            allergy_check = check_recipe_allergy_safety(recipe['ingredients'], allergies)
                            recipe['allergy_safety'] = allergy_check
                            recipe['is_safe'] = allergy_check['safe']
                            recipe['allergy_warnings'] = allergy_check['warnings']
                
            except Exception as e:
                print(f"AI recipes error: {e}")
        
        return render_template('ai_recipes.html', 
                             user_data=user_data,
                             ai_recipes=ai_recipes_data,
                             ai_available=AI_AVAILABLE,
                             user_allergies=allergies)
                             
    except Exception as e:
        print(f"AI recipes route error: {e}")
        flash(f'Error loading AI recipes: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/ai_workout_plan')
def ai_workout_plan():
    """AI-powered workout plan"""
    if 'user_id' not in session:
        flash('Please log in to access AI workout plans.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    try:
        # Get user data with debugging
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
        user = c.fetchone()
        conn.close()
        
        print(f"AI Workout Plan - User data for user {user_id}: {user}")
        
        if not user:
            flash('User profile not found. Please complete your profile first.', 'warning')
            return redirect(url_for('profile'))
        
        # Check if all required fields are filled with better validation
        required_fields = ['region', 'budget', 'gender', 'height', 'weight', 'age', 'activity_level', 'fitness_goal']
        missing_fields = []
        
        print(f"AI Workout Plan - Validating user data: {user}")
        
        for i, field in enumerate(required_fields):
            value = user[i]
            print(f"Field {field}: value = {value}, type = {type(value)}")
            
            # More lenient validation - only check if field is completely empty
            if value is None or value == '' or (isinstance(value, str) and value.strip() == ''):
                missing_fields.append(field)
                print(f"Missing field: {field} (value: {value})")
        
        print(f"Missing fields: {missing_fields}")
        
        if missing_fields:
            flash(f'Please complete your profile first. Missing: {", ".join(missing_fields)}', 'warning')
            return redirect(url_for('profile'))
        
        region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal = user
        
        user_data = {
            'age': age,
            'gender': gender,
            'height': height,
            'weight': weight,
            'activity_level': activity_level,
            'fitness_goal': fitness_goal,
            'region': region,
            'budget': budget,
            'allergies': allergies
        }
        
        print(f"AI Workout Plan - Processed user data: {user_data}")
        
        # Generate AI workout plan if available
        ai_workout_data = None
        if AI_AVAILABLE:
            try:
                ai_workout_data = ai_enhancements.generate_workout_plan_ai(user_data)
                print(f"AI Workout Plan - Generated data: {ai_workout_data}")
            except Exception as e:
                print(f"AI workout plan error: {e}")
        
        return render_template('ai_workout_plan.html', 
                             user_data=user_data,
                             ai_workout=ai_workout_data,
                             ai_available=AI_AVAILABLE)
                             
    except Exception as e:
        print(f"AI workout plan route error: {e}")
        flash(f'Error loading AI workout plan: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/ai_progress_analysis')
def ai_progress_analysis():
    """AI-powered progress analysis"""
    if 'user_id' not in session:
        flash('Please log in to access AI progress analysis.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    try:
        # Get user data and progress with debugging
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
        user = c.fetchone()
        
        print(f"AI Progress Analysis - User data for user {user_id}: {user}")
        
        if not user:
            flash('User profile not found. Please complete your profile first.', 'warning')
            conn.close()
            return redirect(url_for('profile'))
        
        # Check if all required fields are filled with better validation
        required_fields = ['region', 'budget', 'gender', 'height', 'weight', 'age', 'activity_level', 'fitness_goal']
        missing_fields = []
        
        print(f"AI Progress Analysis - Validating user data: {user}")
        
        for i, field in enumerate(required_fields):
            value = user[i]
            print(f"Field {field}: value = {value}, type = {type(value)}")
            
            # More lenient validation - only check if field is completely empty
            if value is None or value == '' or (isinstance(value, str) and value.strip() == ''):
                missing_fields.append(field)
                print(f"Missing field: {field} (value: {value})")
        
        print(f"Missing fields: {missing_fields}")
        
        if missing_fields:
            flash(f'Please complete your profile first. Missing: {", ".join(missing_fields)}', 'warning')
            conn.close()
            return redirect(url_for('profile'))
        
        # Get progress data
        c.execute('SELECT COUNT(*) FROM workouts WHERE user_id = ?', (user_id,))
        total_workouts = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM meals WHERE user_id = ?', (user_id,))
        total_meals = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM goals WHERE user_id = ? AND status = "completed"', (user_id,))
        completed_goals = c.fetchone()[0]
        
        c.execute('SELECT weight FROM weight_log WHERE user_id = ? ORDER BY date DESC LIMIT 2', (user_id,))
        weight_data = c.fetchall()
        
        conn.close()
        
        region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal = user
        
        user_data = {
            'age': age,
            'gender': gender,
            'height': height,
            'weight': weight,
            'activity_level': activity_level,
            'fitness_goal': fitness_goal,
            'region': region,
            'budget': budget,
            'allergies': allergies
        }
        
        progress_data = {
            'total_workouts': total_workouts,
            'total_meals': total_meals,
            'completed_goals': completed_goals,
            'weight_data': weight_data,
            'current_weight': weight
        }
        
        print(f"AI Progress Analysis - Processed user data: {user_data}")
        print(f"AI Progress Analysis - Progress data: {progress_data}")
        
        # Generate AI progress analysis if available
        ai_analysis_data = None
        if AI_AVAILABLE:
            try:
                ai_analysis_data = ai_enhancements.analyze_progress(user_data, progress_data)
                print(f"AI Progress Analysis - Generated data: {ai_analysis_data}")
            except Exception as e:
                print(f"AI progress analysis error: {e}")
        
        return render_template('ai_progress_analysis.html', 
                             user_data=user_data,
                             progress_data=progress_data,
                             ai_analysis=ai_analysis_data,
                             ai_available=AI_AVAILABLE)
                             
    except Exception as e:
        print(f"AI progress analysis route error: {e}")
        flash(f'Error loading AI progress analysis: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/test_profile_update')
def test_profile_update():
    """Test route to check profile update functionality"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'})
    
    user_id = session['user_id']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Get current profile data
        c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
        user_data = c.fetchone()
        
        # Check if profile is complete
        required_fields = ['region', 'budget', 'gender', 'height', 'weight', 'age', 'activity_level', 'fitness_goal']
        missing_fields = []
        
        for i, field in enumerate(required_fields):
            value = user_data[i] if user_data else None
            if value is None or value == '' or (isinstance(value, str) and value.strip() == ''):
                missing_fields.append(field)
        
        return jsonify({
            'user_id': user_id,
            'profile_data': user_data,
            'missing_fields': missing_fields,
            'is_complete': len(missing_fields) == 0,
            'field_names': required_fields
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        conn.close()

@app.route('/force_update_profile', methods=['POST'])
def force_update_profile():
    """Force update profile with test data"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'})
    
    user_id = session['user_id']
    
    try:
        # Test data
        test_data = {
            'region': 'asia',
            'budget': 'medium',
            'allergies': 'none',
            'gender': 'male',
            'height': 175.0,
            'weight': 70.0,
            'age': 25,
            'activity_level': 'moderately_active',
            'fitness_goal': 'weight_loss'
        }
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Update the user profile
        update_query = '''UPDATE users SET 
                         region=?, budget=?, allergies=?, gender=?, height=?, weight=?, age=?, activity_level=?, fitness_goal=? 
                         WHERE id=?'''
        update_values = (
            test_data['region'], test_data['budget'], test_data['allergies'], 
            test_data['gender'], test_data['height'], test_data['weight'], 
            test_data['age'], test_data['activity_level'], test_data['fitness_goal'], 
            user_id
        )
        
        c.execute(update_query, update_values)
        conn.commit()
        
        # Verify the update
        c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
        updated_data = c.fetchone()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Profile force updated with test data',
            'updated_data': updated_data,
            'test_data': test_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/test_ai_coaching')
def test_ai_coaching():
    """Test route to bypass profile validation for AI coaching"""
    if 'user_id' not in session:
        flash('Please log in to access AI coaching.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    try:
        # Get user data
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal FROM users WHERE id=?', (user_id,))
        user = c.fetchone()
        
        if not user:
            flash('User profile not found.', 'warning')
            conn.close()
            return redirect(url_for('profile'))
        
        region, budget, allergies, gender, height, weight, age, activity_level, fitness_goal = user
        
        # Use default values if fields are empty
        user_data = {
            'age': age if age and age > 0 else 25,
            'gender': gender if gender else 'not specified',
            'height': height if height and height > 0 else 170,
            'weight': weight if weight and weight > 0 else 70,
            'activity_level': activity_level if activity_level else 'moderate',
            'fitness_goal': fitness_goal if fitness_goal else 'general fitness',
            'region': region if region else 'global',
            'budget': budget if budget else 'moderate',
            'allergies': allergies if allergies else 'none'
        }
        
        # Get recent workouts and meals
        c.execute('''SELECT date, workout_type, duration, calories_burned 
                     FROM workouts WHERE user_id = ? ORDER BY date DESC LIMIT 5''', (user_id,))
        recent_workouts = c.fetchall()
        
        c.execute('''SELECT date, meal_type, food_name, calories 
                     FROM meals WHERE user_id = ? ORDER BY date DESC LIMIT 5''', (user_id,))
        recent_meals = c.fetchall()
        
        conn.close()
        
        # Generate AI coaching if available
        ai_coaching_data = None
        if AI_AVAILABLE:
            try:
                ai_coaching_data = ai_enhancements.generate_fitness_coaching(
                    user_data, 
                    recent_workouts, 
                    recent_meals
                )
            except Exception as e:
                print(f"AI coaching error: {e}")
        
        return render_template('ai_coaching.html', 
                             user_data=user_data,
                             ai_coaching=ai_coaching_data,
                             recent_workouts=recent_workouts,
                             recent_meals=recent_meals,
                             ai_available=AI_AVAILABLE)
                             
    except Exception as e:
        print(f"Test AI coaching route error: {e}")
        flash(f'Error loading AI coaching: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))