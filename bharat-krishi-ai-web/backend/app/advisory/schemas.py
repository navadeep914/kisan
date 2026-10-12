from typing import Literal

from pydantic import BaseModel, Field, field_validator


class FarmerProfile(BaseModel):
    location: str = Field(default="", max_length=100)
    crops_grown: str = Field(default="", max_length=200)
    soil_type: str = Field(default="", max_length=80)
    land_size: str = Field(default="", max_length=40)


class AdvisoryRequest(BaseModel):
    farmer_id: str = Field(min_length=1, max_length=100)
    query: str = Field(min_length=1, max_length=2000)
    input_type: Literal["text", "voice"] = "text"

    @field_validator("query")
    @classmethod
    def strip_query(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("query must contain non-whitespace text")
        return cleaned


class AdvisoryResponse(BaseModel):
    farmer_id: str
    original_input: str
    input_type: Literal["text", "voice"]
    parsed_query: dict
    advisory: str
    language: str
    retrieved_sources: list[dict]
    history_id: int
