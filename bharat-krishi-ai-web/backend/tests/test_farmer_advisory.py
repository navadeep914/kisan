import os
import tempfile
import unittest
from pathlib import Path

from app.advisory import history_store
from app.advisory.query_processing import process_query


class QueryProcessingTests(unittest.TestCase):
    def test_detects_english_disease_and_entities(self):
        parsed = process_query("My rice has yellow leaves and leaf blast in Karimnagar")
        self.assertEqual(parsed["intent"], "crop_disease")
        self.assertEqual(parsed["crop"], "rice")
        self.assertEqual(parsed["language"], "en")
        self.assertEqual(parsed["symptoms"], "yellow leaves")
        self.assertEqual(parsed["location"], "Karimnagar")

    def test_detects_hindi_scheme_query(self):
        parsed = process_query("पीएम किसान योजना की पात्रता कैसे जांचूं?")
        self.assertEqual(parsed["intent"], "government_scheme")
        self.assertEqual(parsed["language"], "hi")

    def test_does_not_misread_hindi_postposition_as_location(self):
        parsed = process_query("धान में पत्तियों पर रोग के धब्बे दिख रहे हैं")
        self.assertIsNone(parsed["location"])

    def test_detects_telugu_crop_and_disease(self):
        parsed = process_query("వరిలో పసుపు ఆకులు మరియు తెగులు")
        self.assertEqual(parsed["intent"], "crop_disease")
        self.assertEqual(parsed["crop"], "rice")
        self.assertEqual(parsed["language"], "te")
        self.assertEqual(parsed["symptoms"], "పసుపు ఆకులు")

    def test_detects_market_question_and_location(self):
        parsed = process_query("What is today's tomato mandi price in Guntur?")
        self.assertEqual(parsed["intent"], "market_price")
        self.assertEqual(parsed["crop"], "tomato")
        self.assertEqual(parsed["location"], "Guntur")

    def test_detects_pest_fertilizer_irrigation_and_weather_intents(self):
        self.assertEqual(process_query("Cotton aphids are multiplying quickly")["intent"], "pest_control")
        self.assertEqual(process_query("Should I use urea for wheat?")["intent"], "fertilizer")
        self.assertEqual(process_query("How should I water tomato?")["intent"], "irrigation")
        self.assertEqual(process_query("Will rain affect my rice field?")["intent"], "weather")

    def test_normalizes_whitespace_and_detects_season(self):
        parsed = process_query("  When   should I sow wheat in rabi? ")
        self.assertEqual(parsed["normalized_query"], "When should I sow wheat in rabi?")
        self.assertEqual(parsed["intent"], "sowing_harvest_timing")
        self.assertEqual(parsed["season"], "rabi")


class HistoryStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.previous_path = os.environ.get("ADVISORY_DATABASE_PATH")
        os.environ["ADVISORY_DATABASE_PATH"] = str(Path(self.temp_dir.name) / "history.sqlite3")
        history_store.initialize_database()

    def tearDown(self):
        if self.previous_path is None:
            os.environ.pop("ADVISORY_DATABASE_PATH", None)
        else:
            os.environ["ADVISORY_DATABASE_PATH"] = self.previous_path
        self.temp_dir.cleanup()

    def test_profiles_and_interactions_are_scoped_by_farmer(self):
        history_store.save_profile("farmer-a", {
            "location": "Guntur",
            "crops_grown": "rice",
            "soil_type": "clay",
            "land_size": "2 acres",
        })
        history_store.add_interaction({
            "farmer_id": "farmer-a",
            "original_input": "My rice has yellow leaves",
            "input_type": "voice",
            "intent": "crop_disease",
            "retrieved_sources": [{"title": "Rice leaf blast"}],
            "advisory": "Check the crop with an agriculture officer.",
            "language": "en",
        })

        self.assertEqual(history_store.get_profile("farmer-a")["location"], "Guntur")
        self.assertEqual(history_store.get_history("farmer-a")[0]["input_type"], "voice")
        self.assertEqual(history_store.get_history("farmer-a")[0]["retrieved_sources"][0]["title"], "Rice leaf blast")
        self.assertEqual(history_store.get_history("farmer-b"), [])


if __name__ == "__main__":
    unittest.main()
