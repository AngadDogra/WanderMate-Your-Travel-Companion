from django.shortcuts import render, redirect
from django.contrib.auth import login
from opencage.geocoder import OpenCageGeocode
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView 

# isko please .env main daal dena
key = "9a88f993bb9844fa96a0c3333931caae"
geocoder = OpenCageGeocode(key)

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

        source_lat, source_lng = get_coords(source)
        dest_lat, dest_lng = get_coords(dest)

        context = {
            "source": source,
            "destination": dest,
            "source_lat": source_lat,
            "source_lng": source_lng,
            "dest_lat": dest_lat,
            "dest_lng": dest_lng
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