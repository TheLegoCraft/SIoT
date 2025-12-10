# BEFORE STARTING:
# We need to open the virtual environment, so run the following in the Terminal:
# source dht-env/bin/activate

# ---------------------------------------------------------------------------------------
# IMPORTS
import time
# Used to read data
import board
import adafruit_dht
import requests
from datetime import datetime, timedelta
# Used to send emails
import smtplib
import ssl
from email.message import EmailMessage
# Used to read log files
import os
import glob 
# Flask API
from flask import Flask, jsonify, request
# New thread to allow the API and program to run together
from threading import Thread

# ---------------------------------------------------------------------------------------
# SETUPS

# Set up to find the folder location
log_folder_location = "/home/pi/Desktop/SIoT/Logs"
log_file_name_pattern = os.path.join(log_folder_location, "*.txt") # Helps glob find all the file names

# Connect to the .gmail server and encrypts the connection
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587  # TLS

# Reads the email name and password from the .bash environment
SENDER_EMAIL = os.environ["ALERT_EMAIL"]
SENDER_PASSWORD = os.environ["ALERT_EMAIL_PASSWORD"]

# Set-up and create the text file
file_log = "/home/pi/Desktop/SIoT/Logs/" + datetime.now().strftime("log_%Y-%m-%d_%H-%M-%S.txt")

# Set-up of GPIO 4 to be an input pin from the Temp and Humidity Sensor
dht = adafruit_dht.DHT11(board.D4)

# Array set-up
humidity_array = [] # Empty array to add the humidity values to
temp_difference_array = [] # Empty array to add the temperature values to
time_stamp_array = [] # Empty array to add the time stamp values to

# Create the Flask application
app = Flask(__name__)

# ---------------------------------------------------------------------------------------
# FUNCTIONS

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

# Splits a single log line into it's variables
def single_log_line_to_variables(line: str):
    # An example of the structure of a line is: 2025-11-28T17:19:41.778891, 81, 20.7, 11.8
    # This stands for: Date & Time, humidity, inside temperature and outside temperature
    
    # To turn a single log line into its corresponding values, we need to split a line across the commas
    split_log_line = line.strip().split(",")
    
    # We can then split the array above into it's corresponding variables
    timestamp, indoor_humidity, indoor_temperature, outdoor_temperature = [part.strip() for part in split_log_line]
    
    # Coverts the strings to their appropriate format
    try:
        # Converts the strings to their appropriate format
        timestamp = datetime.fromisoformat(timestamp)
        indoor_humidity = float(indoor_humidity)
        indoor_temperature = float(indoor_temperature)
        outdoor_temperature = float(outdoor_temperature)
    except (ValueError, TypeError):
        # If conversion fails, skip this line
        return None
    
    # Returns the variables
    return timestamp, indoor_humidity, indoor_temperature, outdoor_temperature

def load_logs_as_lines(pattern: str):
    # Load all the log files (from having to restart the code) and return a structured array of all the timestamps, humidity and temperatures
    log_line_array = []
    
    # Sorts the files in chronological order
    log_files = sorted(glob.glob(pattern))
    
    # Open each log file
    for filepath in log_files:
        with open(filepath, "r") as current_file:
            for line in current_file:
                # Converts a log line into it's constituent variable
                parsed = single_log_line_to_variables(line)
                
                # If no value is present in that line, it skips it
                if parsed is None:
                    continue
                
                # Splits the parsed values into it's variables 
                timestamp, indoor_humidity, indoor_temperature, outdoor_temperature = parsed
                
                # appends a new line to the array
                log_line_array.append(f"time: {timestamp}, hum: {indoor_humidity}, in_temp: {indoor_temperature}, out_temp: {outdoor_temperature}")
        
    # Returns the arrays
    return log_line_array

# Checks how many intruders are in the room
def check_intruder_presence():
    # 80%-85% humidity & temp_diff increasing = 1 intruder in the room
    # 87%+ humidity & temp_diff increasing = 2 intruders in the room
    
    indoor_humidity_array = []
    indoor_temperature_array = []
    outdoor_temperature_array = []
    
    # First it loads all log files and only looks for the latest one
    try:
        log_files = glob.glob(log_file_name_pattern)
    except Exception as e:
        print(f"Error reading log files: {e}")
        return 0
    
    # Read the latest log
    latest_log = max(log_files, key=os.path.getmtime)
    
    # Read the last 4 log entries in that file (last hour)
    with open(latest_log, "r") as f:
        all_lines = f.readlines()
        
        # Check there's more than 4 lines
        if len(all_lines) >= 4:
            lines = all_lines[-4:] # last 4 entries
        else:
            return 0
            
    for line in lines:
        # Converts a log line into it's constituent variable
        parsed = single_log_line_to_variables(line)
        
        # If no value is present in that line, it skips it
        if parsed is None:
            continue
        
        # Splits the parsed values into it's variables 
        timestamp, indoor_humidity, indoor_temperature, outdoor_temperature = parsed
        
        # Append each variable to the array
        indoor_humidity_array.append(indoor_humidity)
        indoor_temperature_array.append(indoor_temperature)
        outdoor_temperature_array.append(outdoor_temperature)

    # Calculate temperature difference array
    temp_difference_array = [it - ot for it, ot in zip(indoor_temperature_array, outdoor_temperature_array)]
    
    # Calculate if temp_difference is increasing and the average humidity over the last hour
    humidity_average = sum(indoor_humidity_array) / 4
    temp_increase = (temp_difference_array[0] - temp_difference_array[-1]) / 2
        
    # Them, we check the last hour of data (last 4 data points in log). If humidity is in the range and temp_diff has been increasing, we can then return the appropiate number of intruders
    if temp_increase > 0:
        if 80 <= humidity_average <= 85:
            return 1
        elif humidity_average >= 87:
            return 2
        else:
            return 0
    else:
        return 0   

# Send alert email
def send_email_alert(number_intruder, latest_alert_time):
    
    # Check that the email hasn't been sent in the last hour
    if latest_alert_time < (datetime.now() - timedelta(hours=1)):
        # Create the email
        msg = EmailMessage()
        msg["From"] = SENDER_EMAIL
        msg["To"] = "fr422@ic.ac.uk"
        msg["Subject"] = "RASPBERRY PI HAS DETECTED INTRUDERS!"
        msg.set_content(f"{number_intruder} intruder(s) have been detected in the room at {datetime.now()}")

        # Connect and send the email
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        print(f"{number_intruder} intruder(s) have been detected in the room at {datetime.now()}")
        
        return datetime.now()
    else:
        return latest_alert_time

# ---------------------------------------------------------------------------------------
# FLASK API ENDPOINTS & INITIATION

@app.get("/latest")
def latest():
    # Returns the latest reading
    lines = load_logs_as_lines(log_file_name_pattern)

    if not lines:
        return jsonify({"error": "no data yet"}), 404
    
    return jsonify(lines[-1])


@app.get("/history")
def history():
    # Returns all logs
    lines = load_logs_as_lines(log_file_name_pattern)

    if not lines:
        return jsonify({"error": "no data yet"}), 404
    
    return "\n".join(lines), 200, {"Content-Type": "text/plain"}


@app.get("/")
def root():
    # Simple index with basic info.
    
    return jsonify({
        "message": "World's Worst Security System - Data API",
        "endpoints": [
            "/latest",
            "/history"
        ]
    })

# Initiation allowing for the api to run in a seperate thread while the rest of the loop continues recording data
def start_api():
    # host='0.0.0.0' makes the server visible on your LAN.
    # port=5000 is the default Flask port.
    app.run(host="0.0.0.0", port=5000)

# Run the Flask API in a seperate thread
api_thread = Thread(target=start_api)
api_thread.daemon = True
api_thread.start()

# ---------------------------------------------------------------------------------------
# Main

latest_alert_time = datetime.now()

# This will be running continiously, but still checking for values every 15 minutes.
while True:
    # Calls the functions to fetch the current values
    current_inside_humidity = fetch_inside_humidity(dht)
    inside_temp = fetch_inside_temp(dht)
    outside_temp = fetch_outside_temp()
    current_time = datetime.now()
    
    # Append the values first before reading the log
    # Had some errors where the program would crash due to a missing reading so now we need to do a check for them
    if (
        current_inside_humidity is None
        or inside_temp is None
        or outside_temp is None
    ):
        if current_inside_humidity is None:
            print("Skipping data point due to missing reading - current_inside_humidity")
        if inside_temp is None:
            print("Skipping data point due to missing reading - inside_temp")
        if outside_temp is None:
            print("Skipping data point due to missing reading - outside_temp")
        time.sleep(900)  # wait 15 minutes
        continue # Re-starts the loop
    
    # Log the data on the .txt file
    current_log = f"{current_time.isoformat()}, {current_inside_humidity}, {inside_temp}, {outside_temp}\n"

    # Append it to the file
    with open(file_log, "a") as f:
        f.write(current_log)
    
    # Check for the number of intruders
    number_of_intruders = check_intruder_presence()
    
    # Check that the email hasn't been sent in the last hour when sending email by giving it the latest alert time
    send_email_alert(number_of_intruders, latest_alert_time)
    
    # Wait until next reading (15 minutes = 900 seconds)
    time.sleep(900)