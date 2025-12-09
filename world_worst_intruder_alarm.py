# BEFORE STARTING:
# We need to open the virtual environment, so run the following in the Terminal:
# source dht-env/bin/activate

# Imports and setups
import time
import board
import adafruit_dht
import requests
from datetime import datetime
import smtplib
import ssl
from email.message import EmailMessage

# ---------------------------------------------------------------------------------------

# If both indoor humidity and difference in temp are increasing, we can work out when there is 0, 1 or 2+ people in the room

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
    
# Checks how many people are in the room
def check_intruder_presence(dht):
    
    
    
    intruder_number = 1
    return intruder_number

# Send SMS to phone
def send_email_alert(dht):
    return

# Open intruder alert image on screen
def show_intruder_on_screen(dht):
    return