import time
import board
import adafruit_dht

# Use GPIO4 (D4 on the Pi)ss
dht = adafruit_dht.DHT11(board.D4)  # or adafruit_dht.DHT11(board.D4)

while True:
    try:
        temp_c = dht.temperature
        humidity = dht.humidity
        print(f"Temp: {temp_c:.1f} °C, Humidity: {humidity:.1f} %")
    except RuntimeError as e:
        # DHTs are finicky; it's normal to get errors, just try again
        print("Reading error:", e.args[0])
    time.sleep(2)

