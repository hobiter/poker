// Auto-generated lightweight TypeScript types for Phase 2 API and WS events

export interface Blinds {
  small: number;
  big: number;
  ante?: number;
}

export interface RoomCreate {
  name?: string;
  seat_count: number;
  game_type: string;
  blinds: Blinds;
  starting_stack: number;
}

export interface CreateRoomResponse {
  roomId: string;
}

export interface JoinRequest {
  display_name: string;
}

export interface JoinResponse {
  playerId: string;
}

export interface Player {
  id: string;
  display_name: string;
  seat_number: number;
  stack: number;
}

export interface Room {
  id: string;
  name?: string;
  seat_count: number;
  config?: any;
  players?: Player[];
}

export interface HandStartResponse {
  handId: string;
}

// WebSocket event types
export interface StateSyncEvent {
  type: 'state_sync';
  publicView: { roomId: string; playerCount?: number };
  personalView: Record<string, any>;
}

export interface HandStartEvent {
  type: 'hand:start';
  handId: string;
  playerCount?: number;
}

export interface DealHoleEvent {
  type: 'deal:hole';
  handId: string;
  cards: [string, string];
}

export interface ActionPostEvent {
  type: 'action:post';
  payload: { actionType: string; amount?: number | null; street?: string };
}

export interface ActionPostedEvent {
  type: 'action:posted';
  from: string;
  payload: Record<string, any>;
}

export interface ChatMessageEvent {
  type: 'chat:message';
  from: string;
  text: string;
  timestamp?: string;
}

export interface ErrorEvent {
  type: 'error';
  code: string;
  message: string;
}

export type WebSocketEvent =
  | StateSyncEvent
  | HandStartEvent
  | DealHoleEvent
  | ActionPostEvent
  | ActionPostedEvent
  | ChatMessageEvent
  | ErrorEvent;
