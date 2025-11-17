# BEFORE STARTING:
# We need to open the virtual environment, so run the following in the Terminal:
# source dht-env/bin/activate

# Imports and setup
import time
import board
import adafruit_dht
import requests
import matplotlib.pyplot as plot
import matplotlib.dates as mdates
from datetime import datetime

# Setup of GPIO 4 to be an input pin from the Temp and Humidity Sensor
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

# Set-up the plot (Humidity and Temperature Difference against Time)
plot.ion() #Makes the plot interactive so we can update it without closing it
fig, ax1 = plot.subplots() # axis 1 for the temperature
ax2 = ax1.twinx() # axis 2 for the humidity

humidity_array = [] # Empty array to add the humidity values to
temp_difference_array = [] # Empty array to add the temperature values to
time_stamp_array = [] # Empty array to add the time stamp values to

# As we are attempting to record over the course of a week, we will prompt and add a data point every 15 minutes (900 seconds)
while True:
    # Calls the functions to fetch the current values
    current_inside_humidity = fetch_inside_humidity(dht)
    inside_temp = fetch_inside_temp(dht)
    outside_temp = fetch_outside_temp()
    current_time = datetime.now()
    
    # Calculate the temperature difference
    current_temp_difference = inside_temp - outside_temp
    
    # Append the values to the array
    humidity_array.append(current_inside_humidity)
    temp_difference_array.append(current_temp_difference)
    time_stamp_array.append(current_time)
    
    # Clear the plot - using .cla() instead of .clear() stops the axis from stacking
    ax1.cla()
    ax2.cla()   
    
    # Plot the lines and labels for temperature
    ax1.plot(time_stamp_array, temp_difference_array, color="red", label="Temperature difference (°C)")
    ax1.set_ylabel("Temperature difference (°C)", color="red")
    ax1.tick_params(axis="y", labelcolor="red")
    
    # Plot the lines and labels for humidity
    ax2.plot(time_stamp_array, humidity_array, color="blue", label="Humidity (%)")
    ax2.set_ylabel("Humidity (%)", color="blue")
    ax2.tick_params(axis="y", labelcolor="blue")
    # To ensure the label stays on the right, we need to run the following two lines
    ax2.yaxis.set_label_position("right")
    ax2.yaxis.tick_right()
    
    # Add the label for the time
    ax1.set_xlabel("Time_Stamp")
    
    # Add the title
    ax1.set_title("Humidity and Temperature Difference over Time")
    
    # Update the graph
    fig.canvas.draw()
    fig.canvas.flush_events()
    
    # Wait until next reading (15 minutes = 900 seconds)
    time.sleep(900)