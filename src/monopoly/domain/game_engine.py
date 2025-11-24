"""Core game loop and Monopoly rules."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from monopoly.db.repository import Repository

from monopoly.models import BoardSpace, Player, SpaceType

PASS_GO_BONUS = 200
IMPROVEMENT_COST = 100
IMPROVEMENT_RENT_BONUS = 50
SELLBACK_RATIO = 0.5


DEFAULT_BOARD = [
    {
        "name": "GO",
        "type": SpaceType.GO,
        "description": "Collect $200 when you pass.",
        "event_amount": PASS_GO_BONUS,
    },
    {
        "name": "Market Street",
        "type": SpaceType.PROPERTY,
        "description": "Busy local shops.",
        "purchase_cost": 120,
        "base_rent": 25,
    },
    {
        "name": "Volunteer Avenue",
        "type": SpaceType.PROPERTY,
        "description": "College town property.",
        "purchase_cost": 150,
        "base_rent": 35,
    },
    {
        "name": "City Tax",
        "type": SpaceType.TAX,
        "description": "Pay $150 to the city.",
        "event_amount": -150,
    },
    {
        "name": "Fountain City Bonus",
        "type": SpaceType.BONUS,
        "description": "Heritage festival payout.",
        "event_amount": 150,
    },
    {
        "name": "Cumberland Plaza",
        "type": SpaceType.PROPERTY,
        "description": "Mixed-use towers.",
        "purchase_cost": 180,
        "base_rent": 45,
    },
    {
        "name": "Go To Jail",
        "type": SpaceType.JAIL,
        "description": "Move to Jail (Space 8) and pay $50.",
        "event_amount": -50,
        "move_target": 8,
    },
    {
        "name": "Smoky Mountain Trail",
        "type": SpaceType.PROPERTY,
        "description": "Tourism hotspot.",
        "purchase_cost": 220,
        "base_rent": 55,
    },
    {
        "name": "Jail / Just Visiting",
        "type": SpaceType.FREE,
        "description": "Chill out for a turn.",
    },
    {
        "name": "Speeding Fine",
        "type": SpaceType.PENALTY,
        "description": "Pay $100.",
        "event_amount": -100,
    },
    {
        "name": "Market Expansion",
        "type": SpaceType.PROPERTY,
        "description": "Huge retail draw.",
        "purchase_cost": 260,
        "base_rent": 65,
    },
    {
        "name": "Chance",
        "type": SpaceType.CHANCE,
        "description": "Random reward or penalty.",
        "event_amount": 0,
    },
]


@dataclass
class TurnResult:
    player: Player
    space: BoardSpace
    dice_rolls: Tuple[int, int]
    messages: List[str] = field(default_factory=list)
    needs_buy_decision: bool = False
    landed_on_own_property: bool = False
    rent_paid: int = 0
    eliminated_players: List[str] = field(default_factory=list)
    winner: Optional[str] = None


class GameEngine:
    def __init__(self, repo: Repository, game_id: int) -> None:
        self.repo = repo
        self.game_id = game_id

    @classmethod
    def new_game_with_defaults(
        cls, repo: Repository, player_names: List[str], starting_money: int
    ) -> "GameEngine":
        game = repo.create_game(status="active")
        for idx, name in enumerate(player_names):
            repo.add_player(game.id, name, starting_money, idx)
        engine = cls(repo, game.id)
        engine.load_default_board()
        active_players = repo.list_players(game.id, active_only=True)
        if active_players:
            repo.set_current_turn(game.id, active_players[0].id)
        return engine

    def load_default_board(self) -> None:
        for idx, space in enumerate(DEFAULT_BOARD):
            self.repo.add_space(
                self.game_id,
                idx,
                space["name"],
                space["type"],
                space.get("description"),
                space.get("purchase_cost"),
                space.get("base_rent"),
                space.get("event_amount", 0),
                space.get("move_target"),
            )

    def ensure_game_ready(self) -> None:
        if self.repo.count_spaces(self.game_id) == 0:
            raise RuntimeError("Game is not set up. Add spaces before playing.")
        if not self.repo.list_players(self.game_id, active_only=True):
            raise RuntimeError("No players found. Add players before playing.")

    def roll_and_resolve(self, player: Player) -> TurnResult:
        self.ensure_game_ready()
        board_size = self.repo.count_spaces(self.game_id)
        die1, die2 = random.randint(1, 6), random.randint(1, 6)
        total = die1 + die2

        new_position = (player.position + total) % board_size
        passed_go = new_position < player.position
        self.repo.update_player_position(player.id, new_position)

        messages: list[str] = [
            f"Rolled {die1} + {die2} = {total}. Moved to space {new_position}."
        ]
        eliminated: list[str] = []

        if passed_go:
            self.repo.adjust_money(
                self.game_id, player.id, PASS_GO_BONUS, "Passed GO bonus"
            )
            messages.append(f"Collected ${PASS_GO_BONUS} for passing GO.")

        space = self.repo.get_space_by_order(self.game_id, new_position)
        if not space:
            raise RuntimeError("Space not found on board.")

        needs_buy = False
        landed_on_own = False
        rent_paid = 0

        if space.type == SpaceType.PROPERTY:
            needs_buy, landed_on_own, rent_paid, eliminated = self._resolve_property(
                player, space
            )
        else:
            event_messages, eliminated = self._resolve_event_space(player, space)
            messages.extend(event_messages)

        winner = self._detect_winner()

        return TurnResult(
            player=self.repo.get_player(player.id) or player,
            space=space,
            dice_rolls=(die1, die2),
            messages=messages,
            needs_buy_decision=needs_buy,
            landed_on_own_property=landed_on_own,
            rent_paid=rent_paid,
            eliminated_players=eliminated,
            winner=winner,
        )

    def _resolve_property(
        self, player: Player, space: BoardSpace
    ) -> tuple[bool, bool, int, List[str]]:
        state = self.repo.get_property_state(self.game_id, space.id)
        if not state:
            raise RuntimeError("Property state missing.")

        eliminated: list[str] = []

        if state.owner_id is None:
            return True, False, 0, eliminated

        if state.owner_id == player.id:
            return False, True, 0, eliminated

        rent = (space.base_rent or 0) + state.improvement_count * IMPROVEMENT_RENT_BONUS
        self.repo.transfer_money(
            self.game_id, player.id, state.owner_id, rent, f"Rent for {space.name}"
        )

        eliminated.extend(self._handle_bankruptcy_if_needed(player.id))
        return False, False, rent, eliminated

    def _resolve_event_space(
        self, player: Player, space: BoardSpace
    ) -> tuple[List[str], List[str]]:
        messages: list[str] = []
        eliminated: list[str] = []
        payout = space.event_amount

        if space.type == SpaceType.GO:
            payout = payout or PASS_GO_BONUS
            messages.append(f"Landed on GO and collected ${payout}.")
        elif space.type == SpaceType.BONUS:
            payout = payout or 150
            messages.append(f"Bonus space! Received ${payout}.")
        elif space.type == SpaceType.TAX:
            payout = payout or -150
            messages.append(f"Tax time. Paid ${abs(payout)}.")
        elif space.type == SpaceType.PENALTY:
            payout = payout or -100
            messages.append(f"Penalty applied: ${payout}.")
        elif space.type == SpaceType.JAIL:
            target = (
                space.move_target if space.move_target is not None else player.position
            )
            self.repo.update_player_position(player.id, target)
            payout = payout or -50
            messages.append("Sent to jail. Paying fine and moving to jail space.")
        elif space.type == SpaceType.CHANCE:
            payout = random.choice([-100, -50, 50, 100, 200])
            messages.append(
                f"Chance card effect: {'gain' if payout > 0 else 'lose'} ${abs(payout)}."
            )
        elif space.type == SpaceType.FREE:
            payout = payout or 0
            messages.append("Nothing happens here.")

        if payout != 0:
            self.repo.adjust_money(
                self.game_id, player.id, payout, f"Event {space.name}"
            )
            eliminated.extend(self._handle_bankruptcy_if_needed(player.id))

        return messages, eliminated

    def buy_property(self, player: Player, space: BoardSpace) -> bool:
        state = self.repo.get_property_state(self.game_id, space.id)
        if not state or state.owner_id is not None:
            return False
        if player.money < (space.purchase_cost or 0):
            return False
        self.repo.adjust_money(
            self.game_id, player.id, -(space.purchase_cost or 0), f"Bought {space.name}"
        )
        self.repo.set_property_owner(
            self.game_id, space.id, player.id, state.improvement_count
        )
        return True

    def improve_property(self, player: Player, space: BoardSpace) -> bool:
        state = self.repo.get_property_state(self.game_id, space.id)
        if not state or state.owner_id != player.id:
            return False
        if player.money < IMPROVEMENT_COST:
            return False
        self.repo.adjust_money(
            self.game_id, player.id, -IMPROVEMENT_COST, f"Improved {space.name}"
        )
        self.repo.increment_improvement(self.game_id, space.id)
        return True

    def sell_property(self, player: Player, space: BoardSpace) -> int:
        state = self.repo.get_property_state(self.game_id, space.id)
        if not state or state.owner_id != player.id:
            return 0
        sale_value = int((space.purchase_cost or 0) * SELLBACK_RATIO)
        sale_value += state.improvement_count * int(IMPROVEMENT_COST * SELLBACK_RATIO)
        self.repo.set_property_owner(self.game_id, space.id, None, 0)
        self.repo.adjust_money(
            self.game_id, player.id, sale_value, f"Sold {space.name} to bank"
        )
        return sale_value

    def sell_all_properties(self, player_id: int) -> None:
        owned = self.repo.properties_by_owner(self.game_id, player_id)
        for space, state in owned:
            sale_value = int((space.purchase_cost or 0) * SELLBACK_RATIO)
            sale_value += state.improvement_count * int(
                IMPROVEMENT_COST * SELLBACK_RATIO
            )
            self.repo.set_property_owner(self.game_id, space.id, None, 0)
            self.repo.adjust_money(
                self.game_id, player_id, sale_value, f"Forced sale of {space.name}"
            )

    def _handle_bankruptcy_if_needed(self, player_id: int) -> List[str]:
        eliminated: list[str] = []
        player = self.repo.get_player(player_id)
        if not player:
            return eliminated
        if player.money > 0:
            return eliminated
        self.sell_all_properties(player_id)
        player_after_sale = self.repo.get_player(player_id)
        if player_after_sale and player_after_sale.money <= 0:
            self.repo.update_player_active(player_id, False)
            eliminated.append(player_after_sale.name)
            self.repo.release_properties_to_bank(self.game_id, player_id)
            self.repo.reset_turn_orders(self.game_id)
        return eliminated

    def _detect_winner(self) -> Optional[str]:
        active_players = self.repo.list_players(self.game_id, active_only=True)
        if len(active_players) == 1:
            winner = active_players[0]
            self.repo.update_game_status(self.game_id, "completed")
            return winner.name
        return None

    def get_current_player(self) -> Optional[Player]:
        game = self.repo.get_game(self.game_id)
        if not game or not game.current_turn_player_id:
            return None
        return self.repo.get_player(game.current_turn_player_id)

    def next_turn(self) -> Optional[Player]:
        active = self.repo.list_players(self.game_id, active_only=True)
        if not active:
            return None
        active_sorted = sorted(active, key=lambda p: p.turn_order)
        game = self.repo.get_game(self.game_id)
        current_id = game.current_turn_player_id if game else None
        current_index = next(
            (
                idx
                for idx, player in enumerate(active_sorted)
                if player.id == current_id
            ),
            -1,
        )
        next_player = active_sorted[(current_index + 1) % len(active_sorted)]
        self.repo.set_current_turn(self.game_id, next_player.id)
        return next_player
