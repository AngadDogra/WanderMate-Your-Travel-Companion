# 🌍 WanderMate - Your Ultimate Travel Companion

A comprehensive travel planning platform built with Django that helps users plan perfect trips with real-time flight searches, hotel recommendations, weather forecasts, attraction discovery, and AI-powered itinerary generation.

![WanderMate](https://img.shields.io/badge/Django-5.2.8-green)
![Python](https://img.shields.io/badge/Python-3.14-blue)
![Status](https://img.shields.io/badge/Status-Active-success)

## ✨ Features

### 🎯 Core Features
- **🔍 Smart Trip Search** - Search for trips between any two cities with flexible date selection
- **✈️ Flight Comparison** - Real-time flight search with pricing, duration, and airline details
- **🏨 Hotel Recommendations** - Discover top-rated hotels at your destination
- **🗺️ Attraction Discovery** - Browse top attractions with images, ratings, and reviews
- **🌤️ Weather Forecasts** - 3-day weather forecast for your destination
- **🤖 AI Itinerary Generator** - Get personalized 3-day travel plans powered by Google Gemini AI
- **🌐 Interactive 3D Globe** - Visualize your travel route on a stunning interactive globe
- **💰 Cost Estimator** - Get estimated trip costs based on flight prices
- **👤 User Authentication** - Secure login and signup system
- **💾 Save Trips** - Save your favorite trips for future reference (Model ready)

### 🎨 UI/UX Features
- Modern, professional dark-themed interface
- Responsive design for all devices
- Glass morphism effects
- Smooth animations and transitions
- Image galleries with lazy loading
- Interactive flight cards
- Weather widgets
- Cost breakdown displays

## 🛠️ Technology Stack

### Backend
- **Django 5.2.8** - Web framework
- **Python 3.14** - Programming language
- **SQLite** - Database

### Frontend
- **HTML5 & CSS3** - Modern web standards
- **JavaScript** - Interactive features
- **Three.js & Globe.gl** - 3D globe visualization
- **Font Awesome** - Icon library
- **Google Fonts (Poppins)** - Typography

### APIs & Services
- **Amadeus API** - Flight and hotel search
- **Google Places API** - Attraction discovery with images
- **Google Gemini AI** - AI-powered itinerary generation
- **OpenWeather API** - Weather forecasts
- **OpenCage Geocoding API** - Location coordinates

## 📋 Prerequisites

- Python 3.14 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- API keys for:
  - Google Gemini AI
  - Google Places API
  - Amadeus API
  - OpenWeather API (optional)
  - OpenCage Geocoding API

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Chanchreek/WanderMate-Your-Travel-Companion.git
cd WanderMate-Your-Travel-Companion/plannerproject
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the `plannerproject` directory:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_PLACES_API_KEY=your_google_places_key
OPENWEATHER_API_KEY=your_openweather_key
AMADEUS_API_KEY=your_amadeus_key
AMADEUS_API_SECRET=your_amadeus_secret
OPENCAGE_API_KEY=your_opencage_key
```

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser! 🎉

## 🔑 Getting API Keys

### Google Gemini AI
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy and paste into `.env`

### Google Places API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "Places API"
4. Create credentials (API Key)
5. Copy and paste into `.env`

### Amadeus API
1. Visit [Amadeus for Developers](https://developers.amadeus.com/)
2. Sign up for a free account
3. Create a new app
4. Copy API Key and API Secret
5. Paste both into `.env`

### OpenWeather API
1. Go to [OpenWeather](https://openweathermap.org/api)
2. Sign up for free account
3. Generate API key
4. Copy and paste into `.env`

### OpenCage Geocoding API
1. Visit [OpenCage](https://opencagedata.com/)
2. Sign up for free account
3. Get your API key
4. Copy and paste into `.env`

## 📁 Project Structure

```
WanderMate-Your-Travel-Companion/
├── plannerproject/
│   ├── globe/                      # Main app
│   │   ├── templates/
│   │   │   └── globe/
│   │   │       ├── home.html       # Main page (redesigned)
│   │   │       ├── login.html
│   │   │       ├── signup.html
│   │   │       └── base.html
│   │   ├── models.py               # Database models (Profile, SavedTrip)
│   │   ├── views.py                # Business logic (updated with new APIs)
│   │   ├── urls.py
│   │   └── admin.py
│   ├── plannerproject/             # Project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env                        # Environment variables (create this)
│   ├── .env.example                # Example env file
│   └── db.sqlite3                  # Database
├── Jenkinsfile
└── README.md
```

## 🎯 Usage Guide

### Searching for Trips
1. Enter your origin city (e.g., "Delhi")
2. Enter your destination city (e.g., "Hyderabad")
3. Select departure date
4. Click "Search Trips"

### Viewing Results
The results page shows:
- **Weather Forecast** - Current weather and 3-day forecast
- **3D Globe** - Interactive visualization of your route
- **Available Flights** - List of flights with prices and details
- **Hotels** - Recommended accommodations
- **Attractions** - Top-rated places with images and ratings
- **AI Itinerary** - Day-by-day travel plan
- **Cost Estimate** - Estimated trip cost

## 🎨 UI Improvements Made

### Before vs After
- ❌ Basic HTML styling → ✅ Modern glass morphism design
- ❌ Text-only attractions → ✅ Image cards with ratings
- ❌ No weather info → ✅ Beautiful weather widgets
- ❌ No hotels → ✅ Hotel recommendations
- ❌ No cost estimate → ✅ Trip cost calculator
- ❌ Plain forms → ✅ Elegant search interface
- ❌ Static layout → ✅ Responsive, animated UI

### Design Features
- **Color Scheme**: Dark theme with cyan/indigo accents
- **Typography**: Poppins font family
- **Components**: Card-based layouts with hover effects
- **Responsiveness**: Mobile-first design
- **Animations**: Smooth transitions and micro-interactions

## 🔧 Configuration

### Django Settings
Edit `plannerproject/settings.py` for:
- Database configuration
- Static files settings
- Security settings
- API key loading

### Customization
- Modify color scheme in CSS `:root` variables
- Adjust API result limits in `views.py`
- Change globe visualization settings in JavaScript

## 📊 Database Models

### Profile Model
```python
user: User (OneToOne)
country: CharField
budget: DecimalField
preferred_activities: TextField
```

### SavedTrip Model
```python
user: User (ForeignKey)
source_city: CharField
destination_city: CharField
departure_date: DateField
estimated_cost: DecimalField
created_at: DateTimeField
notes: TextField
```

## 🐛 Troubleshooting

### Common Issues

**API Key Errors**
- Ensure all API keys are correctly added to `.env`
- Check API key permissions and quotas
- Restart Django server after changing `.env`

**No Flight Results**
- Verify Amadeus API credentials
- Check if route is available in test environment
- Try different cities with major airports

**Globe Not Loading**
- Check internet connection (CDN resources)
- Clear browser cache
- Ensure JavaScript is enabled

**Weather Not Showing**
- Verify OpenWeather API key
- Check API quota limits
- Ensure city name is correct

## 🚀 Future Enhancements

- [ ] Trip saving/bookmarking functionality (UI implementation)
- [ ] User dashboard with saved trips
- [ ] Multi-city trip planning
- [ ] Budget tracking and recommendations
- [ ] Social features (share trips)
- [ ] Mobile app version
- [ ] Hotel booking integration
- [ ] Flight booking integration
- [ ] Travel insurance recommendations
- [ ] Visa requirements checker
- [ ] Currency converter
- [ ] Packing list generator

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Developer

- **Chanchreek** - [GitHub Profile](https://github.com/Chanchreek)

## 🙏 Acknowledgments

- Amadeus for travel API
- Google for Gemini AI and Places API
- OpenWeather for weather data
- OpenCage for geocoding services
- Three.js and Globe.gl for 3D visualization

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review API documentation

---

Made with ❤️ for travelers worldwide 🌍✈️
