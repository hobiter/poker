// Minimal WS / API types used by the frontend.

export type StateSync = {
  type: 'state_sync'
  publicView: { roomId: string; playerCount?: number }
  personalView: Record<string, unknown>
}

export type HandStart = {
  type: 'hand:start'
  handId: string
  playerCount?: number
}

export type DealHole = {
  type: 'deal:hole'
  handId: string
  cards: [string, string]
}

export type ActionPost = { type: 'action:post'; payload: { actionType: string; amount?: number | null; street?: string } }
export type ActionPosted = { type: 'action:posted'; from: string; payload: Record<string, unknown> }
export type ChatMessage = { type: 'chat:message'; from: string; text: string; timestamp?: string }
export type ErrorEvent = { type: 'error'; code: string; message: string }

export type CommunityUpdate = { type: 'community:update'; community: string[]; street?: string }
export type TurnChange = { type: 'turn:change'; next: string }

export type WSMessage = StateSync | HandStart | DealHole | ActionPost | ActionPosted | ChatMessage | ErrorEvent | CommunityUpdate | TurnChange | Record<string, unknown>
