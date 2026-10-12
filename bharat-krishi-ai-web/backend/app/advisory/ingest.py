import json
from pathlib import Path

from app.advisory.knowledge_base import AgricultureKnowledgeBase


def main() -> None:
    seed_path = Path(__file__).with_name("seed_knowledge.json")
    entries = json.loads(seed_path.read_text(encoding="utf-8"))
    count = AgricultureKnowledgeBase().ingest(entries)
    print(f"Ingested {count} curated agriculture entries into ChromaDB.")


if __name__ == "__main__":
    main()
