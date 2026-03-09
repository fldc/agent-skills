---
name: mjardevi-lunch
description: Hämta dagens lunchmenyer från restauranger i Mjärdevi via Luncha I Mjärdevi API. Använd när användaren frågar efter dagens lunch, lunchmeny eller vad som serveras idag i Mjärdevi.
---

# Mjärdevi Lunch

Hämtar och visar dagens lunchmeny från alla restauranger i Mjärdevi genom Luncha I Mjärdevi API.

## Quick Start

### 1. Konfigurera API-nyckel

Skapa en `.api_key` fil i skill-rotkatalogen med din API-nyckel:

```bash
echo "din_api_nyckel_här" > .api_key
```

Alternativt kopiera exempel-filen:
```bash
cp .api_key.example .api_key
# Redigera sedan .api_key med din faktiska nyckel
```

**Skaffa API-nyckel:**
Registrera en gratis API-nyckel på: https://lunchaimjardevi.com/api/

### 2. Kör scriptet

```bash
python scripts/get_lunch.py [api_key] [format]
```

**Parametrar:**
- `api_key`: API-nyckel. Om den inte anges maste den finnas i `.api_key` filen.
- `format`: "text" (standard) eller "json"

**Exempel:**
```bash
# Använd API-nyckel från .api_key fil
python scripts/get_lunch.py

# Ange API-nyckel direkt
python scripts/get_lunch.py ee57b6b96d25120dd4e921a8e7c246f1

# Få JSON-output
python scripts/get_lunch.py ee57b6b96d25120dd4e921a8e7c246f1 json
```

## Workflow

1. **Kör scriptet** - Använd `scripts/get_lunch.py` för att hämta dagens menyer
2. **Presentera resultatet** - Scriptet formaterar automatiskt outputen på ett lättläst sätt
3. **Hantera fel** - Scriptet hanterar vanliga fel som:
   - Restaurang stängd
   - Meny ej upplagd än
   - Nätverksproblem
   - Saknad API-nyckel

## Output Format

Scriptet genererar en formaterad lista med:
- Restaurangnamn
- Dagens lunchrätter med beskrivningar
- Eventuella noteringar (t.ex. semesterstängt)
- Felmeddelanden om meny inte är tillgänglig

**Exempel på output:**
```
# Dagens lunch i Mjärdevi - 2026-02-16

## Brödernas Kök

**Fransk kycklinggryta**
  Kycklinggryta serveras med potatispuré

**Laxpudding**
  Laxpudding serveras med skirat smör, dillkräm & citron
```

## API Details

För detaljerad API-dokumentation, se `references/api.md`. API:et tillhandahålls av Luncha I Mjärdevi och uppdateras automatiskt varje timme mellan 00-13 på vardagar.

**Viktiga punkter:**
- Menyer kan saknas om restaurangen är stängd eller inte uppdaterat sin webbplats än
- Vissa restauranger har statiska menyer (ändras inte automatiskt)
- API:et inkluderar både vanliga restauranger och foodtrucks
