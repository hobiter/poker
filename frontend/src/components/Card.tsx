import React from 'react'

export default function Card({ code, pulse = false }: { code: string; pulse?: boolean }) {
  return <span className={`card ${pulse ? 'pulse' : ''}`}>{code}</span>
}
