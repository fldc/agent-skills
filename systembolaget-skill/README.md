# Systembolaget Skill

An agent skill for helping users choose, compare, and recommend drinks from Systembolaget and locate stores.

## Features

- Search products by category, country, price, alcohol content, and more
- Lookup products by artikelnummer
- Search for Systembolaget stores by city
- Food pairing and tasting recommendations
- Budget and gift suggestions

## Usage

The skill uses a Python helper to call Systembolaget's public API directly:

```bash
# Search products
python scripts/systembolaget_api.py search-products --query "ipa" --max-price 40 --limit 10

# Sort by price (cheapest first)
python scripts/systembolaget_api.py search-products --category "Öl" --sort-by price --limit 10

# Sort by APK (best alcohol per krona)
python scripts/systembolaget_api.py search-products --category "Öl" --sort-by apk --limit 10

# Lookup by artikelnummer
python scripts/systembolaget_api.py get-product 12345

# Search stores
python scripts/systembolaget_api.py search-stores --city "Uppsala"
```

If you need to override the detected public API key, place `SYSTEMBOLAGET_API_KEY=...` in `~/.config/ehh-skills/config.env`.

### APK (Alcohol Per Krona)

APK is calculated as: `(alcohol% × volume_ml) / price`

This helps find the best value - higher APK = more alcohol per krona spent.

## License

MIT
