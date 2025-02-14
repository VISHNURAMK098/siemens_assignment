import requests
import os
import cachetools
from tenacity import retry, stop_after_attempt, wait_fixed

from dotenv import load_dotenv

load_dotenv()

# Time-based cache (expires every 600 seconds / 10 minutes)
crypto_cache = cachetools.TTLCache(maxsize=100, ttl=600)

class CryptoPriceFetcher:
    @staticmethod
    def get_cached_crypto_price(crypto_ids: list) -> str:
        crypto_ids_tuple = tuple(sorted(crypto_id.lower() for crypto_id in crypto_ids))  # Ensure lowercase sorting

        # Check cache first
        if crypto_ids_tuple in crypto_cache:
            return crypto_cache[crypto_ids_tuple]

        # Fetch fresh prices and update cache
        crypto_data = CryptoPriceFetcher.fetch_prices(list(crypto_ids))
        prices = []
        for crypto_id in crypto_ids:
            crypto_id_lower = crypto_id.lower()  # Convert to lowercase for lookup
            price = crypto_data.get(crypto_id_lower, {}).get("usd", "0.00")  # Use lowercase key
            prices.append(f"The price of {crypto_id} is ${float(price):.2f}")

        result = " and ".join(prices)
        crypto_cache[crypto_ids_tuple] = result  # Cache result

        return result

    # Rate limiter: Retry 3 times with 2 seconds delay if request fails
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def fetch_prices(crypto_list: list) -> dict:
        crypto_ids = [crypto.strip().lower() for crypto in crypto_list]  # Ensure lowercase
        crypto_query = ",".join(crypto_ids)  # Convert list to comma-separated string

        # API request parameters
        params = {"ids": crypto_query, "vs_currencies": "usd"}

        try:
            response = requests.get(os.getenv("CRYPTO_API_URL"), params=params)
            response.raise_for_status()
            return response.json()  # Return JSON data as dictionary

        except requests.exceptions.RequestException as error:
            return {}  # Return empty dictionary in case of error