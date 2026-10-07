"""Pydantic request/response models."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, model_validator

from app.services.notes import note_to_semitone


class SingerProfile(BaseModel):
    """A singer we want to match against songs."""

    name: str = Field(min_length=1, examples=["Mary J."])
    vocal_range_low: str = Field(examples=["C3"], description="Lowest comfortable note, e.g. C3")
    vocal_range_high: str = Field(examples=["C6"], description="Highest comfortable note, e.g. C6")
    vocal_style: str = Field(examples=["pop"], description="e.g. pop, rock, jazz, opera, R&B")
    energy: int = Field(ge=1, le=10, examples=[7], description="Performance energy, 1–10")

    @field_validator("vocal_range_low", "vocal_range_high")
    @classmethod
    def _must_be_valid_note(cls, value: str) -> str:
        note_to_semitone(value)  # raises ValueError with a clear message on failure
        return value

    @model_validator(mode="after")
    def _range_must_be_ordered(self) -> "SingerProfile":
        if note_to_semitone(self.vocal_range_low) > note_to_semitone(self.vocal_range_high):
            raise ValueError("vocal_range_low must not be higher than vocal_range_high")
        return self


class SongProfile(BaseModel):
    """A song with the qualities needed to sing it."""

    title: str = Field(min_length=1, examples=["Time After Time"])
    genre: str = Field(examples=["pop"])
    required_range_low: str = Field(examples=["G3"], description="Lowest note the song needs")
    required_range_high: str = Field(examples=["E5"], description="Highest note the song needs")
    energy: int = Field(ge=1, le=10, examples=[6], description="Energy the song demands, 1–10")

    @field_validator("required_range_low", "required_range_high")
    @classmethod
    def _must_be_valid_note(cls, value: str) -> str:
        note_to_semitone(value)
        return value

    @model_validator(mode="after")
    def _range_must_be_ordered(self) -> "SongProfile":
        if note_to_semitone(self.required_range_low) > note_to_semitone(self.required_range_high):
            raise ValueError("required_range_low must not be higher than required_range_high")
        return self


class MatchRequest(BaseModel):
    singer: SingerProfile
    song: SongProfile


class MatchBreakdown(BaseModel):
    """The three component scores that make up the overall match."""

    range_fit: float
    style_fit: float
    energy_fit: float


class MatchResult(BaseModel):
    singer: str
    song: str
    overall_score: float
    verdict: str
    breakdown: MatchBreakdown