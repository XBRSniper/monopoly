"""Pydantic models for board spaces."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class SpaceType(str, Enum):
    PROPERTY = "property"
    GO = "go"
    TAX = "tax"
    BONUS = "bonus"
    JAIL = "jail"
    CHANCE = "chance"
    PENALTY = "penalty"
    FREE = "free"


class BoardSpace(BaseModel):
    id: int
    game_id: int
    sequence_order: int
    name: str
    type: SpaceType
    description: Optional[str] = None
    purchase_cost: Optional[int] = None
    base_rent: Optional[int] = None
    event_amount: int = 0
    move_target: Optional[int] = None
