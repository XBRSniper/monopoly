"""Pydantic models for game sessions."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class GameSession(BaseModel):
    id: int
    status: str
    current_turn_player_id: Optional[int] = None
    created_at: datetime
