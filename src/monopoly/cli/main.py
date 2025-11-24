"""Command-line interface for the Monopoly game."""

from __future__ import annotations

import sys
from typing import List, Optional

from monopoly.db.connection import Database
from monopoly.db.repository import Repository
from monopoly.domain.game_engine import GameEngine, IMPROVEMENT_COST
from monopoly.models import BoardSpace, Player, SpaceType


def print_banner() -> None:
    raw_banner = r"""
\e[48;5;15m                                                                 \e[m
\e[48;5;15m                                                                 \e[m
\e[48;5;15m                                                                 \e[m
\e[48;5;15m                                                                 \e[m
\e[48;5;15m                                                                 \e[m
\e[48;5;15m                                                                 \e[m
\e[48;5;15m                       \e[38;5;0;48;5;15m▄▄\e[38;5;188;48;5;15m▄\e[48;5;15m   \e[38;5;236;48;5;15m▄\e[38;5;0;48;5;15m▄\e[38;5;255;48;5;15m▄\e[48;5;15m                                 \e[m
\e[48;5;15m                      \e[38;5;232;48;5;255m▄\e[48;5;0m  \e[48;5;15m     \e[48;5;0m   \e[38;5;0;48;5;7m▄\e[38;5;232;48;5;15m▄\e[48;5;15m                              \e[m
\e[48;5;15m             \e[38;5;252;48;5;15m▄\e[38;5;234;48;5;15m▄\e[38;5;254;48;5;15m▄\e[38;5;255;48;5;15m▄\e[38;5;0;48;5;15m▄\e[48;5;15m \e[38;5;15;48;5;255m▄\e[38;5;0;48;5;15m▄\e[48;5;15m \e[48;5;0m  \e[38;5;15;48;5;0m▄\e[48;5;15m    \e[48;5;0m     \e[38;5;15;48;5;0m▄\e[38;5;234;48;5;234m▄\e[48;5;15m                             \e[m
\e[48;5;15m            \e[38;5;234;48;5;249m▄\e[48;5;15m \e[38;5;0;48;5;15m▄\e[48;5;15m \e[38;5;15;48;5;253m▄\e[48;5;15m \e[38;5;15;48;5;0m▄\e[38;5;254;48;5;15m▄\e[48;5;15m \e[38;5;0;48;5;232m▄\e[38;5;0;48;5;15m▄\e[48;5;15m  \e[38;5;15;48;5;250m▄\e[38;5;15;48;5;232m▄\e[38;5;15;48;5;0m▄\e[38;5;253;48;5;0m▄\e[38;5;232;48;5;0m▄\e[48;5;0m   \e[38;5;15;48;5;8m▄\e[38;5;0;48;5;15m▄\e[38;5;15;48;5;15m▄\e[48;5;15m                             \e[m
\e[48;5;15m           \e[38;5;0;48;5;243m▄\e[48;5;15m  \e[48;5;0m \e[38;5;15;48;5;253m▄\e[38;5;59;48;5;0m▄\e[38;5;15;48;5;0m▄\e[38;5;255;48;5;0m▄\e[48;5;0m \e[38;5;250;48;5;0m▄\e[38;5;0;48;5;255m▄\e[38;5;0;48;5;15m▄▄▄▄▄▄\e[38;5;0;48;5;236m▄\e[48;5;0m \e[38;5;0;48;5;233m▄\e[38;5;0;48;5;0m▄\e[38;5;254;48;5;0m▄\e[38;5;0;48;5;15m▄\e[38;5;15;48;5;255m▄\e[48;5;15m                              \e[m
\e[48;5;15m         \e[38;5;241;48;5;240m▄\e[38;5;232;48;5;15m▄\e[38;5;15;48;5;247m▄\e[48;5;15m   \e[38;5;237;48;5;15m▄\e[38;5;253;48;5;15m▄\e[38;5;15;48;5;0m▄\e[38;5;234;48;5;0m▄\e[38;5;15;48;5;232m▄\e[38;5;15;48;5;15m▄\e[48;5;15m   \e[38;5;15;48;5;232m▄\e[38;5;15;48;5;0m▄\e[38;5;0;48;5;15m▄\e[48;5;15m  \e[38;5;15;48;5;234m▄\e[38;5;15;48;5;0m▄\e[38;5;15;48;5;15m▄\e[38;5;0;48;5;15m▄\e[38;5;15;48;5;0m▄\e[38;5;15;48;5;242m▄\e[38;5;59;48;5;15m▄\e[48;5;15m                             \e[m
\e[48;5;15m        \e[48;5;0m \e[38;5;0;48;5;188m▄\e[38;5;232;48;5;15m▄\e[38;5;15;48;5;254m▄\e[38;5;15;48;5;0m▄\e[48;5;15m \e[38;5;0;48;5;15m▄\e[48;5;15m  \e[38;5;236;48;5;15m▄\e[48;5;15m \e[38;5;15;48;5;0m▄\e[48;5;15m    \e[38;5;15;48;5;0m▄\e[48;5;15m      \e[38;5;145;48;5;0m▄\e[38;5;0;48;5;15m▄\e[38;5;15;48;5;0m▄\e[48;5;15m \e[48;5;0m \e[48;5;15m     \e[38;5;232;48;5;15m▄\e[38;5;15;48;5;15m▄\e[38;5;15;48;5;0m▄▄\e[38;5;0;48;5;15m▄\e[48;5;15m                   \e[m
\e[48;5;15m        \e[38;5;238;48;5;0m▄\e[48;5;0m    \e[38;5;0;48;5;232m▄\e[38;5;0;48;5;243m▄\e[48;5;15m  \e[48;5;0m \e[48;5;15m \e[38;5;232;48;5;15m▄\e[38;5;232;48;5;232m▄\e[38;5;0;48;5;15m▄\e[38;5;235;48;5;15m▄\e[38;5;255;48;5;15m▄\e[48;5;15m         \e[38;5;233;48;5;234m▄\e[38;5;15;48;5;0m▄\e[38;5;0;48;5;15m▄\e[38;5;254;48;5;15m▄\e[48;5;15m \e[38;5;250;48;5;251m▄\e[48;5;0m  \e[48;5;15m \e[38;5;15;48;5;15m▄\e[38;5;15;48;5;255m▄▄\e[38;5;253;48;5;0m▄\e[38;5;0;48;5;15m▄\e[48;5;15m                  \e[m
\e[48;5;15m        \e[38;5;0;48;5;234m▄\e[38;5;8;48;5;0m▄\e[48;5;0m     \e[38;5;15;48;5;15m▄\e[38;5;0;48;5;0m▄\e[38;5;15;48;5;0m▄\e[38;5;15;48;5;8m▄\e[48;5;15m    \e[38;5;15;48;5;59m▄\e[38;5;234;48;5;15m▄\e[38;5;0;48;5;15m▄▄\e[38;5;234;48;5;15m▄\e[48;5;15m  \e[38;5;15;48;5;15m▄\e[38;5;0;48;5;15m▄\e[38;5;0;48;5;242m▄\e[38;5;15;48;5;0m▄\e[48;5;15m   \e[38;5;15;48;5;7m▄\e[38;5;15;48;5;251m▄\e[38;5;0;48;5;15m▄\e[38;5;15;48;5;0m▄\e[38;5;0;48;5;254m▄\e[48;5;15m \e[38;5;254;48;5;15m▄\e[48;5;15m  \e[38;5;15;48;5;15m▄\e[38;5;246;48;5;15m▄\e[38;5;242;48;5;15m▄\e[48;5;15m                \e[m
\e[48;5;15m        \e[38;5;145;48;5;0m▄\e[48;5;15m \e[48;5;0m      \e[38;5;0;48;5;15m▄\e[48;5;0m \e[38;5;0;48;5;15m▄\e[38;5;15;48;5;249m▄\e[38;5;15;48;5;0m▄▄\e[48;5;15m \e[38;5;238;48;5;15m▄\e[38;5;233;48;5;15m▄\e[38;5;255;48;5;15m▄\e[38;5;15;48;5;0m▄\e[48;5;15m  \e[38;5;0;48;5;15m▄\e[38;5;249;48;5;0m▄\e[38;5;15;48;5;0m▄\e[38;5;15;48;5;15m▄\e[38;5;243;48;5;15m▄\e[48;5;15m     \e[38;5;15;48;5;236m▄\e[38;5;254;48;5;0m▄\e[48;5;0m  \e[38;5;0;48;5;15m▄▄▄\e[48;5;0m  \e[38;5;0;48;5;15m▄\e[38;5;250;48;5;236m▄\e[38;5;255;48;5;15m▄\e[48;5;15m              \e[m
\e[48;5;15m         \e[38;5;255;48;5;0m▄\e[38;5;246;48;5;15m▄\e[38;5;188;48;5;0m▄\e[48;5;0m       \e[38;5;0;48;5;232m▄\e[38;5;0;48;5;15m▄\e[38;5;238;48;5;15m▄\e[48;5;15m   \e[38;5;237;48;5;15m▄\e[48;5;15m \e[38;5;15;48;5;15m▄\e[38;5;254;48;5;0m▄\e[38;5;15;48;5;15m▄\e[38;5;15;48;5;0m▄\e[48;5;0m  \e[38;5;248;48;5;0m▄\e[38;5;15;48;5;0m▄\e[48;5;15m      \e[38;5;15;48;5;233m▄\e[48;5;0m       \e[38;5;0;48;5;15m▄\e[38;5;240;48;5;0m▄\e[48;5;15m              \e[m
\e[48;5;15m          \e[38;5;15;48;5;241m▄\e[38;5;251;48;5;247m▄\e[38;5;0;48;5;255m▄\e[38;5;15;48;5;0m▄\e[38;5;237;48;5;0m▄\e[48;5;0m     \e[38;5;243;48;5;0m▄\e[38;5;0;48;5;15m▄\e[48;5;0m \e[38;5;15;48;5;237m▄\e[48;5;0m \e[38;5;15;48;5;0m▄\e[38;5;255;48;5;253m▄\e[38;5;15;48;5;0m▄\e[48;5;15m \e[38;5;0;48;5;232m▄\e[38;5;253;48;5;15m▄\e[38;5;15;48;5;253m▄\e[48;5;0m \e[38;5;255;48;5;0m▄\e[38;5;0;48;5;237m▄\e[48;5;15m    \e[38;5;236;48;5;15m▄\e[48;5;15m \e[38;5;15;48;5;245m▄\e[38;5;232;48;5;15m▄\e[48;5;0m \e[38;5;15;48;5;0m▄\e[48;5;0m     \e[38;5;15;48;5;15m▄▄\e[48;5;15m             \e[m
\e[48;5;15m             \e[38;5;15;48;5;234m▄\e[38;5;15;48;5;0m▄\e[38;5;15;48;5;15m▄\e[38;5;251;48;5;15m▄\e[38;5;236;48;5;255m▄\e[38;5;232;48;5;243m▄\e[38;5;0;48;5;238m▄\e[48;5;0m \e[38;5;236;48;5;233m▄\e[38;5;0;48;5;15m▄\e[38;5;0;48;5;255m▄\e[48;5;15m \e[38;5;15;48;5;242m▄\e[38;5;15;48;5;232m▄\e[48;5;15m  \e[38;5;250;48;5;0m▄\e[38;5;248;48;5;15m▄\e[38;5;15;48;5;0m▄\e[38;5;255;48;5;0m▄\e[38;5;0;48;5;0m▄\e[38;5;15;48;5;0m▄\e[48;5;15m \e[38;5;15;48;5;237m▄\e[38;5;145;48;5;0m▄\e[38;5;15;48;5;0m▄▄\e[38;5;15;48;5;237m▄\e[38;5;15;48;5;15m▄\e[48;5;15m  \e[38;5;252;48;5;233m▄\e[48;5;15m \e[38;5;234;48;5;0m▄\e[48;5;0m  \e[38;5;15;48;5;0m▄\e[38;5;0;48;5;241m▄\e[48;5;15m              \e[m
\e[48;5;15m             \e[38;5;255;48;5;15m▄\e[38;5;0;48;5;15m▄\e[38;5;232;48;5;15m▄\e[38;5;15;48;5;15m▄\e[38;5;15;48;5;235m▄\e[38;5;15;48;5;0m▄▄▄▄▄▄\e[38;5;102;48;5;188m▄\e[38;5;0;48;5;15m▄\e[38;5;249;48;5;15m▄\e[38;5;15;48;5;253m▄\e[38;5;15;48;5;15m▄\e[48;5;15m \e[38;5;15;48;5;0m▄\e[38;5;0;48;5;15m▄\e[48;5;15m \e[38;5;0;48;5;15m▄\e[38;5;246;48;5;15m▄\e[48;5;15m \e[38;5;15;48;5;102m▄\e[48;5;15m  \e[48;5;0m \e[48;5;15m     \e[38;5;237;48;5;247m▄\e[38;5;15;48;5;15m▄\e[48;5;0m \e[38;5;239;48;5;236m▄\e[38;5;15;48;5;238m▄\e[48;5;15m  \e[38;5;0;48;5;15m▄▄\e[48;5;15m           \e[m
\e[48;5;15m           \e[38;5;0;48;5;15m▄\e[38;5;15;48;5;0m▄\e[38;5;15;48;5;253m▄\e[48;5;15m             \e[38;5;15;48;5;250m▄\e[38;5;15;48;5;243m▄\e[38;5;15;48;5;233m▄\e[38;5;15;48;5;234m▄\e[38;5;15;48;5;0m▄\e[38;5;233;48;5;0m▄\e[38;5;249;48;5;240m▄\e[38;5;0;48;5;15m▄▄\e[38;5;0;48;5;233m▄\e[38;5;239;48;5;249m▄\e[38;5;15;48;5;0m▄\e[38;5;145;48;5;15m▄\e[38;5;15;48;5;15m▄\e[48;5;15m   \e[38;5;0;48;5;253m▄\e[38;5;0;48;5;233m▄\e[48;5;0m  \e[38;5;0;48;5;15m▄\e[38;5;15;48;5;15m▄\e[38;5;15;48;5;255m▄\e[38;5;232;48;5;0m▄\e[48;5;0m  \e[38;5;15;48;5;0m▄\e[48;5;15m          \e[m
\e[48;5;15m         \e[38;5;0;48;5;15m▄\e[38;5;15;48;5;0m▄\e[48;5;15m                         \e[38;5;15;48;5;0m▄▄\e[38;5;236;48;5;233m▄\e[38;5;145;48;5;15m▄\e[48;5;15m \e[38;5;0;48;5;15m▄\e[38;5;238;48;5;15m▄\e[38;5;251;48;5;0m▄\e[38;5;15;48;5;0m▄▄▄\e[38;5;15;48;5;252m▄\e[48;5;15m       \e[38;5;232;48;5;255m▄\e[38;5;232;48;5;0m▄\e[38;5;15;48;5;239m▄\e[38;5;233;48;5;15m▄\e[38;5;241;48;5;15m▄\e[48;5;15m     \e[m
\e[48;5;15m   \e[38;5;233;48;5;247m▄\e[38;5;252;48;5;0m▄\e[38;5;0;48;5;246m▄\e[38;5;0;48;5;15m▄▄▄\e[38;5;247;48;5;188m▄\e[48;5;15m                    \e[38;5;15;48;5;237m▄\e[38;5;246;48;5;15m▄\e[48;5;15m                       \e[38;5;0;48;5;0m▄\e[48;5;0m   \e[38;5;0;48;5;15m▄\e[38;5;15;48;5;0m▄\e[38;5;252;48;5;15m▄\e[48;5;15m   \e[m
\e[48;5;15m    \e[38;5;15;48;5;242m▄\e[38;5;233;48;5;102m▄\e[38;5;15;48;5;0m▄\e[48;5;0m   \e[48;5;15m         \e[38;5;0;48;5;15m▄\e[38;5;15;48;5;15m▄\e[38;5;15;48;5;0m▄\e[48;5;15m \e[38;5;15;48;5;8m▄\e[38;5;15;48;5;232m▄\e[38;5;0;48;5;15m▄\e[38;5;249;48;5;15m▄\e[48;5;15m    \e[38;5;15;48;5;252m▄\e[38;5;236;48;5;248m▄\e[38;5;0;48;5;15m▄\e[48;5;15m                   \e[38;5;0;48;5;15m▄\e[38;5;15;48;5;237m▄\e[38;5;15;48;5;15m▄\e[48;5;15m  \e[38;5;15;48;5;188m▄\e[38;5;15;48;5;0m▄▄\e[38;5;15;48;5;243m▄\e[48;5;15m   \e[m
\e[48;5;15m      \e[38;5;15;48;5;15m▄\e[38;5;15;48;5;245m▄\e[48;5;15m \e[38;5;15;48;5;233m▄\e[48;5;15m \e[38;5;249;48;5;15m▄\e[38;5;15;48;5;15m▄\e[48;5;15m   \e[38;5;0;48;5;15m▄\e[38;5;15;48;5;254m▄\e[38;5;15;48;5;0m▄\e[48;5;15m        \e[38;5;15;48;5;0m▄▄\e[38;5;15;48;5;236m▄\e[38;5;15;48;5;7m▄\e[38;5;15;48;5;255m▄\e[48;5;15m \e[38;5;15;48;5;245m▄\e[38;5;15;48;5;0m▄\e[38;5;0;48;5;59m▄\e[38;5;0;48;5;15m▄▄\e[38;5;253;48;5;15m▄\e[48;5;15m         \e[38;5;251;48;5;15m▄\e[38;5;0;48;5;15m▄▄\e[38;5;15;48;5;233m▄\e[38;5;15;48;5;232m▄\e[48;5;15m            \e[m
\e[48;5;15m          \e[38;5;15;48;5;0m▄\e[48;5;0m  \e[38;5;246;48;5;0m▄\e[38;5;15;48;5;145m▄\e[38;5;15;48;5;232m▄\e[48;5;15m                     \e[38;5;15;48;5;245m▄\e[38;5;15;48;5;0m▄▄▄▄▄▄▄▄▄▄\e[38;5;15;48;5;255m▄\e[48;5;15m                \e[m
\e[48;5;15m                                                                 \e[m
\e[48;5;15m                                                                 \e[m
\e[48;5;15m                                                                 \e[m
\e[48;5;15m                                                                 \e[m
\e[48;5;15m                                                                 \e[m
\e[48;5;15m                                                                 \e[m
\e[49;38;5;15m▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀\e[m
          """
    banner = raw_banner.replace(r"\e", "\033")
    print(banner)
    print("=" * 60)
    print("MONOPOLY - Terminal Edition")
    print("=" * 60)


def print_rules() -> None:
    print("--- RULES SUMMARY ---")
    print("1) Roll two dice and move clockwise.")
    print("2) Unowned property: you may buy it.")
    print("3) Owned property: pay rent to the owner.")
    print("4) Your property: you may improve or sell it when you land on it.")
    print("5) Special spaces (tax/bonus/jail/chance) trigger automatic events.")
    print(
        "6) Passing GO pays $200. Hitting $0 forces selling property back to the bank."
    )
    print(
        "7) A player with $0 and no property is eliminated. Last player standing wins."
    )


def prompt_int(prompt: str, default: Optional[int] = None, minimum: int = 0) -> int:
    while True:
        raw = input(
            f"{prompt} " + (f"[default {default}]: " if default is not None else ": ")
        )
        if raw.strip() == "" and default is not None:
            return default
        try:
            value = int(raw)
            if value < minimum:
                print(f"Enter a number >= {minimum}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number.")


def prompt_yes_no(prompt: str, default: str = "y") -> bool:
    default = default.lower()
    while True:
        raw = input(
            f"{prompt} [{'Y' if default == 'y' else 'y'}/{'N' if default == 'n' else 'n'}]: "
        ).lower()
        if raw.strip() == "" and default in {"y", "n"}:
            return default == "y"
        if raw in {"y", "yes"}:
            return True
        if raw in {"n", "no"}:
            return False
        print("Please respond with y or n.")


def collect_players(
    repo: Repository, game_id: int, starting_money: int
) -> List[Player]:
    players: list[Player] = []
    print("Enter player names (minimum 2). Leave blank to finish.")
    turn_order = 0
    while True:
        name = input(f"Player {turn_order + 1} name: ").strip()
        if name == "":
            if len(players) >= 2:
                break
            print("At least two players are required.")
            continue
        if any(p.name.lower() == name.lower() for p in players):
            print("Name already used. Choose a unique player name.")
            continue
        player = repo.add_player(game_id, name, starting_money, turn_order)
        players.append(player)
        turn_order += 1
    return players


def add_property_space(repo: Repository, game_id: int) -> BoardSpace:
    sequence = repo.next_sequence_order(game_id)
    name = input("Property name: ").strip() or f"Property {sequence}"
    cost = prompt_int("Purchase cost:", 100, minimum=1)
    rent = prompt_int("Base rent:", 20, minimum=1)
    desc = input("Short description: ").strip() or "User created property."
    space = repo.add_space(
        game_id,
        sequence,
        name,
        SpaceType.PROPERTY,
        desc,
        cost,
        rent,
        0,
        None,
    )
    print(f"Added property '{space.name}' at position {sequence}.")
    return space


def select_event_type() -> SpaceType:
    valid = [t for t in SpaceType if t != SpaceType.PROPERTY]
    print("Choose event type:")
    for idx, space_type in enumerate(valid, start=1):
        print(f"{idx}. {space_type.value}")
    while True:
        choice = input("Type number: ").strip()
        if not choice.isdigit() or not (1 <= int(choice) <= len(valid)):
            print("Invalid selection.")
            continue
        return valid[int(choice) - 1]


def add_non_property_space(repo: Repository, game_id: int) -> BoardSpace:
    sequence = repo.next_sequence_order(game_id)
    space_type = select_event_type()
    name = input("Space name: ").strip() or f"{space_type.value.title()} {sequence}"
    desc = input("Short description: ").strip()
    event_amount = prompt_int(
        "Event payout (negative for fees, 0 for default effect):", 0
    )
    move_target = None
    if space_type == SpaceType.JAIL:
        move_target = prompt_int(
            "Move target index (where Jail is on the board)", sequence
        )
    space = repo.add_space(
        game_id,
        sequence,
        name,
        space_type,
        desc,
        None,
        None,
        event_amount,
        move_target,
    )
    print(f"Added {space.type.value} space '{space.name}' at position {sequence}.")
    return space


def manual_board_setup(repo: Repository, game_id: int) -> None:
    non_property_count = 0
    while True:
        print("\nBoard Builder:")
        print("1. Add property")
        print("2. Add non-property space")
        print("3. Finish")
        choice = input("Select an option: ").strip()
        if choice == "1":
            add_property_space(repo, game_id)
        elif choice == "2":
            space = add_non_property_space(repo, game_id)
            if space.type != SpaceType.PROPERTY:
                non_property_count += 1
        elif choice == "3":
            board_size = repo.count_spaces(game_id)
            if board_size == 0:
                print("You need at least one space before finishing.")
                continue
            if non_property_count < 4:
                print("Add at least 4 non-property spaces to satisfy requirements.")
                continue
            break
        else:
            print("Invalid option.")


def show_status(repo: Repository, game_id: int) -> None:
    game = repo.get_game(game_id)
    current_id = game.current_turn_player_id if game else None
    players = repo.list_players(game_id)
    print("\nPlayers:")
    for player in players:
        status = "ACTIVE" if player.is_active else "OUT"
        turn_marker = " (current turn)" if player.id == current_id else ""
        print(
            f"- {player.name}: ${player.money} | Pos {player.position} | {status}{turn_marker}"
        )

    spaces = repo.list_spaces(game_id)
    print("\nBoard:")
    for space in spaces:
        owner_name = ""
        if space.type == SpaceType.PROPERTY:
            ps = repo.get_property_state(game_id, space.id)
            owner = repo.get_player(ps.owner_id) if ps and ps.owner_id else None
            owner_name = f" | Owner: {owner.name if owner else 'Bank'} | Improves: {ps.improvement_count if ps else 0}"
        print(f"{space.sequence_order}. {space.name} ({space.type.value}){owner_name}")
    print()


def ensure_turn_pointer(repo: Repository, game_id: int) -> Player:
    game = repo.get_game(game_id)
    if game and game.current_turn_player_id:
        player = repo.get_player(game.current_turn_player_id)
        if player:
            return player
    players = repo.list_players(game_id, active_only=True)
    if not players:
        raise RuntimeError("No active players available.")
    repo.set_current_turn(game_id, players[0].id)
    return players[0]


def handle_property_decision(
    engine: GameEngine, player: Player, space: BoardSpace, needs_buy: bool
) -> None:
    repo = engine.repo
    if needs_buy:
        want = prompt_yes_no(
            f"Do you want to buy {space.name} for ${space.purchase_cost}?"
        )
        if want:
            success = engine.buy_property(player, space)
            if success:
                print(f"Purchased {space.name}.")
            else:
                print("Unable to purchase (insufficient funds or already owned).")
    else:
        ps = repo.get_property_state(engine.game_id, space.id)
        if ps and ps.owner_id == player.id:
            print("You own this property.")
            print("1. Improve property")
            print("2. Sell property to bank")
            print("3. Skip")
            choice = input("Select an option: ").strip()
            if choice == "1":
                if engine.improve_property(player, space):
                    print(f"Improved {space.name} for ${IMPROVEMENT_COST}.")
                else:
                    print("Cannot improve (not enough funds?).")
            elif choice == "2":
                sale = engine.sell_property(player, space)
                print(f"Sold {space.name} for ${sale}.")


def play_game(engine: GameEngine) -> None:
    repo = engine.repo
    current_player = ensure_turn_pointer(repo, engine.game_id)

    while True:
        print(f"\n--- {current_player.name}'s Turn ---")
        cmd = (
            input(
                f"[R]oll | [S]tatus | [Q]uit to main menu (You have ${current_player.money}): "
            )
            .strip()
            .lower()
        )
        if cmd in {"q", "quit"}:
            break
        if cmd in {"s", "status"}:
            show_status(repo, engine.game_id)
            continue
        if cmd not in {"r", "roll", ""}:
            print("Invalid command.")
            continue

        result = engine.roll_and_resolve(current_player)
        current_player = result.player
        for msg in result.messages:
            print(msg)

        if result.space.type == SpaceType.PROPERTY:
            state = repo.get_property_state(engine.game_id, result.space.id)
            owner = (
                repo.get_player(state.owner_id) if state and state.owner_id else None
            )
            if owner and owner.id != current_player.id:
                print(
                    f"Landed on {owner.name}'s property. Rent paid: ${result.rent_paid}."
                )
            elif state and state.owner_id is None:
                print("This property is unowned.")
            if current_player.is_active:
                handle_property_decision(
                    engine, current_player, result.space, result.needs_buy_decision
                )

        if result.eliminated_players:
            for name in result.eliminated_players:
                print(f"{name} has been eliminated.")
            if not current_player.is_active:
                print(f"{current_player.name} is out of the game.")

        if result.winner:
            print(f"{result.winner} wins the game!")
            break

        next_player = engine.next_turn()
        if not next_player:
            print("No active players remaining.")
            break
        current_player = next_player


def start_new_game(repo: Repository) -> None:
    reset = prompt_yes_no("Reset database schema? (drops existing games)", default="n")
    if reset:
        repo.db.apply_schema()
    starting_money = prompt_int("Starting money per player", default=1500, minimum=1)
    try:
        game = repo.create_game(status="setup")
    except Exception as exc:
        print(f"Could not start game (did you reset the schema?): {exc}")
        return
    players = collect_players(repo, game.id, starting_money)
    engine = GameEngine(repo, game.id)
    if prompt_yes_no("Use default board layout?", default="y"):
        engine.load_default_board()
    else:
        manual_board_setup(repo, game.id)
    repo.update_game_status(game.id, "active")
    if players:
        repo.set_current_turn(game.id, players[0].id)
    print(f"Game {game.id} ready. Starting...")
    play_game(engine)


def load_game(repo: Repository) -> None:
    game_id = prompt_int("Enter game ID to load", minimum=1)
    game = repo.get_game(game_id)
    if not game:
        print("Game not found.")
        return
    engine = GameEngine(repo, game_id)
    print(f"Loaded game {game_id}.")
    try:
        engine.ensure_game_ready()
    except RuntimeError as exc:
        print(f"Cannot start game: {exc}")
        return
    play_game(engine)


def main() -> None:
    print_banner()
    try:
        db = Database()
    except ValueError as exc:
        print(f"Database error: {exc}")
        sys.exit(1)

    repo = Repository(db)

    while True:
        print("\nMain Menu")
        print("1. Start new game")
        print("2. Load existing game")
        print("3. View rules")
        print("4. Exit")
        choice = input("Select an option: ").strip()
        if choice == "1":
            start_new_game(repo)
        elif choice == "2":
            load_game(repo)
        elif choice == "3":
            print_rules()
        elif choice == "4":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid selection.")


if __name__ == "__main__":
    main()
