import logging
from langdetect import detect, LangDetectException
from llm import llm

logger = logging.getLogger(__name__)

# Full language names for logging and report readability
LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "ur": "Urdu",
}


def detect_and_translate(message: str) -> dict:
    """
    Detect the language of the complaint message.
    If it is not English, translate it using the LLM.

    Returns a dict with:
        original_language     — ISO 639-1 code (e.g. 'hi')
        original_language_name — human-readable name (e.g. 'Hindi')
        original_message       — untouched original text
        translated_message     — English version (same as original if already English)
        was_translated         — bool
    """

    try:
        lang_code = detect(message)
    except LangDetectException:
        # langdetect can fail on very short or symbol-only text — default to English
        logger.warning("Language detection failed, defaulting to English")
        lang_code = "en"

    lang_name = LANGUAGE_NAMES.get(lang_code, lang_code.upper())
    logger.info(f"Detected language: {lang_name} ({lang_code})")

    if lang_code == "en":
        return {
            "original_language": "en",
            "original_language_name": "English",
            "original_message": message,
            "translated_message": message,
            "was_translated": False,
        }

    # Translate to English using the LLM
    prompt = f"""Translate the following text to English.
Return ONLY the translated text, nothing else. No explanations, no labels.

Text:
{message}"""

    translated = llm.invoke(prompt).content.strip()
    logger.info(f"Translated complaint from {lang_name} to English")

    return {
        "original_language": lang_code,
        "original_language_name": lang_name,
        "original_message": message,
        "translated_message": translated,
        "was_translated": True,
    }
