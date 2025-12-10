# BEFORE STARTING:
# We need to open the virtual environment, so run the following in the Terminal:
# source dht-env/bin/activate

# Imports and setups
import os # os is used to read the files
import glob # glob can be used to output the names of all specific files in the folder, meaning that even if new logs are added we can still read them without them being hard-coded
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Set up to find the folder location
log_folder_location = "/home/pi/Desktop/SIoT/Logs/"
log_file_name_pattern = os.path.join(log_folder_location, "*.txt") # Helps glob find all the file names

# ---------------------------------------------------------------------------------------

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

def load_logs(pattern: str):
    # Load all the log files (from having to restart the code) and return arrays of all the timestamps, humidity and temperatures
    timestamp_array = []
    indoor_humidity_array = []
    indoor_temperature_array = []
    outdoor_temperature_array = []
    
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
                
                # Append each variable to the array
                timestamp_array.append(timestamp)
                indoor_humidity_array.append(indoor_humidity)
                indoor_temperature_array.append(indoor_temperature)
                outdoor_temperature_array.append(outdoor_temperature)
    
    if not timestamp_array:
        # No valid data
        return [], [], [], []
    
    # Check that from the latest data point it's only the last 7 days of data
    latest_time = max(timestamp_array)
    cutoff = latest_time - timedelta(days=7)
    
    # Arrays to store the filtered values
    filtered_timestamp_array = []
    filtered_indoor_humidity_array = []
    filtered_indoor_temperature_array = []
    filtered_outdoor_temperature_array = []
    
    # Runs through all the values in the array and removes any before the cutoff of 7 days
    for t, h, it, ot in zip(timestamp_array,indoor_humidity_array,indoor_temperature_array, outdoor_temperature_array):
        if t>= cutoff:
            filtered_timestamp_array.append(t)
            filtered_indoor_humidity_array.append(h)
            filtered_indoor_temperature_array.append(it)
            filtered_outdoor_temperature_array.append(ot)
        
    # Returns the filterd arrays
    return filtered_timestamp_array, filtered_indoor_humidity_array, filtered_indoor_temperature_array, filtered_outdoor_temperature_array
 
def plot_humidity_vs_temp_difference(timestamp, indoor_humidity, indoor_temperature, outdoor_temperature):
    # Plot humidity and temperature difference vs time
    
    # Calculate temperature difference array
    temp_difference = [it - ot for it, ot in zip(indoor_temperature, outdoor_temperature)]
    
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    # Left axis: temperature difference (°C)
    ax1.plot(timestamp, temp_difference, color="red", label="Temp difference (°C)")
    ax1.set_ylabel("Temp difference (°C)", color="red")
    ax1.tick_params(axis="y", labelcolor="red")

    # Right axis: humidity (%)
    ax2.plot(timestamp, indoor_humidity, color="blue", label="Humidity (%)")
    ax2.set_ylabel("Humidity (%)", color="blue")
    ax2.tick_params(axis="y", labelcolor="blue")
    ax2.yaxis.set_label_position("right")
    ax2.yaxis.tick_right()

    # X-axis formatting
    ax1.set_xlabel("Time")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %H:%M"))
    fig.autofmt_xdate()

    ax1.set_title("Humidity and Temperature Difference over Time")
    ax1.grid(True, which="both", linestyle="--", alpha=0.4)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.tight_layout()
    plt.show()

def plot_humidity_vs_indoor_temperature(timestamp, indoor_humidity, indoor_temperature):
    # Plot humidity and indoor temperature vs time

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    # Left axis: indoor temperature
    ax1.plot(timestamp, indoor_temperature, color="red", label="Indoor temp (°C)")
    ax1.set_ylabel("Indoor temp (°C)", color="red")
    ax1.tick_params(axis="y", labelcolor="red")

    # Right axis: humidity
    ax2.plot(timestamp, indoor_humidity, color="blue", label="Humidity (%)")
    ax2.set_ylabel("Humidity (%)", color="blue")
    ax2.tick_params(axis="y", labelcolor="blue")
    ax2.yaxis.set_label_position("right")
    ax2.yaxis.tick_right()

    # X-axis
    ax1.set_xlabel("Time")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %H:%M"))
    fig.autofmt_xdate()

    ax1.set_title("Humidity and Indoor Temperature over Time")
    ax1.grid(True, which="both", linestyle="--", alpha=0.4)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.tight_layout()
    plt.show()

def plot_humidity_vs_outdoor_temperature(timestamp, indoor_humidity, outdoor_temperature):
    # Plot humidity and outdoor temperature vs time (dual y-axis).

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    # Left axis: outdoor temperature
    ax1.plot(timestamp, outdoor_temperature, color="red", label="Outdoor temp (°C)")
    ax1.set_ylabel("Outdoor temp (°C)", color="red")
    ax1.tick_params(axis="y", labelcolor="red")

    # Right axis: humidity
    ax2.plot(timestamp, indoor_humidity, color="blue", label="Humidity (%)")
    ax2.set_ylabel("Humidity (%)", color="blue")
    ax2.tick_params(axis="y", labelcolor="blue")
    ax2.yaxis.set_label_position("right")
    ax2.yaxis.tick_right()

    # X-axis
    ax1.set_xlabel("Time")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m %H:%M"))
    fig.autofmt_xdate()

    ax1.set_title("Humidity and Outdoor Temperature over Time")
    ax1.grid(True, which="both", linestyle="--", alpha=0.4)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.tight_layout()
    plt.show()
   
# ---------------------------------------------------------------------------------------
   
def main():
    # Load all log values from the latest 7 days since the last measurement
    timestamps, indoor_humidities, indoor_temperature, outdoor_temperature = load_logs(log_file_name_pattern)
    
    # Plotting
    plot_humidity_vs_temp_difference(timestamps, indoor_humidities, indoor_temperature, outdoor_temperature)
    plot_humidity_vs_indoor_temperature(timestamps, indoor_humidities, indoor_temperature)
    plot_humidity_vs_outdoor_temperature(timestamps, indoor_humidities, outdoor_temperature)

# ---------------------------------------------------------------------------------------

main()  
    