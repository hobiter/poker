// Lightweight hand-written client generated from OpenAPI (phase-2 api_spec.yaml)
// Exposes the endpoints used by the frontend UI.

export async function createRoom(serverUrl: string, opts?: { name?: string; seat_count?: number; game_type?: string; blinds?: { small: number; big: number }; starting_stack?: number }) {
  const payload = {
    name: opts?.name ?? 'Room',
    seat_count: opts?.seat_count ?? 6,
    game_type: opts?.game_type ?? 'texas_holdem',
    blinds: opts?.blinds ?? { small: 5, big: 10 },
    starting_stack: opts?.starting_stack ?? 2000,
  }
  const res = await fetch(`${serverUrl}/rooms`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
  return res.json()
}

export async function joinRoom(serverUrl: string, roomId: string, displayName?: string) {
  const body = { display_name: displayName ?? 'web' }
  const res = await fetch(`${serverUrl}/rooms/${roomId}/join`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
  return res.json()
}

export async function getRoom(serverUrl: string, roomId: string) {
  const res = await fetch(`${serverUrl}/rooms/${roomId}`)
  return res.json()
}

export async function startHand(serverUrl: string, roomId: string) {
  const res = await fetch(`${serverUrl}/rooms/${roomId}/start_hand`, { method: 'POST', headers: { 'Content-Type': 'application/json' } })
  return res.json()
}

export async function forceTimeout(serverUrl: string, roomId: string) {
  const res = await fetch(`${serverUrl}/rooms/${roomId}/force_timeout`, { method: 'POST' })
  return res.json()
}

export async function getLegalActions(serverUrl: string, roomId: string, playerId: string) {
  const res = await fetch(`${serverUrl}/rooms/${roomId}/session/${playerId}/legal_actions`)
  return res.json()
}
