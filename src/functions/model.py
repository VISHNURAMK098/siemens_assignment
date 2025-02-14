from typing import List
import requests
import os
from diskcache import Cache

from functions.entity_extraction import CryptoNameExtractor
from functions.fetch_crypto_price import CryptoPriceFetcher
from functions.template import PromptTemplate

from dotenv import load_dotenv

load_dotenv()

TOGETHER_AI_URL = os.getenv("TOGETHER_AI_URL")

# Cache for conversation history
cache = Cache("./cache")

class ModelResponse:
    def model(user_id: str, message: str) -> str:
        # Step1: Extract crypto names from the message
        detected_cryptos = CryptoNameExtractor.extract_names_from_message(message)

        # Step2: # Fetch prices and construct the information string
        crypto_info = CryptoPriceFetcher.get_cached_crypto_price(tuple(detected_cryptos)) if detected_cryptos else ""

        # Step 3: Modify prompt with price details
        modified_prompt = f"INFORMATION FROM COINGECKO API: {crypto_info}, USER QUESTION: {message}"

        headers = {
            "Authorization": f"Bearer {os.getenv("TOGETHER_AI_API_KEY")}",
            "Content-Type": "application/json"
        }

        with cache.transact():  # Ensure atomic update
            user_conversation_history = cache.get(user_id, [])

            # Trim the conversation history to a max size if needed
            max_history_size = 10
            if len(user_conversation_history) > max_history_size:
                user_conversation_history = user_conversation_history[-max_history_size:]

            user_conversation_history.append({"role": "user", "content": modified_prompt})
            cache[user_id] = user_conversation_history

            formatted_prompt = PromptTemplate.prompt_with_context(user_id, message, user_conversation_history)

        data = {
            "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            "messages":formatted_prompt,
            "temperature": 0.0,
            "max_tokens": 500
        }

        try:
            response = requests.post(os.getenv("TOGETHER_AI_URL"), json=data, headers=headers)
            response.raise_for_status()
            result = response.json()

            if "choices" in result and result["choices"]:
                ai_reply = result["choices"][0].get("text", "No response received.")
                with cache.transact():
                    user_conversation_history.append({"role": "assistant", "content": ai_reply})
                    cache[user_id] = user_conversation_history
                return f"{ai_reply} {crypto_info}" if crypto_info else ai_reply
            else:
                return "Unexpected response format"
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
