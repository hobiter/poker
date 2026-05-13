import React from 'react'
import Card from './Card'

type Player = { id: string; display_name?: string; seat_number?: number; stack?: number }

export default function SeatLayout({ players, seatCount = 6, myClientId, personalHoleCards, currentTurn, dealPulse = false }: {
  players: Player[]
  seatCount?: number
  myClientId?: string
  personalHoleCards?: Record<string, string[]>
  currentTurn?: string | null
  dealPulse?: boolean
}) {
  const seats = Array.from({ length: seatCount }, (_, i) => i + 1)
  const bySeat: Record<number, Player | undefined> = {}
  for (const p of players) {
    if (p.seat_number) bySeat[p.seat_number] = p
  }

  return (
    <div className="seat-grid">
      {seats.map((s) => {
        const p = bySeat[s]
        const isTurn = p && currentTurn === p.id
        const isMe = p && myClientId === p.id
        const myCards = isMe && personalHoleCards && personalHoleCards[myClientId || '']
        return (
          <div key={s} className={`seat ${isTurn ? 'turn' : ''}`}>
            <div className="seat-number">Seat {s}</div>
            {p ? (
              <div>
                <div className="player-name">{p.display_name || p.id}</div>
                <div className="player-stack">{p.stack}</div>
                <div className="player-cards">
                  {myCards ? myCards.map((c, i) => <Card key={i} code={c} />) : (isMe ? '-' : '')}
                  {isMe && dealPulse && <span className="deal-indicator"> ✨</span>}
                </div>
              </div>
            ) : (
              <div className="empty">(empty)</div>
            )}
          </div>
        )
      })}
    </div>
  )
}
