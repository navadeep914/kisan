import json
import os
from typing import Any

import requests

from app.advisory import history_store
from app.advisory.knowledge_base import AgricultureKnowledgeBase
from app.advisory.query_processing import process_query


class AdvisoryService:
    def __init__(self) -> None:
        self.knowledge_base = AgricultureKnowledgeBase()

    def respond(self, farmer_id: str, query: str, input_type: str) -> dict[str, Any]:
        parsed = process_query(query)
        profile = history_store.get_profile(farmer_id)
        if not parsed["location"]:
            parsed["location"] = profile["location"] or None
        sources = self.knowledge_base.search(query, top_k=int(os.getenv("ADVISORY_TOP_K", "3")))
        context = history_store.get_recent_context(farmer_id, limit=5)
        advisory = self._generate_advisory(query, parsed, sources, profile, context)
        record = history_store.add_interaction({
            "farmer_id": farmer_id,
            "original_input": query,
            "input_type": input_type,
            "intent": parsed["intent"],
            "retrieved_sources": [
                {"title": source["title"], "category": source["category"], "score": source["score"]}
                for source in sources
            ],
            "advisory": advisory,
            "language": parsed["language"],
        })
        return {
            "farmer_id": farmer_id,
            "original_input": query,
            "input_type": input_type,
            "parsed_query": parsed,
            "advisory": advisory,
            "language": parsed["language"],
            "retrieved_sources": record["retrieved_sources"],
            "history_id": record["id"],
        }

    def _generate_advisory(
        self,
        query: str,
        parsed: dict[str, Any],
        sources: list[dict[str, Any]],
        profile: dict[str, str],
        history: list[dict[str, str]],
    ) -> str:
        if not sources:
            return self._insufficient_message(parsed["language"])

        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if api_key:
            try:
                return self._call_gemini(query, parsed, sources, profile, history, api_key)
            except Exception as error:
                print(f"[Advisory] Gemini call failed ({error}), using local grounded template.")
                return self._grounded_template(parsed, sources, profile)

        return self._grounded_template(parsed, sources, profile)

    @staticmethod
    def _call_gemini(
        query: str,
        parsed: dict[str, Any],
        sources: list[dict[str, Any]],
        profile: dict[str, str],
        history: list[dict[str, str]],
        api_key: str,
    ) -> str:
        preferred_model = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite").strip()
        candidate_models = [preferred_model]
        for fallback in ["gemini-3.1-flash-lite", "gemini-3-flash-preview"]:
            if fallback not in candidate_models:
                candidate_models.append(fallback)

        prompt = {
            "role": "You are a careful agricultural extension assistant. Answer in the farmer's detected language. "
            "Use ONLY the supplied retrieved knowledge; never add outside facts or make up rates, diagnoses, or weather. "
            "Give short numbered, actionable steps. Include the supplied chemical safety warning when relevant. "
            "If sources do not answer the question, say information is insufficient and advise contacting the local "
            "agriculture officer. Farmer profile and recent interactions may personalize wording but are not factual sources.",
            "detected_language": parsed["language"],
            "structured_query": parsed,
            "farmer_profile": profile,
            "recent_interactions": history,
            "retrieved_knowledge_only": sources,
            "farmer_question": query,
        }

        last_error = None
        for model in candidate_models:
            try:
                response = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                    params={"key": api_key},
                    json={
                        "contents": [{"parts": [{"text": json.dumps(prompt, ensure_ascii=False)}]}],
                        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 500},
                    },
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                if text:
                    return text
            except Exception as error:
                last_error = error
                continue

        raise ValueError(f"All Gemini candidate models failed: {last_error}")

    @classmethod
    def _grounded_template(
        cls,
        parsed: dict[str, Any],
        sources: list[dict[str, Any]],
        profile: dict[str, str],
    ) -> str:
        language = parsed["language"]
        localized_titles = {"en": "Based on the farm guide", "hi": "कृषि मार्गदर्शिका के अनुसार", "te": "వ్యవసాయ మార్గదర్శిని ప్రకారం"}
        heading = localized_titles.get(language, localized_titles["en"])
        location = parsed.get("location") or profile.get("location")
        if location:
            farm_labels = {
                "en": f"For your farm in {location}",
                "hi": f"{location} में आपके खेत के लिए",
                "te": f"{location}లో మీ పొలం కోసం",
            }
            heading = farm_labels.get(language, farm_labels["en"])
        actions = []
        warning = ""
        for source in sources[:2]:
            content = source["content"]
            actions.extend(content["advice"].get(language, content["advice"]["en"]))
            warning = warning or content["warning"].get(language, content["warning"]["en"])
        numbered = "\n".join(f"{index}. {action}" for index, action in enumerate(dict.fromkeys(actions), start=1))
        if warning:
            return f"{heading}:\n{numbered}\n\n{cls._safety_label(language)}: {warning}"
        return f"{heading}:\n{numbered}"

    @staticmethod
    def _safety_label(language: str) -> str:
        return {"en": "Safety", "hi": "सावधानी", "te": "జాగ్రత్త"}.get(language, "Safety")

    @staticmethod
    def _insufficient_message(language: str) -> str:
        return {
            "en": "I could not find enough information in the agriculture knowledge base to answer safely. Please contact your local agriculture officer for advice.",
            "hi": "कृषि ज्ञान आधार में सुरक्षित उत्तर देने के लिए पर्याप्त जानकारी नहीं मिली। कृपया सलाह के लिए अपने स्थानीय कृषि अधिकारी से संपर्क करें।",
            "te": "వ్యవసాయ జ్ఞాన భాండాగారంలో సురక్షితంగా సమాధానం ఇవ్వడానికి తగిన సమాచారం లేదు. దయచేసి మీ స్థానిక వ్యవసాయ అధికారిని సంప్రదించండి.",
        }.get(language, "I could not find enough information in the agriculture knowledge base. Please contact your local agriculture officer.")
