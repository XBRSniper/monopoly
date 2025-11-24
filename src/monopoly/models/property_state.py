"""Ownership and improvement state for properties."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class PropertyState(BaseModel):
    id: int
    game_id: int
    space_id: int
    owner_id: Optional[int] = None
    improvement_count: int = 0
