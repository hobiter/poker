-- PostgreSQL schema for Phase 1 core entities
-- Requires the uuid-ossp extension for UUID defaults
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  username TEXT,
  email TEXT,
  avatar TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  is_guest BOOLEAN DEFAULT false
);

CREATE TABLE rooms (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  host_id UUID REFERENCES users(id),
  name TEXT,
  seat_count INTEGER NOT NULL,
  invite_token TEXT,
  visibility TEXT,
  password_hash TEXT,
  config JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  status TEXT
);

CREATE INDEX idx_rooms_host ON rooms(host_id);

CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  room_id UUID REFERENCES rooms(id),
  started_at TIMESTAMPTZ,
  ended_at TIMESTAMPTZ,
  total_hands INTEGER DEFAULT 0,
  total_chips BIGINT DEFAULT 0,
  status TEXT
);

CREATE TABLE player_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID REFERENCES sessions(id),
  user_id UUID REFERENCES users(id),
  guest_name TEXT,
  seat_number INTEGER,
  buy_in BIGINT,
  ending_stack BIGINT,
  net_result BIGINT,
  hands_played INTEGER DEFAULT 0,
  vpip_count INTEGER DEFAULT 0,
  pfr_count INTEGER DEFAULT 0
);

CREATE INDEX idx_player_sessions_session ON player_sessions(session_id);

CREATE TABLE hands (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID REFERENCES sessions(id),
  hand_number INTEGER,
  button_seat INTEGER,
  small_blind BIGINT,
  big_blind BIGINT,
  board_cards TEXT[],
  pot BIGINT,
  started_at TIMESTAMPTZ,
  ended_at TIMESTAMPTZ
);

CREATE TABLE hand_actions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  hand_id UUID REFERENCES hands(id),
  player_session_id UUID REFERENCES player_sessions(id),
  street TEXT,
  action_type TEXT,
  amount BIGINT,
  timestamp TIMESTAMPTZ DEFAULT now(),
  stack_before BIGINT,
  stack_after BIGINT,
  sequence INTEGER
);

CREATE INDEX idx_hand_actions_hand ON hand_actions(hand_id);

CREATE TABLE player_hands (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  hand_id UUID REFERENCES hands(id),
  player_session_id UUID REFERENCES player_sessions(id),
  seat_number INTEGER,
  starting_stack BIGINT,
  ending_stack BIGINT,
  hole_cards TEXT[],
  voluntarily_put_money BOOLEAN DEFAULT false,
  preflop_raised BOOLEAN DEFAULT false,
  went_to_showdown BOOLEAN DEFAULT false,
  won_hand BOOLEAN DEFAULT false
);

CREATE TABLE analytics_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  room_id UUID,
  session_id UUID,
  hand_id UUID,
  player_session_id UUID,
  event_type TEXT,
  payload JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_analytics_room ON analytics_events(room_id);
