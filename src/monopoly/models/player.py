"""Pydantic models for player data."""

from __future__ import annotations

from pydantic import BaseModel


class Player(BaseModel):
    id: int
    game_id: int
    name: str
    money: int
    position: int
    is_active: bool
    turn_order: int
