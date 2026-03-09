#!/usr/bin/env python3
"""
Hämtar dagens lunchmeny från alla restauranger i Mjärdevi.
"""

import sys
import json
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

API_BASE = "https://lunchaimjardevi.com/api/v4"
API_KEY = "demo"


def load_api_key():
    """Laddar API-nyckel från .api_key fil om den finns."""
    script_dir = Path(__file__).parent
    api_key_file = script_dir / ".api_key"

    skill_root = script_dir.parent
    api_key_file_root = skill_root / ".api_key"

    if api_key_file.exists():
        try:
            with open(api_key_file, "r") as f:
                key = f.read().strip()
                if key:
                    return key
        except Exception as e:
            print(f"Warning: Could not read {api_key_file}: {e}", file=sys.stderr)

    if api_key_file_root.exists():
        try:
            with open(api_key_file_root, "r") as f:
                key = f.read().strip()
                if key:
                    return key
        except Exception as e:
            print(f"Warning: Could not read {api_key_file_root}: {e}", file=sys.stderr)

    return API_KEY


def get_restaurants(api_key=API_KEY):
    """Hämtar lista över alla restauranger."""
    url = f"{API_BASE}/getRestaurants?key={api_key}"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            if data.get("error") == "none":
                return data.get("restaurants", [])
            else:
                print(f"API Error: {data.get('error')}", file=sys.stderr)
                return []
    except urllib.error.URLError as e:
        print(f"Network error: {e}", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}", file=sys.stderr)
        return []


def get_menu(restaurant_id, api_key=API_KEY):
    """Hämtar meny för en specifik restaurang."""
    url = f"{API_BASE}/getMenu?id={restaurant_id}&key={api_key}"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            if data.get("error") == "none":
                return {
                    "name": data.get("name", ""),
                    "menuItems": data.get("menuItems", []),
                }
            elif data.get("error") == "noMenuForTodayYet":
                return {
                    "name": "",
                    "menuItems": [],
                    "error": "Ingen meny tillgänglig än",
                }
            else:
                return {
                    "name": "",
                    "menuItems": [],
                    "error": data.get("error", "Unknown error"),
                }
    except urllib.error.URLError as e:
        return {"name": "", "menuItems": [], "error": f"Network error: {e}"}
    except json.JSONDecodeError as e:
        return {"name": "", "menuItems": [], "error": f"JSON decode error: {e}"}


def format_lunch_menu(restaurants_with_menus, format_type="text"):
    """Formaterar lunchmenyerna för presentation."""
    if format_type == "json":
        return json.dumps(restaurants_with_menus, ensure_ascii=False, indent=2)

    # Text format (default)
    output = []
    output.append(f"# Dagens lunch i Mjärdevi - {datetime.now().strftime('%Y-%m-%d')}")
    output.append("")

    for restaurant in restaurants_with_menus:
        output.append(f"## {restaurant['name']}")

        if restaurant.get("note"):
            output.append(f"*{restaurant['note']}*")
            output.append("")

        if restaurant.get("error"):
            output.append(f"ERROR: {restaurant['error']}")
            output.append("")
            continue

        if not restaurant.get("menuItems"):
            output.append("Ingen meny tillgänglig")
            output.append("")
            continue

        for item in restaurant["menuItems"]:
            title = item.get("title", "")
            desc = item.get("description", "")

            if title:
                output.append(f"**{title}**")
            if desc:
                output.append(f"  {desc}")
            output.append("")

    return "\n".join(output)


def main():
    """Huvudfunktion som hämtar och visar dagens lunch."""
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        format_type = sys.argv[2] if len(sys.argv) > 2 else "text"
    else:
        api_key = load_api_key()
        format_type = "text"

    restaurants = get_restaurants(api_key)

    if not restaurants:
        print("Kunde inte hämta restauranger från API:et", file=sys.stderr)
        sys.exit(1)

    restaurants_with_menus = []
    for restaurant in restaurants:
        menu_data = get_menu(restaurant["id"], api_key)
        restaurants_with_menus.append(
            {
                "id": restaurant["id"],
                "name": restaurant["name"],
                "shortName": restaurant["shortName"],
                "isFoodtruck": restaurant["isFoodtruck"],
                "website": restaurant["website"],
                "note": restaurant.get("note", ""),
                "menuItems": menu_data.get("menuItems", []),
                "error": menu_data.get("error", None),
            }
        )

    output = format_lunch_menu(restaurants_with_menus, format_type)
    print(output)


if __name__ == "__main__":
    main()
