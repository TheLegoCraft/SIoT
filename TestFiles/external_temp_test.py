import requests

def get_outside_temperature_c(lat: float, lon: float) -> float | None:
    """
    Returns the current outside temperature in °C for the given latitude/longitude.
    Uses the Open-Meteo free API (no key required).
    """
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}&current=temperature_2m"
    )

    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        # Navigate to the current temperature
        return data["current"]["temperature_2m"]

    except Exception as e:
        print(f"Error fetching outside temperature: {e}")
        return None


if __name__ == "__main__":
    # Quick test when run directly
    lat = 51.54937129562199   # Actual Coordinates
    lon = -0.13536038725070398
    temp = get_outside_temperature_c(lat, lon)
    if temp is not None:
        print(f"Outside temperature: {temp:.1f} °C")
    else:
        print("Could not get outside temperature.")
