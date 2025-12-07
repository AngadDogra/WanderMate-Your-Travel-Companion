from django.shortcuts import render, redirect
from django.contrib.auth import login
from opencage.geocoder import OpenCageGeocode
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView 
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
import requests
from plannerproject import settings
from datetime import datetime, timedelta
import os
import google.generativeai as genai
import re
import json
from django.core.cache import cache

geocoder = OpenCageGeocode(settings.OPENCAGE_API_KEY)

def generate_itinerary(dest, attractions, num_days=3):
    """Generate or retrieve cached itinerary for a destination"""
    itinerary_cleaned = None
    
    # Create cache key based on destination, attractions, and number of days
    attraction_names = [a.get('name', '') for a in attractions[:5]]
    cache_key = f"itinerary_{dest.lower().replace(' ', '_')}_{num_days}days_{hash(tuple(attraction_names))}"
    
    # Try to get from cache first (cache for 7 days)
    cached_itinerary = cache.get(cache_key)
    if cached_itinerary:
        print(f"Using cached itinerary for {dest} ({num_days} days)")
        return cached_itinerary
    
    try:
        # Configure Gemini API
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        # Prepare prompt
        attractions_list = ", ".join([a["name"] for a in attractions]) if attractions else "None"

        prompt = (
            f"Create a {num_days}-day travel itinerary for a trip to {dest}. "
            f"The top attractions are: {attractions_list}. "
            f"Organize by Day 1, Day 2, {'Day 3, ' if num_days >= 3 else ''}etc., with morning, afternoon, and evening plans for each day. "
            f"Keep the tone friendly and concise."
        )

        # Generate text with Gemini
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)

        itinerary = response.text.strip()
        itinerary_cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", itinerary)
        
        # Cache the result for 7 days (604800 seconds)
        cache.set(cache_key, itinerary_cleaned, 604800)
        print(f"Cached new itinerary for {dest} ({num_days} days)")

    except Exception as e:
        itinerary_cleaned = f"Could not generate itinerary: {str(e)}"

    return itinerary_cleaned

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
    """Get IATA airport code for a city with fallback options"""
    # Common airport mappings as fallback
    common_airports = {
        'delhi': 'DEL', 'new delhi': 'DEL',
        'mumbai': 'BOM', 'bombay': 'BOM',
        'bangalore': 'BLR', 'bengaluru': 'BLR',
        'hyderabad': 'HYD',
        'chennai': 'MAA',
        'kolkata': 'CCU', 'calcutta': 'CCU',
        'goa': 'GOI',
        'jaipur': 'JAI',
        'pune': 'PNQ',
        'ahmedabad': 'AMD',
        'london': 'LHR',
        'paris': 'CDG',
        'new york': 'JFK',
        'dubai': 'DXB',
        'singapore': 'SIN',
        'bangkok': 'BKK',
        'tokyo': 'NRT',
        'sydney': 'SYD',
        'los angeles': 'LAX',
        'san francisco': 'SFO',
    }
    
    # Check common airports first
    city_lower = city_name.lower().strip()
    if city_lower in common_airports:
        print(f"Using common airport code for {city_name}: {common_airports[city_lower]}")
        return common_airports[city_lower]
    
    # Try API search
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
        'max': 5
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

def get_google_places(city_name):
    """Fetch top attractions for a given city using Google Places API."""
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"top attractions in {city_name}",
        "key": api_key
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            # Enrich results with image URLs
            for place in results:
                if place.get('photos'):
                    # Get the first photo reference
                    photo_reference = place['photos'][0]['photo_reference']
                    # Construct the photo URL
                    place['image_url'] = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photo_reference}&key={api_key}"
                else:
                    # Placeholder image if no photo available
                    place['image_url'] = "https://via.placeholder.com/400x300?text=No+Image"
                    
            return results
        else:
            print(f"Google Places error: {response.text}")
    except Exception as e:
        print(f"Error fetching Google Places data: {e}")
    return []

def search_hotels(city_code, checkin_date, checkout_date, access_token, adults=1):
    """Search for hotels using Amadeus API"""
    url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    params = {
        'cityCode': city_code
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Hotel search response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            hotels = data.get('data', [])[:5]  # Get top 5 hotels
            return hotels
        else:
            print(f"Hotel search error: {response.text}")
    except Exception as e:
        print(f"Error searching hotels: {e}")
    return []

def get_weather(city_name):
    """Get weather forecast using OpenWeather API"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("Warning: OPENWEATHER_API_KEY not found in environment variables")
        return None
        
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric",
        "cnt": 8  # Get 8 forecast entries (24 hours worth)
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"Weather API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Weather data received for: {data.get('city', {}).get('name')}")
            return {
                'city': data.get('city', {}).get('name'),
                'forecast': data.get('list', [])[:8]
            }
        else:
            print(f"Weather API error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error fetching weather data: {e}")
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
        return_date = request.POST.get("return_date")  # Get return date
        
        # If no date provided, use tomorrow
        if not departure_date:
            departure_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Calculate number of days for itinerary
        num_days = 3  # Default
        if departure_date and return_date:
            try:
                dep_date = datetime.strptime(departure_date, "%Y-%m-%d")
                ret_date = datetime.strptime(return_date, "%Y-%m-%d")
                # Add 1 to include both departure and return days
                num_days = max((ret_date - dep_date).days + 1, 1)
                print(f"Calculated trip duration: {num_days} days (from {departure_date} to {return_date})")
            except Exception as e:
                print(f"Error calculating days: {e}")
                num_days = 3

        # Get coordinates (your existing functionality)
        source_lat, source_lng = get_coords(source)
        dest_lat, dest_lng = get_coords(dest)

        # Get Amadeus access token
        access_token = get_amadeus_token()
        
        flights_data = []
        return_flights_data = []
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
                    print(f"Outbound flights found: {len(flights_data)}")
                else:
                    print("No outbound flights found in API response")
                    # Only set error if there are NO outbound flights
                    error_message = "No outbound flights found for the selected route and date."
                
                # Search for return flights if return date provided
                if return_date and origin_code and destination_code:
                    return_flight_results = search_flights(
                        destination_code,  # Return: destination becomes origin
                        origin_code,       # Return: origin becomes destination
                        return_date,
                        access_token
                    )
                    
                    if return_flight_results and return_flight_results.get('data'):
                        for flight in return_flight_results['data']:
                            itinerary = flight['itineraries'][0]
                            segment = itinerary['segments'][0]
                            
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
                            return_flights_data.append(flight_info)
                        print(f"Return flights found: {len(return_flights_data)}")
                    else:
                        print("No return flights found in API response")
                        # Don't set error_message for return flights, just log it
            else:
                error_message = f"Could not find airport codes. Origin: {origin_code}, Destination: {destination_code}"
        else:
            error_message = "Unable to connect to flight search service."
        
        # Fetch attractions
        attractions = get_google_places(dest)
        
        # Fetch weather
        weather_data = get_weather(dest)
        
        # Fetch hotels (if we have destination code)
        hotels_data = []
        if access_token and destination_code:
            # Calculate checkout date based on return date or default to trip duration
            checkin = datetime.strptime(departure_date, "%Y-%m-%d")
            if return_date:
                checkout_date = return_date
            else:
                checkout = checkin + timedelta(days=num_days)
                checkout_date = checkout.strftime("%Y-%m-%d")
            hotels_data = search_hotels(
                destination_code,
                departure_date,
                checkout_date,
                access_token
            )

        itinerary = generate_itinerary(dest, attractions, num_days)
        
        # Calculate estimated trip cost
        total_cost = 0
        if flights_data:
            # Get cheapest outbound flight
            total_cost += min([float(f['price']) for f in flights_data])
        if return_flights_data:
            # Add cheapest return flight
            total_cost += min([float(f['price']) for f in return_flights_data])
        
        # Debug output
        print(f"\n=== CONTEXT DATA ===")
        print(f"Outbound flights: {len(flights_data)}")
        print(f"Return flights: {len(return_flights_data)}")
        print(f"Error message: {error_message}")
        print(f"==================\n")
        
        # Store in session for PDF export (dates are already strings from POST)
        request.session['itinerary'] = itinerary
        request.session['destination'] = dest
        request.session['num_days'] = num_days
        request.session['departure_date'] = request.POST.get('departure_date', '')
        request.session['return_date'] = request.POST.get('return_date', '')
        
        context = {
            "source": source, 
            "destination": dest,
            "departure_date": departure_date,
            "return_date": return_date,
            "num_days": num_days,
            "source_lat": source_lat,
            "source_lng": source_lng,
            "dest_lat": dest_lat,
            "dest_lng": dest_lng,
            "outbound_flights": flights_data,  # Changed key name for clarity
            "flights": flights_data,  # Keep both for backward compatibility
            "return_flights": return_flights_data,
            "error_message": error_message,
            "attractions": attractions,
            "itinerary": itinerary,
            "weather": weather_data,
            "hotels": hotels_data,
            "estimated_cost": total_cost if total_cost > 0 else None
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


def parse_itinerary_for_pdf(itinerary_text):
    """Parse itinerary text into structured data for PDF template"""
    days = []
    lines = itinerary_text.split('\n')
    
    current_day = None
    current_time = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Day headers
        if re.match(r'^Day\s+\d+', line, re.IGNORECASE):
            if current_day and current_time:
                current_day['times'].append(current_time)
            if current_day:
                days.append(current_day)
                
            match = re.match(r'Day\s+(\d+)[:\s]*(.*)', line, re.IGNORECASE)
            day_num = match.group(1) if match else len(days) + 1
            title = match.group(2).strip() if match and match.group(2) else ''
            
            current_day = {
                'day_num': day_num,
                'title': title,
                'times': []
            }
            current_time = None
            
        # Time blocks
        elif re.match(r'^(Morning|Afternoon|Evening|Night|Breakfast|Lunch|Dinner):', line, re.IGNORECASE):
            if current_time:
                current_day['times'].append(current_time)
                
            match = re.match(r'^([^:]+):(.*)', line)
            time_name = match.group(1).strip()
            content = match.group(2).strip()
            
            current_time = {
                'time': time_name,
                'items': []
            }
            if content:
                current_time['items'].append({'type': 'text', 'content': content})
                
        # Activity items
        elif re.match(r'^[\*\-•]\s+', line):
            content = re.sub(r'^[\*\-•]\s+', '', line)
            if current_time:
                current_time['items'].append({'type': 'activity', 'content': content})
            elif current_day:
                if not current_day['times']:
                    current_day['times'].append({'time': '', 'items': []})
                current_day['times'][-1]['items'].append({'type': 'activity', 'content': content})
                
        # Regular text
        else:
            if current_time:
                current_time['items'].append({'type': 'text', 'content': line})
            elif current_day and current_day['times']:
                current_day['times'][-1]['items'].append({'type': 'text', 'content': line})
    
    # Add last time block and day
    if current_time and current_day:
        current_day['times'].append(current_time)
    if current_day:
        days.append(current_day)
    
    return days


def export_itinerary_pdf(request):
    """Export itinerary as PDF"""
    try:
        from weasyprint import HTML, CSS
    except ImportError:
        return HttpResponse("WeasyPrint not installed. Run: pip install weasyprint", status=500)
    
    # Get itinerary from session
    itinerary = request.session.get('itinerary', '')
    destination = request.session.get('destination', 'Trip')
    num_days = request.session.get('num_days', 3)
    departure_date = request.session.get('departure_date', '')
    return_date = request.session.get('return_date', '')
    
    if not itinerary:
        return HttpResponse("No itinerary found. Please generate an itinerary first.", status=404)
    
    # Parse dates
    if departure_date:
        try:
            departure_date = datetime.strptime(departure_date, '%Y-%m-%d')
        except:
            departure_date = None
    
    if return_date:
        try:
            return_date = datetime.strptime(return_date, '%Y-%m-%d')
        except:
            return_date = None
    
    # Parse itinerary
    parsed_itinerary = parse_itinerary_for_pdf(itinerary)
    
    # Render HTML
    context = {
        'destination': destination,
        'num_days': num_days,
        'departure_date': departure_date,
        'return_date': return_date,
        'parsed_itinerary': parsed_itinerary,
    }
    
    html_string = render_to_string('globe/itinerary_pdf.html', context)
    
    # Generate PDF
    pdf_file = HTML(string=html_string).write_pdf()
    
    # Return PDF response
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{destination}_{num_days}Day_Itinerary.pdf"'
    
    return response


@csrf_exempt
def chatbot(request):
    """AI Travel Chatbot using Gemini"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return JsonResponse({'error': 'Message is required'}, status=400)
            
            # Get conversation history from session
            conversation_history = request.session.get('chat_history', [])
            
            # Get destination context if available
            destination = request.session.get('destination', '')
            context = f"The user is planning a trip to {destination}. " if destination else ""
            
            # Configure Gemini
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            # Build conversation context
            chat_context = (
                f"You are WanderMate, a friendly and knowledgeable travel assistant. {context}"
                "Provide helpful, specific travel advice and recommendations. "
                "Keep responses concise (2-3 paragraphs max) and friendly. "
                "If asked about specific places, provide practical tips like best time to visit, must-see spots, local food, etc.\n\n"
            )
            
            # Add conversation history
            for msg in conversation_history[-6:]:  # Last 3 exchanges
                chat_context += f"User: {msg['user']}\nAssistant: {msg['bot']}\n\n"
            
            chat_context += f"User: {user_message}\nAssistant:"
            
            # Generate response
            response = model.generate_content(chat_context)
            bot_response = response.text.strip()
            
            # Update conversation history
            conversation_history.append({
                'user': user_message,
                'bot': bot_response
            })
            
            # Keep only last 10 exchanges
            if len(conversation_history) > 10:
                conversation_history = conversation_history[-10:]
            
            request.session['chat_history'] = conversation_history
            
            return JsonResponse({
                'response': bot_response,
                'success': True
            })
            
        except Exception as e:
            print(f"Chatbot error: {e}")
            return JsonResponse({
                'error': 'Sorry, I encountered an error. Please try again.',
                'success': False
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def clear_chat(request):
    """Clear chat history"""
    if 'chat_history' in request.session:
        del request.session['chat_history']
    return JsonResponse({'success': True})



