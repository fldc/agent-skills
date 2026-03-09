#!/usr/bin/env python3
"""
Simple CLI wrapper for SMHI weather queries
Usage: weather_cli.py <command> [location]
"""

import sys
from pathlib import Path

# Add script directory to path
sys.path.insert(0, str(Path(__file__).parent))

from smhi_api import SMHIWeather


def main():
    if len(sys.argv) < 2:
        print("Usage: weather_cli.py <current|forecast|warnings> [location]")
        sys.exit(1)
    
    command = sys.argv[1]
    location = sys.argv[2] if len(sys.argv) > 2 else "mjölby"
    
    client = SMHIWeather()
    
    if command == "current":
        weather = client.get_current_weather(location)
        if "error" in weather:
            print(f"❌ {weather['error']}")
            return
        
        print(f"🌡️  Temperatur: {weather['temperature']}°C")
        print(f"💧 Luftfuktighet: {weather['humidity']}%")
        print(f"🌨️  Nederbörd: {weather['precipitation']}")
        print(f"💨 Vind: {weather['wind_speed']} m/s")
        print(f"☁️  Molnighet: {weather['cloud_cover']}/8")
    
    elif command == "forecast":
        hours = int(sys.argv[3]) if len(sys.argv) > 3 else 12
        summary = client.get_weather_summary(location, hours)
        print(summary)
    
    elif command == "warnings":
        county = sys.argv[2] if len(sys.argv) > 2 else "Östergötland"
        summary = client.get_warnings_summary(county)
        print(summary)
    
    else:
        print(f"Unknown command: {command}")
        print("Available: current, forecast, warnings")
        sys.exit(1)


if __name__ == "__main__":
    main()
