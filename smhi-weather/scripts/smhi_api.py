#!/usr/bin/env python3
"""
SMHI Weather API Client
Fetches weather data from SMHI's open API (api.smhi.se)
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime
import json


class SMHIWeather:
    """Client for SMHI's open weather API"""
    
    BASE_URL = "https://opendata-download-metfcst.smhi.se/api"
    WARNINGS_URL = "https://wpt-a.smhi.se/backend-warnings-page"
    
    # Common locations in Östergötland with coordinates
    LOCATIONS = {
        "mjölby": {"lat": 58.3253, "lon": 15.1286, "name": "Mjölby"},
        "linköping": {"lat": 58.4108, "lon": 15.6214, "name": "Linköping"},
        "norrköping": {"lat": 58.5877, "lon": 16.1924, "name": "Norrköping"},
        "motala": {"lat": 58.5370, "lon": 15.0370, "name": "Motala"},
        "vadstena": {"lat": 58.4495, "lon": 14.8894, "name": "Vadstena"},
    }
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_forecast(self, location: str = "mjölby") -> Dict:
        """
        Get weather forecast for a location
        
        Args:
            location: Location name (default: mjölby)
            
        Returns:
            Dictionary with forecast data
        """
        location = location.lower()
        
        if location not in self.LOCATIONS:
            raise ValueError(f"Unknown location: {location}. Available: {', '.join(self.LOCATIONS.keys())}")
        
        coords = self.LOCATIONS[location]
        lat, lon = coords["lat"], coords["lon"]
        
        # SMHI forecast API endpoint
        url = f"{self.BASE_URL}/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "location": coords["name"],
                "coordinates": {"lat": lat, "lon": lon},
                "approved_time": data.get("approvedTime"),
                "reference_time": data.get("referenceTime"),
                "forecast": self._parse_forecast(data.get("timeSeries", []))
            }
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to fetch forecast: {str(e)}"}
    
    def _parse_forecast(self, time_series: List) -> List[Dict]:
        """Parse SMHI time series data into readable format"""
        parsed = []
        
        for entry in time_series:  # Get all available forecast hours
            params = {}
            for param in entry.get("parameters", []):
                name = param.get("name")
                values = param.get("values", [])
                if values:
                    params[name] = values[0]
            
            parsed.append({
                "valid_time": entry.get("validTime"),
                "temperature": params.get("t"),  # Air temperature (°C)
                "feels_like": params.get("t"),  # Simplified - SMHI doesn't provide feels_like
                "humidity": params.get("r"),  # Relative humidity (%)
                "precipitation": params.get("pcat"),  # Precipitation category
                "wind_speed": params.get("ws"),  # Wind speed (m/s)
                "wind_direction": params.get("wd"),  # Wind direction (degrees)
                "visibility": params.get("vis"),  # Visibility (km)
                "cloud_cover": params.get("tcc_mean"),  # Total cloud cover (0-8)
                "weather_symbol": params.get("Wsymb2"),  # Weather symbol
            })
        
        return parsed
    
    def get_warnings(self, county: str = "Östergötland") -> Dict:
        """
        Get active weather warnings for a county
        
        Args:
            county: County name (default: Östergötland)
            
        Returns:
            Dictionary with warning data including all types (weather, fire, water)
        """
        url = f"{self.WARNINGS_URL}/warningAreas"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            all_warnings = response.json()
            
            # Filter warnings for the specified county
            county_warnings = []
            for warning in all_warnings:
                affected_areas = warning.get("affectedAreas", [])
                if any(county in area.get("sv", "") for area in affected_areas):
                    county_warnings.append(warning)
            
            # Parse warnings to our format
            parsed = [self._parse_warning(w) for w in county_warnings]
            
            # Get highest severity level
            highest = self._get_highest_severity(parsed)
            
            return {
                "county": county,
                "warnings": parsed,
                "highest_level": highest,
                "fetched_at": datetime.now().isoformat()
            }
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to fetch warnings: {str(e)}"}
    
    def _parse_warning(self, raw: Dict) -> Dict:
        """Parse raw API data to structured warning format"""
        # Extract event type for categorization
        event_code = raw.get("eventDescription", {}).get("code", "")
        category = self._categorize_warning(event_code)
        
        # Extract descriptions
        descriptions = raw.get("descriptions", [])
        what_happens = self._find_description(descriptions, "HAPPENS")
        what_to_do = self._find_description(descriptions, "AFFECT")
        
        # Extract affected municipality names
        affected_areas = raw.get("affectedAreas", [])
        area_names = [area.get("sv", "") for area in affected_areas]
        
        return {
            "id": raw.get("id"),
            "type": category["type"],
            "emoji": category["emoji"],
            "category": event_code,
            "category_sv": raw.get("eventDescription", {}).get("sv", ""),
            "severity": raw.get("warningLevel", {}).get("code", ""),
            "severity_sv": raw.get("warningLevel", {}).get("sv", ""),
            "title": raw.get("eventDescription", {}).get("sv", ""),
            "description": what_happens,
            "advice": what_to_do,
            "areas": area_names,
            "valid_from": raw.get("approximateStart"),
            "valid_to": raw.get("approximateEnd"),
            "issued_at": raw.get("published"),
        }
    
    def _categorize_warning(self, event_code: str) -> Dict:
        """Categorize warning based on event code"""
        fire_events = ["GRASS_FIRE", "FOREST_FIRE"]
        water_events = ["WATER_SHORTAGE", "HIGH_WATER", "FLOODING"]
        
        if event_code in fire_events:
            return {"type": "fire", "emoji": "🔥"}
        elif event_code in water_events:
            return {"type": "water", "emoji": "💧"}
        else:
            return {"type": "weather", "emoji": "⛈️"}
    
    def _find_description(self, descriptions: List, code: str) -> str:
        """Find specific description from descriptions array"""
        for desc in descriptions:
            if desc.get("title", {}).get("code") == code:
                return desc.get("text", {}).get("sv", "")
        return ""
    
    def _get_highest_severity(self, warnings: List[Dict]) -> str:
        """Determine highest warning level from list"""
        severity_order = {"RED": 3, "ORANGE": 2, "YELLOW": 1, "NONE": 0}
        if not warnings:
            return "NONE"
        highest = max(warnings, key=lambda w: severity_order.get(w.get("severity", "NONE"), 0))
        return highest.get("severity", "NONE")
    
    def get_warnings_summary(self, county: str = "Östergötland") -> str:
        """
        Get a human-readable warnings summary (MEDIUM detail level)
        
        Args:
            county: County name (default: Östergötland)
            
        Returns:
            Formatted warnings summary string
        """
        data = self.get_warnings(county)
        
        if "error" in data:
            return f"⚠️ Kunde inte hämta varningar: {data['error']}"
        
        warnings = data["warnings"]
        
        if not warnings:
            return f"✅ Inga aktiva varningar för {county}."
        
        # Sort by severity (most severe first)
        severity_order = {"RED": 0, "ORANGE": 1, "YELLOW": 2}
        sorted_warnings = sorted(warnings, key=lambda w: severity_order.get(w.get("severity", "YELLOW"), 99))
        
        output = f"AKTIVA VARNINGAR - {county}\n"
        output += "=" * 60 + "\n\n"
        
        for w in sorted_warnings:
            # Severity icon
            severity_icons = {"RED": "🔴", "ORANGE": "🟠", "YELLOW": "🟡"}
            severity_icon = severity_icons.get(w.get("severity", "YELLOW"), "⚠️")
            
            # Format dates
            try:
                valid_from = datetime.fromisoformat(w["valid_from"].replace("Z", "+00:00"))
                valid_to = datetime.fromisoformat(w["valid_to"].replace("Z", "+00:00"))
                date_str = f"{valid_from.strftime('%d %b %H:%M')} - {valid_to.strftime('%d %b %H:%M')}"
            except (ValueError, KeyError):
                date_str = "Okänd tid"
            
            # Build warning text
            output += f"{severity_icon} {w['emoji']} {w['severity_sv'].upper()} VARNING - {w['title']}\n"
            output += f"Gäller: {date_str}\n"
            
            if w.get("areas"):
                areas_text = ", ".join(w["areas"][:3])  # Show max 3 areas
                if len(w["areas"]) > 3:
                    areas_text += f" (+{len(w['areas']) - 3} till)"
                output += f"Områden: {areas_text}\n"
            
            if w.get("description"):
                desc = w["description"][:200]
                if len(w["description"]) > 200:
                    desc += "..."
                output += f"Beskrivning: {desc}\n"
            
            if w.get("advice"):
                advice = w["advice"][:150]
                if len(w["advice"]) > 150:
                    advice += "..."
                output += f"Råd: {advice}\n"
            
            output += "\n"
        
        # Summary by type
        type_counts = {"weather": 0, "fire": 0, "water": 0}
        for w in warnings:
            wtype = w.get("type", "weather")
            type_counts[wtype] = type_counts.get(wtype, 0) + 1
        
        if type_counts["fire"] == 0 and type_counts["water"] == 0:
            output += "✅ Inga brandvarningar eller vattenvarningar aktiva.\n"
        
        return output
    
    def get_weather_summary(self, location: str = "mjölby", hours: int = 12) -> str:
        """
        Get a human-readable weather summary
        
        Args:
            location: Location name (default: mjölby)
            hours: Number of hours to include (default: 12)
            
        Returns:
            Formatted weather summary string
        """
        forecast_data = self.get_forecast(location)
        
        if "error" in forecast_data:
            return forecast_data["error"]
        
        loc_name = forecast_data["location"]
        forecast = forecast_data["forecast"][:hours]
        
        summary = f"Väderprognos för {loc_name}\n"
        summary += "=" * 50 + "\n\n"
        
        for entry in forecast:
            time = entry["valid_time"]
            temp = entry.get("temperature", "N/A")
            precip = self._precipitation_category(entry.get("precipitation"))
            wind = entry.get("wind_speed", "N/A")
            
            summary += f"{time}: {temp}°C, {precip}, Vind: {wind} m/s\n"
        
        return summary
    
    def _precipitation_category(self, pcat: Optional[int]) -> str:
        """Convert precipitation category to Swedish text"""
        if pcat is None:
            return "Okänd"
        categories = {
            0: "Ingen nederbörd",
            1: "Snö",
            2: "Snöblandat regn",
            3: "Regn",
            4: "Duggregn",
            5: "Underkylt regn",
            6: "Underkylt duggregn"
        }
        return categories.get(pcat, "Okänd")
    
    def get_current_weather(self, location: str = "mjölby") -> Dict:
        """
        Get current weather (first entry in forecast)
        
        Args:
            location: Location name (default: mjölby)
            
        Returns:
            Dictionary with current weather data
        """
        forecast_data = self.get_forecast(location)
        
        if "error" in forecast_data:
            return forecast_data
        
        current = forecast_data["forecast"][0] if forecast_data["forecast"] else {}
        
        return {
            "location": forecast_data["location"],
            "time": current.get("valid_time"),
            "temperature": current.get("temperature"),
            "humidity": current.get("humidity"),
            "precipitation": self._precipitation_category(current.get("precipitation")),
            "wind_speed": current.get("wind_speed"),
            "wind_direction": current.get("wind_direction"),
            "cloud_cover": current.get("cloud_cover"),
        }


def main():
    """Example usage"""
    client = SMHIWeather()
    
    # Get current weather for Mjölby
    print("Current weather:")
    current = client.get_current_weather("mjölby")
    print(json.dumps(current, indent=2, ensure_ascii=False))
    
    print("\n" + "="*50 + "\n")
    
    # Get weather summary
    print(client.get_weather_summary("mjölby", hours=8))
    
    print("\n" + "="*50 + "\n")
    
    # Get warnings for Östergötland
    print("Vädervarningar för Östergötland:")
    print(client.get_warnings_summary())


if __name__ == "__main__":
    main()
