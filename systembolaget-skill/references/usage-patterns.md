# Usage Patterns

Use this reference when the request is a little fuzzy and you need a practical way to turn the user's wording into direct API calls or a best-effort recommendation.

## Preferred command patterns

Use the bundled helper first.

```bash
python scripts/systembolaget_api.py search-products --query "ipa" --country "Sverige" --max-price 40 --limit 10
python scripts/systembolaget_api.py get-product 12345
python scripts/systembolaget_api.py search-stores --city "Stockholm"
```

Treat the script output as the grounded source of truth when it succeeds.

## Anti-shortcut rule

If the first API result is messy, do not jump to web search. Improve the API query first.

Typical fixes:
- add or tighten `--category`
- add `--country`
- add `--max-price` or `--min-price`
- add alcohol bounds
- replace a vague query with a style-specific one
- fetch a few finalists with `get-product` instead of running a broader search

Use the website only when the API helper genuinely fails or the API does not expose the needed information.

## Common request shapes

### Pairing request

Typical prompts:
- "what wine should I get for seafood"
- "recommend a red for steak under 200 kr"
- "I need something for spicy food"

Approach:
- identify likely category first
- extract budget and alcohol preferences if present
- look up enough live candidates with the helper script to have options
- rank finalists using visible taste fields, description, and serving guidance
- be explicit that the pairing is a best-fit recommendation based on available catalog data

### Budget shortlist

Typical prompts:
- "best beer under 35 kr"
- "good whisky around 500"
- "party bottles between 100 and 150"

Approach:
- prioritize price bounds and category
- use structured notes while comparing so you can sort, count, and compare precisely
- avoid naming a single winner too early if the search returns a wide range of styles

### Value comparison

Typical prompts:
- "which one is the best value"
- "compare these three IPAs"
- "what gives me the most for the money"

Approach:
- calculate price per liter when volume is present
- compare alcohol, taste profile, and category fit separately from pure value
- explain whether your winner is best value, best taste fit, or best overall compromise

### Tasting lineup

Typical prompts:
- "build a whisky tasting"
- "give me 5 wines from different regions"
- "I want a beer flight with variety"

Approach:
- search for diversity on purpose, not just the top few cheapest or strongest products
- vary country, style, price point, or taste profile depending on the request
- explain what makes each slot different in the lineup

### Store lookup

Typical prompts:
- "which stores are in Linkoping"
- "closest Systembolaget to central station"
- "show stores in Stockholm with hours"

Approach:
- use city names for city-level requests
- use addresses, areas, or landmarks when given
- if "closest" cannot be established confidently, label the answer as best-effort rather than exact

## Heuristic mappings

These are reasoning aids, not guaranteed site categories.

- "beer", "lager", "IPA", "stout" -> likely search with `category: "Ol"` or a beer-oriented query
- "wine", "red wine", "white wine", "sparkling" -> likely search with `category: "Vin"` or a wine-style query
- "whisky", "whiskey", "vodka", "gin", "rum" -> likely spirit-oriented search, often better with `query` plus price filters if category naming is uncertain
- "sweet" -> prioritize sweetness-related fields if available
- "bitter" -> prioritize bitterness fields if available
- "light", "crisp", "not too strong" -> use lower or moderate body/alcohol when the data supports it

## Output priorities

When the user wants help deciding, optimize for decision quality rather than raw completeness.

Prefer:
- 3 to 5 clearly differentiated recommendations
- one-line rationale per option
- a short note on tradeoffs

Avoid:
- dumping long unranked result lists
- overstating certainty about pairings or store proximity
- inventing stock, shelf availability, or unavailable metadata
