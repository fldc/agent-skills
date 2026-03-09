# Luncha I Mjärdevi API Reference

## Base URL

```
https://lunchaimjardevi.com/api/v4/
```

## Endpoints

### 1. Get Restaurants

**Endpoint:** `getRestaurants`  
**Method:** GET/POST  
**Description:** Hämtar lista över alla restauranger i Mjärdevi

**Query Parameters:**

- `key` (string, required): API-nyckel
- `showOutsideMjardevi` (boolean, optional): Inkludera restauranger utanför Mjärdevi

**Response Example:**

```json
{
  "error": "none",
  "restaurants": [
    {
      "id": "1",
      "name": "Brödernas Kök",
      "shortName": "brodernas",
      "isFoodtruck": false,
      "website": "https://www.brodernaskok.se/meny",
      "lastUpdate": "1657572107",
      "coordLat": "58.39423",
      "coordLong": "15.55948",
      "static": true,
      "note": ""
    }
  ]
}
```

### 2. Get Restaurant Info

**Endpoint:** `getRestaurantInfo`  
**Method:** GET/POST  
**Description:** Hämtar detaljerad information om en specifik restaurang

**Query Parameters:**

- `key` (string, required): API-nyckel
- `id` (integer, required\*): Restaurang-ID
- `shortName` (string, required\*): Restaurangens kortnamn

\*Du måste använda antingen `id` eller `shortName`

### 3. Get Menu

**Endpoint:** `getMenu`  
**Method:** GET/POST  
**Description:** Hämtar dagens meny för en specifik restaurang

**Query Parameters:**

- `key` (string, required): API-nyckel
- `id` (integer, required\*): Restaurang-ID
- `shortName` (string, required\*): Restaurangens kortnamn

\*Du måste använda antingen `id` eller `shortName`

**Response Example:**

```json
{
  "error": "none",
  "name": "Pegs & Tails",
  "menuItems": [
    {
      "title": "Fransk kycklinggryta",
      "description": "Kycklinggryta serveras med potatispuré",
      "static": false
    }
  ]
}
```

## Error Codes

- `none`: Inga fel
- `invalidId`: Ingen restaurang med angivet ID finns
- `needsNewParser`: Restaurangens webbplats har uppdaterats, parser behöver fixas
- `noMenuForTodayYet`: Ingen meny tillgänglig än (kan bero på flera orsaker):
  - Restaurangen är stängd idag
  - Restaurangens webbplats inte uppdaterad än
  - Parser behöver uppdateras

## API Key

En API-nyckel krävs för att använda API:et. Registrera dig på:
https://lunchaimjardevi.com/api/
