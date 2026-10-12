import re
import unicodedata
from typing import Any


INTENT_TERMS = {
    "crop_disease": {
        "en": ("disease", "yellow", "spots", "blight", "wilt", "rot", "fungus", "symptom", "leaf"),
        "hi": ("रोग", "पीला", "धब्बे", "झुलसा", "मुरझा", "सड़न", "पत्ती"),
        "te": ("తెగులు", "పసుపు", "మచ్చలు", "ఎండ", "కుళ్ళు", "ఆకు"),
    },
    "pest_control": {
        "en": ("pest", "insect", "worm", "aphid", "caterpillar", "borer", "bug"),
        "hi": ("कीट", "किड़ा", "इल्ली", "माहू"),
        "te": ("పురుగు", "కీటకం", "లద్దె", "కాయతొలుచు"),
    },
    "fertilizer": {
        "en": ("fertilizer", "fertiliser", "nutrient", "urea", "compost", "manure", "npk"),
        "hi": ("खाद", "उर्वरक", "यूरिया", "पोषक"),
        "te": ("ఎరువు", "యూరియా", "పోషక"),
    },
    "irrigation": {
        "en": ("water", "irrigation", "drip", "watering"),
        "hi": ("पानी", "सिंचाई", "ड्रिप"),
        "te": ("నీరు", "నీటిపారుదల", "బిందు"),
    },
    "weather": {
        "en": ("weather", "rain", "rainfall", "forecast", "temperature"),
        "hi": ("मौसम", "बारिश", "वर्षा", "तापमान"),
        "te": ("వాతావరణం", "వర్షం", "వాన", "ఉష్ణోగ్రత"),
    },
    "market_price": {
        "en": ("price", "market", "mandi", "rate", "sell", "selling"),
        "hi": ("भाव", "कीमत", "बाजार", "मंडी", "बेच"),
        "te": ("ధర", "మార్కెట్", "రేటు", "అమ్మకం"),
    },
    "government_scheme": {
        "en": ("scheme", "subsidy", "government", "benefit", "pm-kisan", "insurance"),
        "hi": ("योजना", "सब्सिडी", "सरकार", "किसान सम्मान", "बीमा"),
        "te": ("పథకం", "సబ్సిడీ", "ప్రభుత్వ", "బీమా"),
    },
    "sowing_harvest_timing": {
        "en": ("sow", "sowing", "planting", "harvest", "when to plant", "season", "calendar"),
        "hi": ("बुवाई", "बोना", "रोपाई", "कटाई", "कब बोएं", "मौसम"),
        "te": ("విత్తడం", "నాటడం", "కోత", "ఎప్పుడు వేయాలి", "సీజన్"),
    },
}

CROPS = {
    "rice": ("rice", "paddy", "धान", "चावल", "వరి", "బియ్యం"),
    "wheat": ("wheat", "गेहूं", "గోధుమ"),
    "cotton": ("cotton", "कपास", "పత్తి"),
    "tomato": ("tomato", "टमाटर", "టమాటా", "టమోటా"),
    "chilli": ("chilli", "chili", "मिर्च", "మిరప"),
    "maize": ("maize", "corn", "मक्का", "మొక్కజొన్న"),
    "groundnut": ("groundnut", "peanut", "मूंगफली", "వేరుశెనగ"),
    "sugarcane": ("sugarcane", "गन्ना", "చెరకు"),
    "soybean": ("soybean", "सोयाबीन", "సోయాబీన్"),
    "potato": ("potato", "आलू", "బంగాళాదుంప"),
}

STAGES = (
    "seedling", "vegetative", "flowering", "fruiting", "maturity", "harvest",
    "रोपाई", "फूल", "फल", "कटाई", "కోసు", "పూత", "కాయ", "పంట కోత",
)
SEASONS = (
    "kharif", "rabi", "zaid", "monsoon", "summer", "winter",
    "खरीफ", "रबी", "जायद", "बरसात", "गर्मी", "सर्दी",
    "ఖరీఫ్", "రబీ", "వేసవి", "వర్షాకాలం",
)
SYMPTOMS = (
    "yellow leaves", "yellowing", "yellow", "spots", "wilting", "curling", "holes", "rot",
    "पीली पत्तियां", "पीले पत्ते", "पीला", "पीली", "धब्बे", "मुरझाना", "सड़न",
    "పసుపు ఆకులు", "పసుపు", "మచ్చలు", "వాడిపోవడం", "కుళ్ళు",
)


def detect_language(text: str) -> str:
    """Detect Hindi/Telugu from script, otherwise use English."""
    for character in text:
        codepoint = ord(character)
        if 0x0C00 <= codepoint <= 0x0C7F:
            return "te"
        if 0x0900 <= codepoint <= 0x097F:
            return "hi"
    return "en"


def _find_alias(text: str, aliases: tuple[str, ...]) -> str | None:
    for alias in sorted(aliases, key=len, reverse=True):
        if alias.isascii() and re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", text):
            return alias
        if not alias.isascii() and alias in text:
            return alias
    return None


def process_query(query: str) -> dict[str, Any]:
    normalized = unicodedata.normalize("NFKC", query).strip()
    normalized = re.sub(r"\s+", " ", normalized)
    search_text = normalized.casefold()
    language = detect_language(normalized)

    intent_scores = {
        intent: sum(term in search_text for terms in translations.values() for term in terms)
        for intent, translations in INTENT_TERMS.items()
    }
    best_intent = max(intent_scores, key=intent_scores.get)
    intent = best_intent if intent_scores[best_intent] else "general"

    crop = None
    for crop_name, aliases in CROPS.items():
        if _find_alias(search_text, aliases):
            crop = crop_name
            break

    location_patterns = (
        r"(?:\bin\s+|\bnear\s+|\bat\s+)([A-Za-z][A-Za-z .'-]{1,40})",
        r"(?:जिला|जिले|गाँव|गांव|ग्राम|शहर)\s*[:\-]?\s*([\u0900-\u097F][\u0900-\u097F .'-]{1,40})",
        r"(?:జిల్లా|గ్రామం|ఊరు|నగరం)\s*[:\-]?\s*([\u0C00-\u0C7F][\u0C00-\u0C7F .'-]{1,40})",
    )
    location = None
    for pattern in location_patterns:
        location_match = re.search(pattern, normalized, flags=re.IGNORECASE)
        if location_match:
            location = location_match.group(1).strip(" .,'")
            break

    return {
        "intent": intent,
        "crop": crop,
        "growth_stage": _find_alias(search_text, STAGES),
        "symptoms": _find_alias(search_text, SYMPTOMS),
        "location": location,
        "season": _find_alias(search_text, SEASONS),
        "language": language,
        "normalized_query": normalized,
    }
