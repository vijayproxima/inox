from geopy.geocoders import Nominatim
from time import sleep
from random import randint

def get_lat_long(pincode):
    geolocator = Nominatim(user_agent="geoapiExercises")
    sleep(randint(1*100,2*100)/100)
    location = geolocator.geocode({"postalcode": pincode, "country": "India"})
    if location:
        return (location.latitude, location.longitude)
    else:
        return None

# def get_Location(latitude,longitude):
#     geolocator = Nominatim(user_agent="geoapiExercises")
#     location = geolocator.reverse(str(latitude) + "," + str(longitude))
#     return location

# pincode = "140507"  # Example pincode

# latitude, longitude = get_lat_long(pincode)

# location = get_Location(latitude,longitude)


# if latitude and longitude:
#     print(f"Latitude: {latitude}, Longitude: {longitude}, Location: {location}")
# else:
#     print("Location not found for the given pincode.")
