/**
 * WebSocket Service for Real-time Updates
 * Handles real-time negotiation events, notifications, and live data streaming
 */

import { EventEmitter } from 'events'

export interface WebSocketConfig {
  url: string
  reconnectInterval?: number
  maxReconnectAttempts?: number
  heartbeatInterval?: number
}

export interface WebSocketMessage {
  type: string
  payload: any
  timestamp: string
  id?: string
}

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error'

export type EventType = 
  | 'negotiation.started'
  | 'negotiation.offer_received'
  | 'negotiation.counter_offer'
  | 'negotiation.round_complete'
  | 'negotiation.completed'
  | 'negotiation.failed'
  | 'approval.required'
  | 'approval.granted'
  | 'approval.rejected'
  | 'contract.generated'
  | 'contract.signed'
  | 'vendor.response'
  | 'ai.reasoning'
  | 'system.notification'

class WebSocketService extends EventEmitter {
  private ws: WebSocket | null = null
  private config: WebSocketConfig
  private reconnectAttempts = 0
  private reconnectTimer: NodeJS.Timeout | null = null
  private heartbeatTimer: NodeJS.Timeout | null = null
  private messageQueue: WebSocketMessage[] = []
  private status: ConnectionStatus = 'disconnected'
  private subscriptions: Map<string, Set<(data: any) => void>> = new Map()

  constructor(config: WebSocketConfig) {
    super()
    this.config = {
      reconnectInterval: 5000,
      maxReconnectAttempts: 10,
      heartbeatInterval: 30000,
      ...config,
    }
  }

  /**
   * Connect to WebSocket server
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve()
        return
      }

      this.status = 'connecting'
      this.emit('status', this.status)

      try {
        this.ws = new WebSocket(this.config.url)

        this.ws.onopen = () => {
          console.log('WebSocket connected')
          this.status = 'connected'
          this.emit('status', this.status)
          this.reconnectAttempts = 0
          
          // Start heartbeat
          this.startHeartbeat()
          
          // Process queued messages
          this.processMessageQueue()
          
          // Emit connected event
          this.emit('connected')
          
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          this.status = 'error'
          this.emit('status', this.status)
          this.emit('error', error)
          reject(error)
        }

        this.ws.onclose = () => {
          console.log('WebSocket disconnected')
          this.status = 'disconnected'
          this.emit('status', this.status)
          this.emit('disconnected')
          
          // Stop heartbeat
          this.stopHeartbeat()
          
          // Attempt reconnection
          this.scheduleReconnect()
        }
      } catch (error) {
        console.error('Failed to create WebSocket:', error)
        this.status = 'error'
        this.emit('status', this.status)
        reject(error)
      }
    })
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    this.stopHeartbeat()
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    
    this.status = 'disconnected'
    this.emit('status', this.status)
  }

  /**
   * Send message to server
   */
  send(type: string, payload: any): void {
    const message: WebSocketMessage = {
      type,
      payload,
      timestamp: new Date().toISOString(),
      id: this.generateMessageId(),
    }

    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      // Queue message if not connected
      this.messageQueue.push(message)
    }
  }

  /**
   * Subscribe to specific event type
   */
  subscribe(eventType: EventType, callback: (data: any) => void): () => void {
    if (!this.subscriptions.has(eventType)) {
      this.subscriptions.set(eventType, new Set())
    }
    
    this.subscriptions.get(eventType)!.add(callback)
    
    // Return unsubscribe function
    return () => {
      const callbacks = this.subscriptions.get(eventType)
      if (callbacks) {
        callbacks.delete(callback)
        if (callbacks.size === 0) {
          this.subscriptions.delete(eventType)
        }
      }
    }
  }

  /**
   * Subscribe to negotiation updates for a specific request
   */
  subscribeToNegotiation(requestId: string, callback: (data: any) => void): () => void {
    const channel = `negotiation.${requestId}`
    this.send('subscribe', { channel })
    
    const handler = (message: WebSocketMessage) => {
      if (message.payload?.requestId === requestId) {
        callback(message.payload)
      }
    }
    
    this.on('message', handler)
    
    return () => {
      this.send('unsubscribe', { channel })
      this.off('message', handler)
    }
  }

  /**
   * Get connection status
   */
  getStatus(): ConnectionStatus {
    return this.status
  }

  /**
   * Handle incoming message
   */
  private handleMessage(message: WebSocketMessage): void {
    // Emit raw message event
    this.emit('message', message)
    
    // Handle specific message types
    switch (message.type) {
      case 'pong':
        // Heartbeat response
        break
        
      case 'error':
        console.error('Server error:', message.payload)
        this.emit('server-error', message.payload)
        break
        
      default:
        // Emit typed events
        if (this.isEventType(message.type)) {
          const callbacks = this.subscriptions.get(message.type as EventType)
          if (callbacks) {
            callbacks.forEach(callback => callback(message.payload))
          }
        }
        
        // Emit generic typed event
        this.emit(message.type, message.payload)
        break
    }
  }

  /**
   * Check if string is a valid EventType
   */
  private isEventType(type: string): type is EventType {
    const validTypes: EventType[] = [
      'negotiation.started',
      'negotiation.offer_received',
      'negotiation.counter_offer',
      'negotiation.round_complete',
      'negotiation.completed',
      'negotiation.failed',
      'approval.required',
      'approval.granted',
      'approval.rejected',
      'contract.generated',
      'contract.signed',
      'vendor.response',
      'ai.reasoning',
      'system.notification',
    ]
    return validTypes.includes(type as EventType)
  }

  /**
   * Start heartbeat to keep connection alive
   */
  private startHeartbeat(): void {
    this.stopHeartbeat()
    
    this.heartbeatTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send('ping', {})
      }
    }, this.config.heartbeatInterval)
  }

  /**
   * Stop heartbeat
   */
  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  /**
   * Schedule reconnection attempt
   */
  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= (this.config.maxReconnectAttempts || 10)) {
      console.error('Max reconnection attempts reached')
      this.emit('max-reconnect-attempts')
      return
    }

    this.reconnectAttempts++
    const delay = this.config.reconnectInterval || 5000
    
    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`)
    
    this.reconnectTimer = setTimeout(() => {
      this.connect().catch(error => {
        console.error('Reconnection failed:', error)
      })
    }, delay)
  }

  /**
   * Process queued messages
   */
  private processMessageQueue(): void {
    while (this.messageQueue.length > 0 && this.ws?.readyState === WebSocket.OPEN) {
      const message = this.messageQueue.shift()
      if (message) {
        this.ws.send(JSON.stringify(message))
      }
    }
  }

  /**
   * Generate unique message ID
   */
  private generateMessageId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }
}

// Singleton instance
let wsInstance: WebSocketService | null = null

/**
 * Get or create WebSocket service instance
 */
export function getWebSocketService(config?: WebSocketConfig): WebSocketService {
  if (!wsInstance && config) {
    wsInstance = new WebSocketService(config)
  }
  
  if (!wsInstance) {
    throw new Error('WebSocket service not initialized. Please provide config.')
  }
  
  return wsInstance
}

/**
 * React Hook for WebSocket connection
 */
import { useEffect, useState, useCallback, useRef } from 'react'

export interface UseWebSocketOptions {
  autoConnect?: boolean
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: any) => void
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const [status, setStatus] = useState<ConnectionStatus>('disconnected')
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocketService | null>(null)

  useEffect(() => {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'
    
    try {
      wsRef.current = getWebSocketService({ url: wsUrl })
    } catch {
      wsRef.current = new WebSocketService({ url: wsUrl })
    }

    const ws = wsRef.current

    // Status listener
    const handleStatus = (newStatus: ConnectionStatus) => {
      setStatus(newStatus)
      setIsConnected(newStatus === 'connected')
    }

    // Event listeners
    const handleConnect = () => {
      options.onConnect?.()
    }

    const handleDisconnect = () => {
      options.onDisconnect?.()
    }

    const handleError = (error: any) => {
      options.onError?.(error)
    }

    ws.on('status', handleStatus)
    ws.on('connected', handleConnect)
    ws.on('disconnected', handleDisconnect)
    ws.on('error', handleError)

    // Auto-connect if enabled
    if (options.autoConnect !== false) {
      ws.connect().catch(console.error)
    }

    return () => {
      ws.off('status', handleStatus)
      ws.off('connected', handleConnect)
      ws.off('disconnected', handleDisconnect)
      ws.off('error', handleError)
    }
  }, [])

  const connect = useCallback(() => {
    return wsRef.current?.connect()
  }, [])

  const disconnect = useCallback(() => {
    wsRef.current?.disconnect()
  }, [])

  const send = useCallback((type: string, payload: any) => {
    wsRef.current?.send(type, payload)
  }, [])

  const subscribe = useCallback((eventType: EventType, callback: (data: any) => void) => {
    return wsRef.current?.subscribe(eventType, callback) || (() => {})
  }, [])

  const subscribeToNegotiation = useCallback((requestId: string, callback: (data: any) => void) => {
    return wsRef.current?.subscribeToNegotiation(requestId, callback) || (() => {})
  }, [])

  return {
    status,
    isConnected,
    connect,
    disconnect,
    send,
    subscribe,
    subscribeToNegotiation,
  }
}

/**
 * React Hook for negotiation updates
 */
export function useNegotiationUpdates(requestId: string | null) {
  const [messages, setMessages] = useState<any[]>([])
  const [currentRound, setCurrentRound] = useState(0)
  const [status, setStatus] = useState<'active' | 'completed' | 'failed'>('active')
  const { subscribeToNegotiation } = useWebSocket()

  useEffect(() => {
    if (!requestId) return

    const unsubscribe = subscribeToNegotiation(requestId, (data) => {
      switch (data.type) {
        case 'offer_received':
        case 'counter_offer':
          setMessages(prev => [...prev, data.message])
          break
        case 'round_complete':
          setCurrentRound(data.round)
          break
        case 'negotiation_complete':
          setStatus('completed')
          break
        case 'negotiation_failed':
          setStatus('failed')
          break
      }
    })

    return unsubscribe
  }, [requestId, subscribeToNegotiation])

  return {
    messages,
    currentRound,
    status,
  }
}
