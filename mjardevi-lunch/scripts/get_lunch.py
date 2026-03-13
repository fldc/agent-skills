#!/usr/bin/env python3
"""
Hämtar dagens lunchmeny från alla restauranger i Mjärdevi.
"""

import sys
import json
import os
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

API_BASE = "https://lunchaimjardevi.com/api/v4"
CONFIG_DIR = Path.home() / ".config" / "ehh-skills"
CONFIG_FILE = CONFIG_DIR / "config.env"


def load_env_file(env_path):
    """Load simple KEY=VALUE pairs from an env file into the process."""
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def load_api_key():
    """Laddar API-nyckel från ~/.config/ehh-skills/config.env."""
    try:
        load_env_file(CONFIG_FILE)
    except OSError as exc:
        print(f"Warning: Could not read {CONFIG_FILE}: {exc}", file=sys.stderr)

    for env_name in ["MJARDEVI_LUNCH_API_KEY", "LUNCHA_I_MJARDEVI_API_KEY", "API_KEY"]:
        value = os.environ.get(env_name)
        if value:
            return value.strip()

    return None


def parse_args(argv):
    """Parsar argument och accepterar endast valfritt output-format."""
    if not argv:
        return load_api_key(), "text"

    if len(argv) == 1 and argv[0] in {"text", "json"}:
        return load_api_key(), argv[0]

    print(
        "Usage: python scripts/get_lunch.py [text|json]\n"
        "Set API key via MJARDEVI_LUNCH_API_KEY or ~/.config/ehh-skills/config.env.",
        file=sys.stderr,
    )
    sys.exit(2)


def get_restaurants(api_key):
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


def get_menu(restaurant_id, api_key):
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
    api_key, format_type = parse_args(sys.argv[1:])

    if not api_key:
        print(
            "Error: API key required. Set MJARDEVI_LUNCH_API_KEY or configure ~/.config/ehh-skills/config.env.",
            file=sys.stderr,
        )
        sys.exit(1)

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
