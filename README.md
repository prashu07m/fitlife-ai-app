# FitLife - Fitness & Diet Tracking App

A modern, comprehensive fitness and diet tracking application built with Flask. Track your workouts, meals, weight, and progress with beautiful visualizations and personalized recommendations.

## ✨ Features

### 🏃‍♂️ Fitness Tracking
- **Workout Logging**: Log different types of workouts (Cardio, Strength Training, HIIT, Yoga, etc.)
- **Exercise Details**: Record specific exercises, duration, and calories burned
- **Progress Analytics**: View workout statistics and trends
- **Workout History**: Complete history of all your workouts

### 🍎 Diet Management
- **Meal Logging**: Track meals with detailed nutrition information
- **Macro Tracking**: Monitor protein, carbs, fat, and fiber intake
- **Nutrition Analytics**: Visualize your macro distribution
- **Meal History**: Complete history of all your meals

### 📊 Dashboard & Analytics
- **Personal Dashboard**: Overview of your fitness journey
- **Progress Charts**: Interactive charts for weight and nutrition tracking
- **Statistics**: Comprehensive stats and metrics
- **Real-time Updates**: Live progress tracking

### 🎯 Goal Setting
- **Multiple Goal Types**: Weight loss/gain, workout frequency, strength goals, etc.
- **Progress Tracking**: Visual progress bars and percentage completion
- **Goal Management**: Set, update, and track multiple goals
- **Achievement System**: Celebrate your milestones

### ⚖️ Weight Tracking
- **Weight Logging**: Daily weight entries with notes
- **Progress Visualization**: Weight trend charts
- **Statistics**: Weight change analysis and averages
- **BMI Calculation**: Automatic BMI calculation and categorization

### 👤 User Profile
- **Comprehensive Profile**: Age, height, weight, activity level, fitness goals
- **Personalization**: Region, budget, allergies, and preferences
- **BMI Analysis**: Health status and recommendations
- **Profile Summary**: Quick overview of your stats

### 🧠 Smart Recommendations
- **Personalized Plans**: Workout and diet recommendations based on your profile
- **BMI-based Advice**: Tailored recommendations for your health status
- **Goal-specific Guidance**: Recommendations aligned with your fitness goals
- **Allergy Considerations**: Diet recommendations that respect your allergies

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd kamalika
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 📱 How to Use

### 1. Registration & Profile Setup
- Create a new account with username and password
- Complete your profile with personal information
- Set your fitness goals and preferences

### 2. Dashboard Overview
- View your fitness statistics and recent activities
- Check your progress towards goals
- Access quick actions for logging workouts and meals

### 3. Fitness Tracking
- Log your workouts with type, duration, and calories burned
- Add specific exercises and notes
- View your workout history and statistics

### 4. Diet Tracking
- Log meals with detailed nutrition information
- Track macronutrients (protein, carbs, fat, fiber)
- View nutrition analytics and trends

### 5. Goal Management
- Set personalized fitness and diet goals
- Track your progress with visual indicators
- Update your current values as you progress

### 6. Weight Tracking
- Log your weight regularly
- View weight trends and changes
- Monitor your BMI and health status

### 7. Get Recommendations
- Receive personalized workout and diet recommendations
- Get advice based on your BMI and goals
- Consider your allergies and preferences

## 🛠️ Technical Details

### Database Schema
The app uses SQLite with the following main tables:
- **users**: User profiles and preferences
- **workouts**: Workout logs and details
- **meals**: Meal logs and nutrition data
- **goals**: User goals and progress
- **weight_log**: Weight tracking entries
- **achievements**: User achievements and milestones

### Key Technologies
- **Backend**: Flask (Python web framework)
- **Database**: SQLite (lightweight, file-based)
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js for data visualization
- **Icons**: Font Awesome for UI icons
- **Styling**: Modern CSS with gradients and animations

### Security Features
- Password hashing with Werkzeug
- Session management
- Input validation and sanitization
- SQL injection prevention

## 🎨 Design Features

### Modern UI/UX
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Gradient Backgrounds**: Beautiful purple gradient theme
- **Card-based Layout**: Clean, organized information display
- **Interactive Elements**: Hover effects and smooth animations
- **Progress Indicators**: Visual progress bars and charts

### Color Scheme
- **Primary**: Purple gradient (#667eea to #764ba2)
- **Success**: Green (#27ae60)
- **Warning**: Orange (#f39c12)
- **Danger**: Red (#e74c3c)
- **Info**: Blue (#17a2b8)

## 📊 Analytics & Insights

### Workout Analytics
- Total workouts completed
- Calories burned
- Average workout duration
- Workout type distribution

### Nutrition Analytics
- Total calories consumed
- Macro distribution (protein, carbs, fat)
- Meal frequency analysis
- Nutrition trends over time

### Progress Tracking
- Weight change over time
- BMI trends
- Goal completion rates
- Achievement milestones

## 🔮 Future Enhancements

### Planned Features
- **Social Features**: Connect with friends, share achievements
- **Recipe Database**: Built-in healthy recipes
- **Exercise Library**: Comprehensive exercise database
- **Mobile App**: Native mobile application
- **Data Export**: Export your data for backup
- **Notifications**: Reminder system for workouts and meals
- **Integration**: Connect with fitness devices and apps

### Technical Improvements
- **API Development**: RESTful API for mobile apps
- **Advanced Analytics**: Machine learning recommendations
- **Data Visualization**: More advanced charts and graphs
- **Performance Optimization**: Caching and database optimization

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues or have questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information

## 🙏 Acknowledgments

- Flask community for the excellent web framework
- Chart.js for beautiful data visualizations
- Font Awesome for the icon library
- All contributors and users of FitLife

---

**Made with ❤️ for fitness enthusiasts everywhere** 