import React, { useState } from 'react'

export default function BettingPanel({ onAction, allowedActions }: { onAction: (action: string, amount?: number) => void; allowedActions?: any[] }) {
  const [amount, setAmount] = useState<number | ''>('')

  const allowed = (name: string) => (allowedActions || []).some((a: any) => a.action === name)
  const find = (name: string) => (allowedActions || []).find((a: any) => a.action === name)

  return (
    <div className="betting-panel">
      <div style={{ marginBottom: 8 }}>
        <input type="number" placeholder="amount" value={amount as any} onChange={(e) => setAmount(e.target.value === '' ? '' : Number(e.target.value))} />
      </div>
      <div>
        <button onClick={() => onAction('fold')} disabled={!allowed('fold')}>Fold</button>
        <button onClick={() => onAction('check')} disabled={!allowed('check')}>Check</button>
        <button onClick={() => onAction('call', find('call')?.amount)} disabled={!allowed('call')}>Call{allowed('call') && find('call')?.amount ? ` (${find('call').amount})` : ''}</button>
        <button onClick={() => onAction('allin')} disabled={!allowed('allin')}>All-in</button>
        <button onClick={() => onAction('bet', amount === '' ? undefined : Number(amount))} disabled={!allowed('bet')}>Bet</button>
        <button onClick={() => onAction('raise', amount === '' ? undefined : Number(amount))} disabled={!allowed('raise')}>Raise</button>
      </div>
      {allowedActions && <div className="allowed">Allowed: {(allowedActions || []).map((a: any) => a.action).join(', ')}</div>}
    </div>
  )
}
