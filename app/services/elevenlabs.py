import requests
from app.config import Config

BASE_URL = "https://api.elevenlabs.io/v1"

# Voices grouped by language
# Each group has 2 female + 2 male
VOICE_SETS = {
    "english": {
        "sarah": {
            "id":          "EXAVITQu4vr4xnSDxMaL",
            "name":        "Sarah",
            "gender":      "female",
            "description": "Warm and gentle. Soft tone, very calming.",
        },
        "aria": {
            "id":          "9BWtsMINqrJLrRacOk9x",
            "name":        "Aria",
            "gender":      "female",
            "description": "Expressive and empathetic. Natural and present.",
        },
        "liam": {
            "id":          "TX3LPaxmHKxFdv7VOQHJ",
            "name":        "Liam",
            "gender":      "male",
            "description": "Calm and grounded. Clear and reassuring.",
        },
        "charlie": {
            "id":          "IKne3meq5aSn9XLyUdCD",
            "name":        "Charlie",
            "gender":      "male",
            "description": "Friendly and steady. Warm without being heavy.",
        },
    },
    "hindi": {
        "aradhya": {
            "id":          "Xb7hH8MSUJpSbSDYk0k2",
            "name":        "Aradhya",
            "gender":      "female",
            "description": "Soft and soothing. Natural Hindi warmth.",
        },
        "neerja": {
            "id":          "XrExE9yKIg1WjnnlVkGX",
            "name":        "Neerja",
            "gender":      "female",
            "description": "Gentle and expressive. Calm desi tone.",
        },
        "rohan": {
            "id":          "bIHbv24MWmeRgasZH58o",
            "name":        "Rohan",
            "gender":      "male",
            "description": "Steady and reassuring. Grounded presence.",
        },
        "arjun": {
            "id":          "onwK4e9ZLuTAKqWW03F9",
            "name":        "Arjun",
            "gender":      "male",
            "description": "Warm and clear. Friendly, not heavy.",
        },
    },
    "tamil": {
        "kavya": {
            "id":          "EXAVITQu4vr4xnSDxMaL",  # closest warm female
            "name":        "Kavya",
            "gender":      "female",
            "description": "Gentle and warm. Clear Tamil delivery.",
        },
        "meera": {
            "id":          "9BWtsMINqrJLrRacOk9x",
            "name":        "Meera",
            "gender":      "female",
            "description": "Expressive and calm. Natural presence.",
        },
        "karthik": {
            "id":          "TX3LPaxmHKxFdv7VOQHJ",
            "name":        "Karthik",
            "gender":      "male",
            "description": "Steady and grounded. Reassuring tone.",
        },
        "vijay": {
            "id":          "IKne3meq5aSn9XLyUdCD",
            "name":        "Vijay",
            "gender":      "male",
            "description": "Friendly and warm. Calm delivery.",
        },
    },
}

# Languages that map to a specific voice set
LANGUAGE_VOICE_MAP = {
    "English":  "english",
    "Tamil":    "tamil",
    "Hindi":    "hindi",
    # All others fall back to hindi as closest
    "Marathi":   "hindi",
    "Gujarati":  "hindi",
    "Punjabi":   "hindi",
    "Bengali":   "hindi",
    "Kannada":   "hindi",
    "Telugu":    "hindi",
}

# Flat VOICES dict kept for backward compatibility
VOICES = {**VOICE_SETS["english"], **VOICE_SETS["hindi"], **VOICE_SETS["tamil"]}

DEFAULT_VOICE_ID = VOICE_SETS["english"]["sarah"]["id"]

LANGUAGE_CODES = {
    "English":  "en",
    "Hindi":    "hi",
    "Tamil":    "ta",
    "Telugu":   "te",
    "Marathi":  "hi",
    "Kannada":  "hi",
    "Bengali":  "hi",
    "Gujarati": "hi",
    "Punjabi":  "hi",
}


def get_voices_for_language(language: str) -> dict:
    """Return the 4-voice set appropriate for the given language."""
    set_key = LANGUAGE_VOICE_MAP.get(language, "hindi")
    return VOICE_SETS[set_key]


def synthesize_speech(
    text:     str,
    language: str = "English",
    voice_id: str = None,
) -> bytes:
    if not voice_id:
        voice_id = DEFAULT_VOICE_ID

    lang_code = LANGUAGE_CODES.get(language, "en")

    response = requests.post(
        f"{BASE_URL}/text-to-speech/{voice_id}",
        headers={
            "xi-api-key":   Config.ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "text":          text,
            "model_id":      "eleven_multilingual_v2",
            "language_code": lang_code,
            "voice_settings": {
                "stability":         0.65,
                "similarity_boost":  0.75,
                "style":             0.10,
                "use_speaker_boost": True,
            },
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.content


def generate_voice_preview(voice_id: str, language: str = "English") -> bytes:
    """Short preview clip in the correct language."""
    previews = {
        "English": "Hi, I'm here with you. Whatever you're feeling right now is completely valid. Take a breath — you're not alone.",
        "Hindi":   "मैं यहाँ हूँ आपके साथ। आप जो भी महसूस कर रहे हैं वह बिल्कुल सही है। एक गहरी सांस लें — आप अकेले नहीं हैं।",
        "Tamil":   "நான் உங்களுடன் இருக்கிறேன். நீங்கள் இப்போது உணர்வது முற்றிலும் சரியானது. மூச்சு எடுங்கள் — நீங்கள் தனியாக இல்லை.",
    }
    # For other languages use Hindi preview as closest
    text = previews.get(language, previews["Hindi"])
    return synthesize_speech(text, language, voice_id)