# Monopoly

![game](docs/readme/game.gif)
-----

## Overview

A text-based Monopoly implementation that uses PostgreSQL (e.g., ElephantSQL) for persistence. It supports new games, loading existing games, default or custom boards, buying/improving/selling properties, automatic event spaces, bankruptcy enforcement, and victory detection.

## Prerequisites

- Python 3.8+
- PostgreSQL connection string exported as `DATABASE_URL` (or stored in a `.env` file). Example:  
  `DATABASE_URL=postgresql://user:password@hostname:5432/database`
- Dependencies from `pyproject.toml` (`psycopg[binary]`, `pydantic`, `python-dotenv`).

## Running

```bash
python -m monopoly
```

Main menu options:
- **Start new game** – Optionally reset schema (drops tables), set starting money, add players (≥2, unique names), and choose default or manual board builder (requires ≥4 non-property spaces).
- **Load existing game** – Provide a game ID already stored in the database.
- **View rules** – Quick summary of the simplified Monopoly rules implemented here.

Gameplay:
- Roll 2d6 to move; passing GO automatically awards $200.
- Unowned property → choose to buy.
- Owned by another player → rent auto-paid based on improvements.
- Owned by you → option to improve (cost $100) or sell back to the bank (50% of purchase + improvements).
- Special spaces (tax/bonus/jail/chance/penalty/free) apply automatic money/position effects.
- If money ≤ 0, properties are forcibly sold back to the bank; players with $0 and no property are eliminated. Last active player wins.

## Database Design

```mermaid
erDiagram
    game_sessions ||--o{ players : has
    game_sessions ||--o{ spaces : defines
    game_sessions ||--o{ propertystates : tracks
    game_sessions ||--o{ transactions : logs

    players {
        int id PK
        int game_id FK
        string name
        int money
        int position
        bool is_active
        int turn_order
    }

    spaces {
        int id PK
        int game_id FK
        int sequence_order
        string name
        string type
        string description
        int purchase_cost
        int base_rent
        int event_amount
        int move_target
    }

    propertystates {
        int id PK
        int game_id FK
        int space_id FK
        int owner_id FK
        int improvement_count
    }

    transactions {
        int id PK
        int game_id FK
        int player_id FK
        int amount
        string description
        datetime created_at
    }
```

## License

`monopoly` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
