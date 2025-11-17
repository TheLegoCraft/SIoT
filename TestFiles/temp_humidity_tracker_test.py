# BEFORE STARTING:
# We need to open the virtual environment, so run the following in the Terminal:
# source dht-env/bin/activate

# Imports and setup
import time
import board
import adafruit_dht
import requests

# Setup of pin4 to be an imput pin from the Temp and Humidity Sensor
dht = adafruit_dht.DHT11(board.D4)

# Function to get the outside temperature
def fetch_outside_temp() -> float | None: # (" -> float | None" is needed as a hint in case the internet is down so the function does not break)
    # We use the Open-Meteo API and call it to get a return of the current outside temperature in °C for the given latitude/longitude.
    # For the location of the house, the latitude and longitude is: 
    latitude = 51.54937129562199
    longitude = -0.13536038725070398
    
    # The url is what is called to gain access to the Open-Meteo API
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}&current=temperature_2m"
    )
    
    # Send a GET request to the API
    response = requests.get(url, timeout=5) # If no response arrives within 5 seconds, it fails
    response.raise_for_status() # Checks for errors
    data = response.json() # Converts the response from json to python
    
    # "try" attempt to get the temperature unless there's an error -> "except" 
    try:
        outside_temp = data["current"]["temperature_2m"]
    except Exception as e:
        print(f"Error fetching outside temperature: {e}")
        outside_temp = None

    return outside_temp

# Function to get inside temperature
def fetch_inside_temp(dht):
    # Attemps to get humidity and return it 
    try:
        indoor_temp = dht.temperature
        return indoor_temp
    except RuntimeError as e:
        print("indoor_temp ERROR") # Will show the error on the terminal
        return None

# Function to get inside Humidity
def fetch_inside_humidity(dht):
    # Attemps to get humidity and return it 
    try:
        indoor_humidity = dht.humidity
        return indoor_humidity
    except RuntimeError as e:
        print("indoor_humidity ERROR") # Will show the error on the terminal
        return None

# As we are attempting to record over the course of a week, we will prompt and add a data point every 15 minutes (900 seconds)
# For this test version it's set to every 10 seconds
while True:
    inside_humidity = fetch_inside_humidity(dht)
    inside_temp = fetch_inside_temp(dht)
    outside_temp = fetch_outside_temp()
    print("I_Humidity:", inside_humidity)
    print("I_Temp:", inside_temp)
    print("O_Temp:", outside_temp)
    time.sleep(10)