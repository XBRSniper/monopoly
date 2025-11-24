-- Drop tables if they exist to start fresh (for development)
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS property_states CASCADE;
DROP TABLE IF EXISTS spaces CASCADE;
DROP TABLE IF EXISTS players CASCADE;
DROP TABLE IF EXISTS game_sessions CASCADE;

-- Game Sessions
CREATE TABLE game_sessions (
    id SERIAL PRIMARY KEY,
    status VARCHAR(20) NOT NULL DEFAULT 'waiting',
    current_turn_player_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Players
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES game_sessions(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    money INTEGER DEFAULT 1500,
    position INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    turn_order INTEGER DEFAULT 0
);

-- Spaces (Board Layout)
CREATE TABLE spaces (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES game_sessions(id) ON DELETE CASCADE,
    sequence_order INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    purchase_cost INTEGER,
    base_rent INTEGER,
    event_amount INTEGER DEFAULT 0,
    move_target INTEGER,
    UNIQUE (game_id, sequence_order)
);

-- Property States (Ownership and Improvements)
CREATE TABLE property_states (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES game_sessions(id) ON DELETE CASCADE,
    space_id INTEGER REFERENCES spaces(id) ON DELETE CASCADE,
    owner_id INTEGER REFERENCES players(id) ON DELETE SET NULL,
    improvement_count INTEGER DEFAULT 0
);

-- Optional transaction log for money changes and auditing
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES game_sessions(id) ON DELETE CASCADE,
    player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
