# SMHI API Reference

This document provides detailed information about SMHI's open weather API and the parameters available.

## API Endpoints

### Weather Forecast
```
https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json
```

Returns weather forecast for a specific geographic point.

### Weather Warnings
```
https://wpt-a.smhi.se/backend-warnings-page/warningAreas
```

Returns active weather warnings for Sweden (all types: weather, fire, water).

**Note:** The old API endpoint at `opendata-download-warnings.smhi.se` is deprecated as of January 2026.

## Weather Parameters

The forecast API returns the following parameters:

| Parameter | Name | Unit | Description |
|-----------|------|------|-------------|
| `t` | Air temperature | °C | Temperature 2m above ground |
| `r` | Relative humidity | % | Relative humidity at 2m |
| `ws` | Wind speed | m/s | Wind speed at 10m height |
| `wd` | Wind direction | degrees | Wind direction (0=north, 90=east) |
| `pcat` | Precipitation category | 0-6 | Type of precipitation |
| `pmean` | Precipitation | mm/h | Mean precipitation intensity |
| `pmin` | Min precipitation | mm/h | Minimum precipitation |
| `pmax` | Max precipitation | mm/h | Maximum precipitation |
| `tcc_mean` | Total cloud cover | 0-8 | Cloud cover (0=clear, 8=overcast) |
| `lcc_mean` | Low cloud cover | 0-8 | Low-level cloud cover |
| `mcc_mean` | Medium cloud cover | 0-8 | Medium-level cloud cover |
| `hcc_mean` | High cloud cover | 0-8 | High-level cloud cover |
| `vis` | Visibility | km | Horizontal visibility |
| `gust` | Wind gust | m/s | Wind gust speed |
| `Wsymb2` | Weather symbol | 1-27 | Weather condition symbol |

## Precipitation Categories (pcat)

- `0`: No precipitation
- `1`: Snow
- `2`: Snow and rain
- `3`: Rain
- `4`: Drizzle
- `5`: Freezing rain
- `6`: Freezing drizzle

## Weather Symbols (Wsymb2)

1. Clear sky
2. Nearly clear sky
3. Variable cloudiness
4. Halfclear sky
5. Cloudy sky
6. Overcast
7. Fog
8. Light rain showers
9. Moderate rain showers
10. Heavy rain showers
11. Thunderstorm
12. Light sleet showers
13. Moderate sleet showers
14. Heavy sleet showers
15. Light snow showers
16. Moderate snow showers
17. Heavy snow showers
18. Light rain
19. Moderate rain
20. Heavy rain
21. Thunder
22. Light sleet
23. Moderate sleet
24. Heavy sleet
25. Light snowfall
26. Moderate snowfall
27. Heavy snowfall

## Wind Speed Interpretation

- **0-0.2 m/s**: Calm
- **0.3-1.5 m/s**: Light air
- **1.6-3.3 m/s**: Light breeze
- **3.4-5.4 m/s**: Gentle breeze
- **5.5-7.9 m/s**: Moderate breeze
- **8.0-10.7 m/s**: Fresh breeze
- **10.8-13.8 m/s**: Strong breeze
- **13.9-17.1 m/s**: Near gale
- **17.2-20.7 m/s**: Gale
- **20.8-24.4 m/s**: Strong gale
- **24.5-28.4 m/s**: Storm
- **28.5-32.6 m/s**: Violent storm
- **>32.6 m/s**: Hurricane

## Common Locations (Östergötland)

Pre-configured locations with coordinates:

| Location | Latitude | Longitude |
|----------|----------|-----------|
| Mjölby | 58.3253 | 15.1286 |
| Linköping | 58.4108 | 15.6214 |
| Norrköping | 58.5877 | 16.1924 |
| Motala | 58.5370 | 15.0370 |
| Vadstena | 58.4495 | 14.8894 |

## Data Update Frequency

- Forecasts are updated approximately 4 times per day
- Each forecast covers up to 10 days ahead
- Hourly granularity for the first 48 hours
- 3-hour granularity for days 3-10

## Error Handling

Common errors:

- **404**: Invalid coordinates or endpoint
- **503**: API temporarily unavailable
- **Timeout**: Network issues or slow response

Always implement timeout handling (recommended: 10 seconds).

## Rate Limiting

SMHI's open API has no official rate limits for reasonable use. However:

- Avoid making excessive requests
- Cache forecast data (valid for at least 1 hour)
- Use appropriate User-Agent headers

## Weather Warnings (Detailed)

### API Endpoint

**Get All Active Warnings:**
```
GET https://wpt-a.smhi.se/backend-warnings-page/warningAreas
```

Returns JSON array of all active warnings in Sweden.

### Warning Levels

The API uses three severity levels (color-coded):

| Level | Swedish | Icon | Meaning |
|-------|---------|------|---------|
| `YELLOW` | Gul | 🟡 | Yellow warning - Be aware |
| `ORANGE` | Orange | 🟠 | Orange warning - Dangerous conditions |
| `RED` | Röd | 🔴 | Red warning - Very dangerous conditions |
| `NONE` | - | ✅ | No active warnings |

### Warning Types

#### Weather Warnings (⛈️)

| Event Code | Swedish | Description |
|------------|---------|-------------|
| `WIND_SNOW` | Snöfall i kombination med vind | Snow and wind |
| `SNOW` | Snöfall | Snowfall |
| `GALE_LOW` | Hård vind | Near gale (14-17 m/s) |
| `ICE_ACCRETION` | Isbildning | Ice accretion at sea |
| `HIGH_TEMPERATURES` | Höga temperaturer | High temperatures |
| `RAIN` | Regn | Heavy rain |
| `THUNDER` | Åska | Thunderstorms |

#### Fire Warnings (🔥)

| Event Code | Swedish | Description |
|------------|---------|-------------|
| `GRASS_FIRE` | Gräsbrandrisk | Grass fire risk |
| `FOREST_FIRE` | Skogsbrandrisk | Forest fire risk |

#### Water Warnings (💧)

| Event Code | Swedish | Description |
|------------|---------|-------------|
| `WATER_SHORTAGE` | Vattenbrist | Water shortage risk |
| `HIGH_WATER` | Höga vattennivåer | High water levels |
| `FLOODING` | Översvämning | Flooding risk |

### Response Structure

```json
{
  "id": 9439,
  "published": "2026-01-25T09:41:01.993Z",
  "created": "2026-01-25T09:41:01.993Z",
  "approximateStart": "2026-01-26T09:00:00.342Z",
  "approximateEnd": "2026-01-27T08:00:00.963Z",
  "normalProbability": true,
  "pushNotice": true,
  "areaName": {
    "en": "Östergötland County",
    "sv": "Östergötlands län"
  },
  "warningLevel": {
    "sv": "Orange",
    "en": "Orange",
    "code": "ORANGE"
  },
  "eventDescription": {
    "sv": "Snöfall i kombination med vind",
    "en": "Snow and wind",
    "code": "WIND_SNOW"
  },
  "affectedAreas": [
    {
      "id": 5,
      "sv": "Östergötlands län",
      "en": "Östergötland County"
    }
  ],
  "descriptions": [
    {
      "title": {
        "sv": "Vad händer?",
        "en": "What happens?",
        "code": "HAPPENS"
      },
      "text": {
        "sv": "Snöfall 10-20 cm i kombination med hård vind...",
        "en": "Snowfall 10-20 cm combined with strong winds..."
      }
    },
    {
      "title": {
        "sv": "Vad ska jag tänka på?",
        "en": "What should I think about?",
        "code": "AFFECT"
      },
      "text": {
        "sv": "Undvik onödiga resor...",
        "en": "Avoid unnecessary travel..."
      }
    }
  ],
  "area": {
    "type": "Feature",
    "geometry": {
      "type": "Polygon",
      "coordinates": [...]
    }
  }
}
```

### Filtering by Region

**Important:** The API does not support server-side filtering. You must:

1. Fetch all warnings from `/warningAreas`
2. Filter client-side by checking `affectedAreas` array for your county

**Example filtering for Östergötland:**
```python
all_warnings = requests.get('https://wpt-a.smhi.se/backend-warnings-page/warningAreas').json()
ostergotland_warnings = [
    w for w in all_warnings 
    if any("Östergötland" in area.get("sv", "") for area in w.get("affectedAreas", []))
]
```

### Description Fields

Each warning contains multiple description sections:

- **`HAPPENS`** (Vad händer?) - What is happening
- **`AFFECT`** (Vad ska jag tänka på?) - What to be aware of / advice
- **`CONSEQUENCE`** - Possible consequences (not always present)

### Data Format

- **Format:** JSON only
- **Language:** Bilingual (Swedish and English)
- **Coordinates:** WGS84 (standard lat/lon)
- **Geometry:** GeoJSON format for warning area polygons
- **Timestamps:** ISO 8601 format with UTC timezone (ends with 'Z')

### Authentication & Usage

- **Authentication:** None required (public API)
- **CORS:** Enabled (`access-control-allow-origin: *`)
- **Caching:** Recommended - warnings update every few hours
- **Rate Limiting:** Not explicitly documented, use reasonable intervals

## Additional Resources

- Official SMHI API Documentation: https://opendata.smhi.se/apidocs/
- SMHI Open Data Portal: https://opendata.smhi.se/
- Official Warnings Page: https://www.smhi.se/vader/prognoser-och-varningar/varningar-och-meddelanden/varningar
