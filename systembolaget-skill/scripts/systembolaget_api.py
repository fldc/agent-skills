#!/usr/bin/env python3
"""Direct Systembolaget API helper for the skill.

Extracts the public API key from Systembolaget's site,
then calling the same public endpoints used by the website.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_BASE = "https://api-extern.systembolaget.se/sb-api-ecommerce/v1"
WEBSITE = "https://www.systembolaget.se"
TIMEOUT = 30
CACHE_TTL_SECONDS = 3600


class APIError(Exception):
    pass


def cache_path() -> Path:
    base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return base / "systembolaget-skill" / "api-key.json"


def read_cache() -> str | None:
    path = cache_path()
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    api_key = payload.get("api_key")
    timestamp = payload.get("timestamp")
    if not api_key or not timestamp:
        return None
    if time.time() - float(timestamp) >= CACHE_TTL_SECONDS:
        return None
    return str(api_key)


def write_cache(api_key: str) -> None:
    path = cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"api_key": api_key, "timestamp": time.time()}))


def fetch_text(url: str, headers: dict[str, str] | None = None) -> str:
    request = Request(url, headers=headers or {})
    try:
        with urlopen(request, timeout=TIMEOUT) as response:
            return response.read().decode("utf-8")
    except HTTPError as exc:
        raise APIError(f"HTTP {exc.code} for {url}") from exc
    except URLError as exc:
        raise APIError(f"Network error for {url}: {exc.reason}") from exc


def fetch_json(url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
    return json.loads(fetch_text(url, headers=headers))


def extract_api_key() -> str:
    env_key = os.environ.get("SYSTEMBOLAGET_API_KEY")
    if env_key:
        return env_key

    cached = read_cache()
    if cached:
        return cached

    homepage = fetch_text(WEBSITE)
    bundle_match = re.search(r'<script src="([^"]+_app-[^"]+\.js)"', homepage)
    if not bundle_match:
        raise APIError("Could not find Systembolaget app bundle")

    bundle_path = bundle_match.group(1)
    bundle_url = (
        bundle_path if bundle_path.startswith("http") else f"{WEBSITE}{bundle_path}"
    )
    bundle = fetch_text(bundle_url)

    key_match = re.search(r'NEXT_PUBLIC_API_KEY_APIM:"([^"]+)"', bundle)
    if not key_match:
        raise APIError("Could not extract Systembolaget API key")

    api_key = key_match.group(1)
    write_cache(api_key)
    return api_key


def api_get(
    endpoint: str, params: dict[str, Any] | None = None, *, origin: bool = False
) -> dict[str, Any]:
    api_key = extract_api_key()
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    if origin:
        headers["Origin"] = WEBSITE
    query = f"?{urlencode(params)}" if params else ""
    url = f"{API_BASE}{endpoint}{query}"
    try:
        return fetch_json(url, headers=headers)
    except APIError as exc:
        if "HTTP 403" in str(exc):
            try:
                cache_path().unlink(missing_ok=True)
            except OSError:
                pass
            headers["Ocp-Apim-Subscription-Key"] = extract_api_key()
            return fetch_json(url, headers=headers)
        raise


def search_products(args: argparse.Namespace) -> dict[str, Any]:
    params: dict[str, Any] = {
        "page": args.offset // args.limit,
        "pageSize": args.limit,
    }
    if args.query:
        params["searchQuery"] = args.query
    if args.category:
        params["category"] = args.category
    if args.country:
        params["country"] = args.country
    if args.min_price is not None:
        params["minPrice"] = args.min_price
    if args.max_price is not None:
        params["maxPrice"] = args.max_price
    if args.min_alcohol is not None:
        params["minAlcohol"] = args.min_alcohol
    if args.max_alcohol is not None:
        params["maxAlcohol"] = args.max_alcohol

    # Fetch products (with pagination if limit > pageSize)
    all_products = []
    page_size = min(args.limit, 100)  # API max is usually 100 per page
    total_needed = args.limit
    current_offset = args.offset

    while len(all_products) < total_needed:
        params["page"] = current_offset // page_size
        params["pageSize"] = min(page_size, total_needed - len(all_products))

        result = api_get("/productsearch/search", params=params)
        products = result.get("products", [])

        if not products:
            break

        all_products.extend(products)
        current_offset += len(products)

        # Stop if we've fetched all available results
        if len(products) < params["pageSize"]:
            break

    # Calculate APK for each product
    for product in all_products:
        product["apk"] = calculate_apk(product)

    # Sort if requested
    if args.sort_by:
        reverse = args.sort_order == "desc"
        if args.sort_by == "price":
            all_products.sort(key=lambda p: p.get("price", 0), reverse=reverse)
        elif args.sort_by == "apk":
            all_products.sort(key=lambda p: p.get("apk", 0), reverse=reverse)

    return {"products": all_products[: args.limit], "total": len(all_products)}


def get_product(args: argparse.Namespace) -> dict[str, Any]:
    return api_get(f"/product/{args.product_number}")


def calculate_apk(product: dict[str, Any]) -> float:
    """Calculate APK (Alcohol Per Krona).

    Formula: (alcohol_percentage * volume_ml) / price

    Returns 0 if data is missing.
    """
    try:
        alcohol = product.get("alcoholPercentage", 0)
        price = product.get("price", 0)
        volume = product.get("volume", 0)

        # Volume might be in different formats, try to parse it
        if isinstance(volume, str):
            # Extract number from strings like "500 ml" or "75 cl"
            volume_match = re.search(r"(\d+(?:\.\d+)?)", volume)
            if volume_match:
                volume = float(volume_match.group(1))
            else:
                volume = 0

        if alcohol and price and volume:
            return round((alcohol * volume) / price, 2)
        return 0.0
    except (TypeError, ValueError):
        return 0.0


def search_stores(args: argparse.Namespace) -> dict[str, Any]:
    terms = [value for value in [args.query, args.city] if value]
    params = {"includePredictions": "true"}
    if terms:
        params["q"] = " ".join(terms)
    return api_get("/sitesearch/site", params=params, origin=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Systembolaget direct API helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    products = subparsers.add_parser("search-products")
    products.add_argument("--query")
    products.add_argument("--category")
    products.add_argument("--country")
    products.add_argument("--min-price", type=float)
    products.add_argument("--max-price", type=float)
    products.add_argument("--min-alcohol", type=float)
    products.add_argument("--max-alcohol", type=float)
    products.add_argument("--limit", type=int, default=20)
    products.add_argument("--offset", type=int, default=0)
    products.add_argument(
        "--sort-by",
        choices=["price", "apk"],
        help="Sort results by price or APK (alcohol per krona)",
    )
    products.add_argument(
        "--sort-order",
        choices=["asc", "desc"],
        default="asc",
        help="Sort order: asc (low to high) or desc (high to low). Default: asc",
    )
    products.set_defaults(handler=search_products)

    product = subparsers.add_parser("get-product")
    product.add_argument("product_number")
    product.set_defaults(handler=get_product)

    stores = subparsers.add_parser("search-stores")
    stores.add_argument("--query")
    stores.add_argument("--city")
    stores.set_defaults(handler=search_stores)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = args.handler(args)
    except APIError as exc:
        print(json.dumps({"error": str(exc)}))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
