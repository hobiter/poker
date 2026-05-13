import React, { useState, useRef } from 'react'
import { createRoom, joinRoom, startHand, getRoom, forceTimeout } from './openapiClient'
import { WSMessage } from './types'
import SeatLayout from './components/SeatLayout'
import BettingPanel from './components/BettingPanel'

function App() {
  // Use Vite env var if provided at build time; otherwise default to same origin
  const defaultServerUrl = (import.meta.env.VITE_SERVER_URL as string) ?? (typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.host}` : 'http://localhost:8000')
  const [serverUrl, setServerUrl] = useState(defaultServerUrl)
  const [roomId, setRoomId] = useState('')
  const [clientId, setClientId] = useState('')
  const [messages, setMessages] = useState<string[]>([])
  const wsRef = useRef<WebSocket | null>(null)
  const [players, setPlayers] = useState<any[]>([])
  const [personalHoleCards, setPersonalHoleCards] = useState<Record<string, string[]>>({})
  const [community, setCommunity] = useState<string[]>([])
  const [currentTurn, setCurrentTurn] = useState<string | null>(null)
  const [street, setStreet] = useState<string | null>(null)
  const [allowedActions, setAllowedActions] = useState<any[] | null>(null)
  const [dealPulse, setDealPulse] = useState(false)
  const [communityPulse, setCommunityPulse] = useState(false)

  function log(msg: string) {
    setMessages(prev => [...prev, msg])
  }

  async function handleCreateRoom() {
    try {
      const res = await createRoom(serverUrl)
      // server returns { roomId }
      const rid = res.roomId || res.id || ''
      setRoomId(rid)
      log('Room created: ' + JSON.stringify(res))
    } catch (e) {
      log('Create room error: ' + String(e))
    }
  }

  async function handleJoinRoom() {
    if (!roomId) { log('Set room id'); return }
    try {
      const res = await joinRoom(serverUrl, roomId, clientId || undefined)
      // server returns { playerId }
      const pid = res.playerId || res.id || clientId
      setClientId(pid)
      log('Joined room: ' + JSON.stringify(res))
      // refresh room info
      const room = await getRoom(serverUrl, roomId)
      setPlayers(room.players || [])
    } catch (e) {
      log('Join error: ' + String(e))
    }
  }

  async function fetchRoom() {
    if (!roomId) return
    try {
      const room = await getRoom(serverUrl, roomId)
      setPlayers(room.players || [])
    } catch (e) {
      log('Fetch room error: ' + String(e))
    }
  }

  function wsConnect() {
    if (!roomId || !clientId) { log('Need roomId and clientId'); return }
    const wsProtocol = serverUrl.startsWith('https') ? 'wss' : 'ws'
    const base = serverUrl.replace(/^https?:\/\//, '')
    const wsUrl = `${wsProtocol}://${base}/ws/${roomId}/${clientId}`
    log('Connecting to ' + wsUrl)
    const ws = new WebSocket(wsUrl)
    ws.onopen = () => {
      log('WS open')
      // refresh room state on connect
      fetchRoom()
    }
    ws.onmessage = (e) => {
      log('WS msg: ' + e.data)
      try {
        const msg = JSON.parse(e.data) as WSMessage
        if (msg.type === 'deal:hole') {
          // this message is personal — store the cards for this client
          // @ts-ignore
          setPersonalHoleCards(prev => ({ ...prev, [clientId]: msg.cards }))
          // pulse deal animation briefly
          setDealPulse(true)
          setTimeout(() => setDealPulse(false), 700)
        } else if (msg.type === 'hand:start') {
          setCommunity([])
          setPersonalHoleCards({})
          setCurrentTurn(null)
          setStreet(null)
        } else if ((msg as any).type === 'community:update') {
          const m: any = msg
          setCommunity(m.community || [])
          setStreet(m.street || null)
          setCommunityPulse(true)
          setTimeout(() => setCommunityPulse(false), 700)
        } else if ((msg as any).type === 'turn:change') {
          const m: any = msg
          setCurrentTurn(m.next || null)
          // if it's our turn, fetch legal actions
          if (m.next === clientId) {
            ;(async () => {
              try {
                const la = await (await import('./openapiClient')).getLegalActions(serverUrl, roomId, clientId)
                setAllowedActions(la.actions || la)
              } catch (e) {
                log('legal actions fetch error: ' + String(e))
                setAllowedActions(null)
              }
            })()
          } else {
            setAllowedActions(null)
          }
        }
      } catch (err) {
        // ignore parse error
      }
    }
    ws.onclose = () => log('WS closed')
    ws.onerror = (e) => log('WS error')
    wsRef.current = ws
  }

  async function handleStartHand() {
    if (!roomId) { log('Set room id'); return }
    try {
      const res = await startHand(serverUrl, roomId)
      log('Start hand: ' + JSON.stringify(res))
    } catch (e) {
      log('Start hand error: ' + String(e))
    }
  }

  function sendAction(action: string, amount?: number) {
    const ws = wsRef.current
    if (!ws || ws.readyState !== WebSocket.OPEN) { log('WS not open'); return }
    const payload: any = { actionType: action }
    if (amount !== undefined) payload.amount = amount
    ws.send(JSON.stringify({ type: 'action:post', payload }))
    log('Sent action: ' + action + (amount ? ` ${amount}` : ''))
  }

  return (
    <div style={{ padding: 16, fontFamily: 'sans-serif' }}>
      <h1>Poker MVP Frontend</h1>
      <div style={{ marginBottom: 8 }}>
        <label>Server URL: </label>
        <input value={serverUrl} onChange={(e) => setServerUrl(e.target.value)} style={{ width: 400 }} />
      </div>
      <div style={{ marginBottom: 8 }}>
        <button onClick={handleCreateRoom}>Create Room</button>
        <button onClick={handleJoinRoom}>Join Room</button>
        <button onClick={wsConnect}>Connect WS</button>
        <button onClick={handleStartHand}>Start Hand</button>
      </div>
      <div style={{ marginBottom: 8 }}>
        <label>Room ID:</label>
        <input value={roomId} onChange={(e) => setRoomId(e.target.value)} />
        <label style={{ marginLeft: 8 }}>Client ID:</label>
        <input value={clientId} onChange={(e) => setClientId(e.target.value)} />
      </div>
      <div style={{ marginTop: 12 }}>
        <button onClick={() => sendAction('fold')}>Fold</button>
        <button onClick={() => sendAction('call')}>Call</button>
        <button onClick={() => sendAction('check')}>Check</button>
        <button onClick={() => sendAction('allin')}>All-in</button>
        <button onClick={() => fetchRoom()} style={{ marginLeft: 12 }}>Refresh Room</button>
        <button onClick={async () => { if (roomId) { const r = await forceTimeout(serverUrl, roomId); log('force_timeout: ' + JSON.stringify(r)) } }} style={{ marginLeft: 8 }}>Force Timeout (test)</button>
      </div>

      <h2>Room</h2>
      <div style={{ border: '1px solid #eee', padding: 8, marginBottom: 12 }}>
        <div><strong>Room:</strong> {roomId || '-'}</div>
        <div><strong>Players:</strong></div>
        <ul>
          {players.map((p: any) => (
            <li key={p.id}>{p.display_name || p.id} — stack: {p.stack}</li>
          ))}
        </ul>
        <div><strong>Your cards:</strong> {(personalHoleCards[clientId] || []).join(', ') || '-'}</div>
        <div><strong>Community ({street || '-'})</strong>: {community.join(', ') || '-'}</div>
        <div><strong>Current turn:</strong> {currentTurn || '-'}</div>
      </div>

      <SeatLayout players={players} myClientId={clientId} personalHoleCards={personalHoleCards} currentTurn={currentTurn} dealPulse={dealPulse} />

      <div className={`community ${communityPulse ? 'reveal' : ''}`}>
        <div><strong>Board:</strong> {community.map((c, i) => <span key={i} className="card">{c}</span>)}</div>
      </div>

      <BettingPanel onAction={sendAction} allowedActions={allowedActions || []} />

      <h2>Messages</h2>
      <div style={{ whiteSpace: 'pre-wrap', border: '1px solid #ddd', padding: 8, height: 220, overflow: 'auto' }}>
        {messages.map((m, i) => <div key={i}>{m}</div>)}
      </div>
    </div>
  )
}

export default App
