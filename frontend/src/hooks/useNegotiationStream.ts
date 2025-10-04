import { useEffect, useRef, useState } from 'react'
import { api } from '../services/api'

export interface NegotiationEvent {
  type: string
  timestamp: string
  data: {
    round_number?: number
    actor?: string
    offer?: {
      unit_price: number
      term_months: number
      payment_terms: string
    }
    strategy?: string
    rationale?: string[]
    utility?: number
    tco?: number
    message?: string
  }
}

export interface NegotiationStreamState {
  connected: boolean
  events: NegotiationEvent[]
  isNegotiating: boolean
  error: string | null
}

export function useNegotiationStream(sessionId: string | null) {
  const [state, setState] = useState<NegotiationStreamState>({
    connected: false,
    events: [],
    isNegotiating: false,
    error: null,
  })

  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    if (!sessionId) return

    // Create WebSocket connection
    const ws = api.createNegotiationWebSocket(sessionId)
    wsRef.current = ws

    ws.onopen = () => {
      setState((prev) => ({ ...prev, connected: true, error: null }))
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as NegotiationEvent

        setState((prev) => {
          const newEvent: NegotiationEvent = {
            type: data.type,
            timestamp: data.timestamp || new Date().toISOString(),
            data: data.data || {},
          }

          return {
            ...prev,
            events: [...prev.events, newEvent],
            isNegotiating: data.type !== 'completed' && data.type !== 'error',
          }
        })
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setState((prev) => ({
        ...prev,
        connected: false,
        error: 'WebSocket connection error',
      }))
    }

    ws.onclose = () => {
      setState((prev) => ({
        ...prev,
        connected: false,
        isNegotiating: false,
      }))
    }

    // Cleanup on unmount
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close()
      }
    }
  }, [sessionId])

  const clearEvents = () => {
    setState((prev) => ({ ...prev, events: [] }))
  }

  return {
    ...state,
    clearEvents,
  }
}
