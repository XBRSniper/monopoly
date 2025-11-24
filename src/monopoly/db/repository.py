"""Persistence layer for Monopoly game state."""

from __future__ import annotations

from typing import List, Optional

from psycopg.rows import dict_row

from monopoly.models import BoardSpace, GameSession, Player, PropertyState, SpaceType
from monopoly.db.connection import Database


class Repository:
    """Simple repository that wraps SQL operations."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def create_game(self, status: str = "setup") -> GameSession:
        with self.db.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "INSERT INTO game_sessions (status) VALUES (%s) RETURNING *;",
                (status,),
            )
            row = cur.fetchone()
            return GameSession.model_validate(row)

    def get_game(self, game_id: int) -> Optional[GameSession]:
        with self.db.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM game_sessions WHERE id = %s;", (game_id,))
            row = cur.fetchone()
            return GameSession.model_validate(row) if row else None

    def update_game_status(self, game_id: int, status: str) -> None:
        with self.db.connection() as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE game_sessions SET status = %s WHERE id = %s;", (status, game_id)
            )

    def set_current_turn(self, game_id: int, player_id: int) -> None:
        with self.db.connection() as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE game_sessions SET current_turn_player_id = %s WHERE id = %s;",
                (player_id, game_id),
            )

    def add_player(
        self, game_id: int, name: str, starting_money: int, turn_order: int
    ) -> Player:
        with self.db.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO players (game_id, name, money, turn_order)
                VALUES (%s, %s, %s, %s) RETURNING *;
                """,
                (game_id, name, starting_money, turn_order),
            )
            row = cur.fetchone()
            return Player.model_validate(row)

    def list_players(self, game_id: int, active_only: bool = False) -> List[Player]:
        where_clause = "WHERE game_id = %s"
        params: list[object] = [game_id]
        if active_only:
            where_clause += " AND is_active = TRUE"
        with self.db.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"SELECT * FROM players {where_clause} ORDER BY turn_order ASC;",
                tuple(params),
            )
            rows = cur.fetchall()
            return [Player.model_validate(r) for r in rows]

    def get_player(self, player_id: int) -> Optional[Player]:
        with self.db.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM players WHERE id = %s;", (player_id,))
            row = cur.fetchone()
            return Player.model_validate(row) if row else None

    def update_player_position(self, player_id: int, position: int) -> None:
        with self.db.connection() as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE players SET position = %s WHERE id = %s;", (position, player_id)
            )

    def update_player_active(self, player_id: int, is_active: bool) -> None:
        with self.db.connection() as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE players SET is_active = %s WHERE id = %s;",
                (is_active, player_id),
            )

    def adjust_money(
        self, game_id: int, player_id: int, delta: int, description: str
    ) -> Player:
        with self.db.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "UPDATE players SET money = money + %s WHERE id = %s RETURNING *;",
                (delta, player_id),
            )
            row = cur.fetchone()
            cur.execute(
                """
                INSERT INTO transactions (game_id, player_id, amount, description)
                VALUES (%s, %s, %s, %s);
                """,
                (game_id, player_id, delta, description),
            )
            return Player.model_validate(row)

    def set_money(self, player_id: int, amount: int) -> Player:
        with self.db.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "UPDATE players SET money = %s WHERE id = %s RETURNING *;",
                (amount, player_id),
            )
            row = cur.fetchone()
            return Player.model_validate(row)

    def add_space(
        self,
        game_id: int,
        sequence_order: int,
        name: str,
        type_: SpaceType | str,
        description: str | None = None,
        purchase_cost: int | None = None,
        base_rent: int | None = None,
        event_amount: int = 0,
        move_target: int | None = None,
    ) -> BoardSpace:
        type_enum = type_ if isinstance(type_, SpaceType) else SpaceType(type_)

        with self.db.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO spaces (
                    game_id, sequence_order, name, type, description,
                    purchase_cost, base_rent, event_amount, move_target
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *;
                """,
                (
                    game_id,
                    sequence_order,
                    name,
                    type_enum.value,
                    description,
                    purchase_cost,
                    base_rent,
                    event_amount,
                    move_target,
                ),
            )
            row = cur.fetchone()
            space = BoardSpace.model_validate(row)
            if type_enum == SpaceType.PROPERTY:
                cur.execute(
                    """
                    INSERT INTO property_states (game_id, space_id, owner_id, improvement_count)
                    VALUES (%s, %s, NULL, 0);
                    """,
                    (game_id, space.id),
                )
            return space

    def list_spaces(self, game_id: int) -> List[BoardSpace]:
        with self.db.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT * FROM spaces WHERE game_id = %s ORDER BY sequence_order ASC;",
                (game_id,),
            )
            rows = cur.fetchall()
            return [BoardSpace.model_validate(r) for r in rows]

    def get_space_by_order(
        self, game_id: int, sequence_order: int
    ) -> Optional[BoardSpace]:
        with self.db.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT * FROM spaces WHERE game_id = %s AND sequence_order = %s;",
                (game_id, sequence_order),
            )
            row = cur.fetchone()
            return BoardSpace.model_validate(row) if row else None

    def get_space_by_id(self, space_id: int) -> Optional[BoardSpace]:
        with self.db.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM spaces WHERE id = %s;", (space_id,))
            row = cur.fetchone()
            return BoardSpace.model_validate(row) if row else None

    def get_property_state(
        self, game_id: int, space_id: int
    ) -> Optional[PropertyState]:
        with self.db.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT * FROM property_states WHERE game_id = %s AND space_id = %s;",
                (game_id, space_id),
            )
            row = cur.fetchone()
            return PropertyState.model_validate(row) if row else None

    def set_property_owner(
        self,
        game_id: int,
        space_id: int,
        owner_id: Optional[int],
        improvement_count: Optional[int] = None,
    ) -> None:
        update_sql = "UPDATE property_states SET owner_id = %s"
        params: list[object] = [owner_id]
        if improvement_count is not None:
            update_sql += ", improvement_count = %s"
            params.append(improvement_count)
        update_sql += " WHERE game_id = %s AND space_id = %s;"
        params.extend([game_id, space_id])

        with self.db.connection() as conn, conn.cursor() as cur:
            cur.execute(update_sql, tuple(params))

    def increment_improvement(self, game_id: int, space_id: int) -> PropertyState:
        with self.db.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                UPDATE property_states
                SET improvement_count = improvement_count + 1
                WHERE game_id = %s AND space_id = %s
                RETURNING *;
                """,
                (game_id, space_id),
            )
            row = cur.fetchone()
            return PropertyState.model_validate(row)

    def properties_by_owner(
        self, game_id: int, owner_id: int
    ) -> List[tuple[BoardSpace, PropertyState]]:
        with self.db.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT
                    ps.id AS ps_id,
                    ps.game_id AS ps_game_id,
                    ps.space_id AS ps_space_id,
                    ps.owner_id,
                    ps.improvement_count,
                    s.id AS space_id,
                    s.game_id AS space_game_id,
                    s.sequence_order,
                    s.name,
                    s.type,
                    s.description,
                    s.purchase_cost,
                    s.base_rent,
                    s.event_amount,
                    s.move_target
                FROM property_states ps
                JOIN spaces s ON ps.space_id = s.id
                WHERE ps.game_id = %s AND ps.owner_id = %s
                ORDER BY s.sequence_order;
                """,
                (game_id, owner_id),
            )
            rows = cur.fetchall()
            results: list[tuple[BoardSpace, PropertyState]] = []
            for row in rows:
                ps_row = {
                    "id": row["ps_id"],
                    "game_id": row["ps_game_id"],
                    "space_id": row["ps_space_id"],
                    "owner_id": row["owner_id"],
                    "improvement_count": row["improvement_count"],
                }
                space_row = {
                    "id": row["space_id"],
                    "game_id": row["space_game_id"],
                    "sequence_order": row["sequence_order"],
                    "name": row["name"],
                    "type": row["type"],
                    "description": row["description"],
                    "purchase_cost": row["purchase_cost"],
                    "base_rent": row["base_rent"],
                    "event_amount": row["event_amount"],
                    "move_target": row["move_target"],
                }
                results.append(
                    (
                        BoardSpace.model_validate(space_row),
                        PropertyState.model_validate(ps_row),
                    )
                )
            return results

    def release_properties_to_bank(self, game_id: int, owner_id: int) -> None:
        with self.db.connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                UPDATE property_states
                SET owner_id = NULL, improvement_count = 0
                WHERE game_id = %s AND owner_id = %s;
                """,
                (game_id, owner_id),
            )

    def count_spaces(self, game_id: int) -> int:
        with self.db.connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM spaces WHERE game_id = %s;", (game_id,))
            row = cur.fetchone()
            count = row[0] if row else 0
            return int(count)

    def next_sequence_order(self, game_id: int) -> int:
        with self.db.connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(MAX(sequence_order) + 1, 0) FROM spaces WHERE game_id = %s;",
                (game_id,),
            )
            row = cur.fetchone()
            next_order = row[0] if row else 0
            return int(next_order)

    def reset_turn_orders(self, game_id: int) -> None:
        """Re-normalize turn order so active players stay in order without gaps."""
        players = self.list_players(game_id, active_only=True)
        for idx, player in enumerate(players):
            with self.db.connection() as conn, conn.cursor() as cur:
                cur.execute(
                    "UPDATE players SET turn_order = %s WHERE id = %s;",
                    (idx, player.id),
                )

    def transfer_money(
        self, game_id: int, payer_id: int, payee_id: int, amount: int, description: str
    ) -> None:
        self.adjust_money(
            game_id, payer_id, -amount, f"Paid {amount} for {description}"
        )
        self.adjust_money(
            game_id, payee_id, amount, f"Received {amount} for {description}"
        )

    def remove_player(self, player_id: int) -> None:
        with self.db.connection() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM players WHERE id = %s;", (player_id,))
