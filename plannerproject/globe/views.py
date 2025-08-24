from django.shortcuts import render, redirect
from django.contrib.auth import login
from opencage.geocoder import OpenCageGeocode
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView 
import requests
from plannerproject import settings
from datetime import datetime, timedelta

geocoder = OpenCageGeocode(settings.OPENCAGE_API_KEY)

def get_amadeus_token():
    """Get access token from Amadeus API"""
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    
    data = {
        'grant_type': 'client_credentials',
        'client_id': settings.AMADEUS_API_KEY,
        'client_secret': settings.AMADEUS_API_SECRET
    }
    
    try:
        response = requests.post(url, data=data)
        print(f"Token response status: {response.status_code}")  # Debug
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            print(f"Token error: {response.text}")  # Debug
    except Exception as e:
        print(f"Error getting Amadeus token: {e}")
    return None

def get_airport_code(city_name, access_token):
    """Get IATA airport code for a city"""
    # Try multiple endpoints for better airport detection
    
    # First try: City search
    url = "https://test.api.amadeus.com/v1/reference-data/locations"
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    params = {
        'keyword': city_name,
        'subType': 'AIRPORT,CITY',
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Airport search for {city_name}: {response.status_code}")  # Debug
        
        if response.status_code == 200:
            data = response.json()
            print(f"Airport data: {data}")  # Debug
            
            if data.get('data'):
                # Look for airports first, then cities
                for location in data['data']:
                    if location.get('subType') == 'AIRPORT':
                        return location.get('iataCode')
                
                # If no direct airport, look for city with associated airport
                for location in data['data']:
                    if location.get('subType') == 'CITY':
                        return location.get('iataCode')
                        
                # Fallback: return first available iataCode
                for location in data['data']:
                    if location.get('iataCode'):
                        return location.get('iataCode')
        else:
            print(f"Airport search error: {response.text}")  # Debug
            
    except Exception as e:
        print(f"Error getting airport code for {city_name}: {e}")
    return None

def search_flights(origin_code, destination_code, departure_date, access_token, adults=1):
    """Search for flights using Amadeus API"""
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    params = {
        'originLocationCode': origin_code,
        'destinationLocationCode': destination_code,
        'departureDate': departure_date,
        'adults': adults,
        'currencyCode': 'INR',
        'max': 2  
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Flight search response: {response.status_code}")  # Debug
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Flight search error: {response.text}")  # Debug
            
    except Exception as e:
        print(f"Error searching flights: {e}")
    return None

def get_coords(city_name):
    result = geocoder.geocode(city_name)
    if result:
        return result[0]['geometry']['lat'], result[0]['geometry']['lng']
    return None, None

def home(request):
    context = {}
    
    if request.method == "POST":
        source = request.POST.get("source_city")
        dest = request.POST.get("destination_city")
        departure_date = request.POST.get("departure_date")
        
        # If no date provided, use tomorrow
        if not departure_date:
            departure_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        # Get coordinates (your existing functionality)
        source_lat, source_lng = get_coords(source)
        dest_lat, dest_lng = get_coords(dest)

        # Get Amadeus access token
        access_token = get_amadeus_token()
        
        flights_data = []
        error_message = None
        
        if access_token:
            print(f"Successfully got Amadeus token")  # Debug
            
            # Get airport codes
            origin_code = get_airport_code(source, access_token)
            destination_code = get_airport_code(dest, access_token)
            
            print(f"Origin code: {origin_code}, Destination code: {destination_code}")  # Debug
            
            if origin_code and destination_code:
                # Search for flights
                flight_results = search_flights(
                    origin_code, 
                    destination_code, 
                    departure_date, 
                    access_token
                )
                
                print(f"Flight results found: {len(flight_results.get('data', [])) if flight_results else 0}")  # Debug
                
                if flight_results and flight_results.get('data'):
                    for flight in flight_results['data']:
                        # Parse flight data
                        itinerary = flight['itineraries'][0]  # First itinerary
                        segment = itinerary['segments'][0]    # First segment
                        
                        flight_info = {
                            'airline': segment['carrierCode'],
                            'flight_number': segment['number'],
                            'departure_time': segment['departure']['at'],
                            'arrival_time': segment['arrival']['at'],
                            'departure_airport': segment['departure']['iataCode'],
                            'arrival_airport': segment['arrival']['iataCode'],
                            'duration': itinerary['duration'],
                            'price': flight['price']['total'],
                            'currency': flight['price']['currency'],
                            'stops': len(itinerary['segments']) - 1
                        }
                        flights_data.append(flight_info)
                else:
                    error_message = "No flights found for the selected route and date."
            else:
                error_message = f"Could not find airport codes. Origin: {origin_code}, Destination: {destination_code}"
        else:
            error_message = "Unable to connect to flight search service."

        context = {
            "source": source,
            "destination": dest,
            "departure_date": departure_date,
            "source_lat": source_lat,
            "source_lng": source_lng,
            "dest_lat": dest_lat,
            "dest_lng": dest_lng,
            "flights": flights_data,
            "error_message": error_message
        }

    return render(request, "globe/home.html", context)

# Signup view
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # log the user in after signup
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "globe/signup.html", {"form": form})

# Login view (uses Django's built-in but with our template)
class CustomLoginView(LoginView):
    template_name = "globe/login.html"

# Logout view
class CustomLogoutView(LogoutView):
    next_page = "home"  # redirect after logout using URL name