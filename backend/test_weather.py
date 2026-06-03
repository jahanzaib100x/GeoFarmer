import requests
import json

def run_weather_test():
    """
    Test client script to verify the hyper-local weather forecast endpoint.
    Retrieves the 7-day meteorological charts based on farm GPS coordinates.
    """
    url = "http://localhost:8000/api/weather"
    
    # Target Coordinates: Multan area
    params = {
        "lat": 30.1575,
        "lon": 71.5249
    }
    
    print(f"Requesting 7-day local agricultural weather forecast for coordinates: {params['lat']}, {params['lon']}...")
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print("\n" + "="*60)
            print("PRECISION WEATHER REPORT RECEIVED (Source: {})".format(result.get("source")))
            print("="*60)
            print("Location: {}".format(result.get("city")))
            print("Coordinates: Lat={}, Lon={}".format(result.get("latitude"), result.get("longitude")))
            print("-"*60)
            for day_info in result.get("forecast", []):
                print("Day: {:<10} | Temp: {:<15} | Wind: {:<18} | Rain: {}".format(
                    day_info.get("day"),
                    day_info.get("temp_range"),
                    day_info.get("wind"),
                    day_info.get("rain_chance")
                ))
            print("="*60)
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Connection failure: {e}")

if __name__ == "__main__":
    run_weather_test()
