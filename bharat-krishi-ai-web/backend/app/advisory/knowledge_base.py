import json
import os
from pathlib import Path
from typing import Any

import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _backend_path(configured: str) -> Path:
    path = Path(configured)
    return path if path.is_absolute() else Path(__file__).resolve().parents[2] / path


class AgricultureKnowledgeBase:
    def __init__(self) -> None:
        self.seed_path = Path(__file__).with_name("seed_knowledge.json")
        self.embedding_model_name = os.getenv(
            "ADVISORY_EMBEDDING_MODEL",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        )
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        chroma_path = _backend_path(os.getenv("ADVISORY_CHROMA_PATH", "data/chroma"))
        self.client = chromadb.PersistentClient(path=str(chroma_path))
        self.collection = self.client.get_or_create_collection(
            name="farmer_advisory",
            metadata={"hnsw:space": "cosine", "embedding_model": self.embedding_model_name},
            embedding_function=None,
        )
        stored_model = (self.collection.metadata or {}).get("embedding_model")
        if self.collection.count() and stored_model != self.embedding_model_name:
            raise RuntimeError(
                "The existing Chroma collection uses a different embedding model. "
                "Set a new ADVISORY_CHROMA_PATH or re-ingest into a fresh collection."
            )
        self.ensure_seeded()

    def ensure_seeded(self) -> None:
        if self.collection.count():
            return
        entries = json.loads(self.seed_path.read_text(encoding="utf-8"))
        self.ingest(entries)

    def ingest(self, entries: list[dict[str, Any]]) -> int:
        if not entries:
            return 0
        documents = [self._document(entry) for entry in entries]
        self.collection.upsert(
            ids=[entry["id"] for entry in entries],
            documents=documents,
            metadatas=[
                {"category": entry["category"], "title": entry["title"]["en"]}
                for entry in entries
            ],
            embeddings=self._embed(documents),
        )
        return len(entries)

    def search(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        count = self.collection.count()
        if not count:
            return []
        result = self.collection.query(
            query_embeddings=self._embed([query]),
            n_results=min(top_k, count),
            include=["documents", "metadatas", "distances"],
        )
        matches = []
        for document, metadata, distance in zip(
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        ):
            score = max(0.0, 1.0 - float(distance))
            if score >= 0.08:
                matches.append({
                    "title": metadata["title"],
                    "category": metadata["category"],
                    "content": json.loads(document),
                    "score": round(score, 3),
                })
        return matches

    def _embed(self, texts: list[str]) -> list[list[float]]:
        return self.embedding_model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).tolist()

    @staticmethod
    def _document(entry: dict[str, Any]) -> str:
        return json.dumps(entry, ensure_ascii=False, sort_keys=True)
