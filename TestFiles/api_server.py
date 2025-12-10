# BEFORE STARTING:
#   source dht-env/bin/activate
#   python api_server.py

# IMPORTS
from flask import Flask, jsonify, request
import os
import glob
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------------------
# SETUPS

log_folder_location = "/home/pi/Desktop/SIoT/Logs/"
log_file_name_pattern = os.path.join(log_folder_location, "*.txt")  # e.g. /Logs/*.txt

# Create the Flask application
app = Flask(__name__)

# ---------------------------------------------------------------------------------------
# FUNCTIONS

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

# ---------------------------------------------------------------------------------------
# API ENDPOINTS

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

# ---------------------------------------------------------------------------------------
# MAIN

# host='0.0.0.0' makes the server visible on your LAN.
# port=5000 is the default Flask port.
app.run(host="0.0.0.0", port=5000)
