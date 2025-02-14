from deep_translator import GoogleTranslator

def translate_to_english(text: str) -> str:
    try:
        translated = GoogleTranslator(source="auto", target="en").translate(text)
        return translated
    except Exception as e:
        print(f"Translation Error: {e}")
        return text  # Fallback to original text