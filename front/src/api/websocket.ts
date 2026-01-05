type MessageHandler = (event: string, data: unknown) => void

class WebSocketClient {
  private ws: WebSocket | null = null
  private roomCode: string | null = null
  private playerId: number | null = null
  private messageHandler: MessageHandler | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private pingInterval: number | null = null

  connect(roomCode: string, playerId: number, onMessage: MessageHandler): void {
    this.roomCode = roomCode
    this.playerId = playerId
    this.messageHandler = onMessage
    this.reconnectAttempts = 0
    this.doConnect()
  }

  private doConnect(): void {
    if (!this.roomCode || !this.playerId) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const url = `${protocol}//${host}/api/rooms/${this.roomCode}/ws?player_id=${this.playerId}`

    console.log('Connecting to WebSocket:', url)
    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      this.startPing()
      // Request initial state on connect
      this.requestState()
    }

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        console.log('WebSocket message:', message)
        if (this.messageHandler) {
          this.messageHandler(message.event, message.data)
        }
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }

    this.ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason)
      this.stopPing()
      this.attemptReconnect()
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnect attempts reached')
      return
    }

    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`)

    setTimeout(() => {
      if (this.roomCode && this.playerId) {
        this.doConnect()
      }
    }, delay)
  }

  private startPing(): void {
    this.pingInterval = window.setInterval(() => {
      this.send('ping', {})
    }, 30000)
  }

  private stopPing(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval)
      this.pingInterval = null
    }
  }

  send(event: string, data: unknown): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ event, data }))
    }
  }

  /**
   * Request current game state from server via WebSocket.
   * Server will respond with 'room_state' event.
   */
  requestState(): void {
    this.send('get_state', {})
  }

  disconnect(): void {
    this.stopPing()
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.roomCode = null
    this.playerId = null
    this.messageHandler = null
    this.reconnectAttempts = this.maxReconnectAttempts // Prevent reconnect
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

export const wsClient = new WebSocketClient()
