import { makeAutoObservable, runInAction } from 'mobx'
import { api } from '@/api/client'
import type { Room, Player, RoundResult, FinalStanding, GameType } from '@/types'
import { wsClient } from '@/api/websocket'

export type GameStatus = 'idle' | 'loading' | 'connected' | 'error'

class GameStore {
  room: Room | null = null
  playerId: number | null = null
  gameStatus: GameStatus = 'idle'
  error: string | null = null
  
  // Round results (shown after round ends)
  lastRoundResult: RoundResult | null = null
  
  // Final standings (shown after game ends)
  finalStandings: FinalStanding[] = []

  constructor() {
    makeAutoObservable(this)
  }

  get currentPlayer(): Player | null {
    if (!this.room || !this.playerId) return null
    return this.room.players.find(p => p.id === this.playerId) ?? null
  }

  get isHost(): boolean {
    return this.currentPlayer?.is_host ?? false
  }

  get canStartGame(): boolean {
    return (
      this.isHost &&
      this.room?.status === 'waiting' &&
      (this.room?.players.length ?? 0) >= 2
    )
  }

  get timeRemaining(): number {
    if (!this.room?.current_round?.started_at) return 0
    const startedAt = new Date(this.room.current_round.started_at).getTime()
    const elapsed = (Date.now() - startedAt) / 1000
    const remaining = Math.max(0, 30 - elapsed) // 30 seconds per round
    return Math.ceil(remaining)
  }

  get gameType(): GameType {
    return this.room?.game_type ?? api.getDefaultGameType()
  }

  async createRoom(playerName: string, gameType?: GameType): Promise<void> {
    this.setStatus('loading')
    this.error = null

    try {
      const response = await api.createRoom(playerName, gameType)
      runInAction(() => {
        this.room = response.room
        this.playerId = response.player_id
        this.setStatus('connected')
      })
      this.connectWebSocket()
    } catch (e) {
      runInAction(() => {
        this.error = e instanceof Error ? e.message : 'Failed to create room'
        this.setStatus('error')
      })
    }
  }

  async joinRoom(code: string, playerName: string, gameType?: GameType): Promise<void> {
    this.setStatus('loading')
    this.error = null

    try {
      const response = await api.joinRoom(code, playerName, gameType)
      runInAction(() => {
        this.room = response.room
        this.playerId = response.player_id
        this.setStatus('connected')
      })
      this.connectWebSocket()
    } catch (e) {
      runInAction(() => {
        this.error = e instanceof Error ? e.message : 'Failed to join room'
        this.setStatus('error')
      })
    }
  }

  async startGame(): Promise<void> {
    if (!this.room || !this.playerId) return

    try {
      const result = await api.startGame(this.room.code, this.playerId, this.room.game_type)
      if (result.room) {
        runInAction(() => {
          this.room = result.room
          this.lastRoundResult = null
        })
      }
      // Request updated state via WebSocket
      this.requestState()
    } catch (e) {
      runInAction(() => {
        this.error = e instanceof Error ? e.message : 'Failed to start game'
      })
    }
  }

  async submitGuess(guess: number): Promise<void> {
    if (!this.room || !this.playerId) return

    try {
      const result = await api.submitGuess(this.room.code, this.playerId, guess, this.room.game_type)
      if (result.room) {
        runInAction(() => {
          this.room = result.room
        })
      }
      // Request updated state via WebSocket
      this.requestState()
    } catch (e) {
      runInAction(() => {
        this.error = e instanceof Error ? e.message : 'Failed to submit guess'
      })
    }
  }

  /**
   * Execute a generic game action
   */
  async executeAction(action: Record<string, unknown>): Promise<void> {
    if (!this.room || !this.playerId) return

    try {
      const result = await api.executeAction(this.room.code, this.playerId, action, this.room.game_type)
      if (result.room) {
        runInAction(() => {
          this.room = result.room
        })
      }
      this.requestState()
    } catch (e) {
      runInAction(() => {
        this.error = e instanceof Error ? e.message : 'Action failed'
      })
    }
  }

  /**
   * Request current game state via WebSocket.
   * This is the preferred way to get state updates.
   */
  requestState(): void {
    wsClient.requestState()
  }

  private connectWebSocket(): void {
    if (!this.room || !this.playerId) return
    
    wsClient.connect(
      this.room.code, 
      this.playerId, 
      this.room.game_type,
      this.handleWSMessage.bind(this)
    )
  }

  private handleWSMessage(event: string, data: unknown): void {
    switch (event) {
      case 'room_state':
        // Main state update handler - used by GamesStorage broadcasts
        runInAction(() => {
          const d = data as { room: Room }
          if (d.room) {
            this.room = d.room
          }
        })
        break

      case 'player_joined':
        this.requestState()
        break

      case 'player_left':
        this.requestState()
        break

      case 'game_started':
        runInAction(() => {
          const d = data as { room: Room }
          if (d.room) {
            this.room = d.room
          }
          this.lastRoundResult = null
        })
        break

      case 'round_started':
        runInAction(() => {
          this.lastRoundResult = null
        })
        this.requestState()
        break

      case 'round_finished':
        runInAction(() => {
          this.lastRoundResult = data as RoundResult
        })
        this.requestState()
        break

      case 'game_finished':
        runInAction(() => {
          const d = data as { standings: FinalStanding[] }
          this.finalStandings = d.standings
          if (this.room) {
            this.room.status = 'finished'
          }
        })
        break

      case 'guess_submitted':
        this.requestState()
        break
    }
  }

  private setStatus(status: GameStatus): void {
    this.gameStatus = status
  }

  leaveRoom(): void {
    wsClient.disconnect()
    this.room = null
    this.playerId = null
    this.gameStatus = 'idle'
    this.error = null
    this.lastRoundResult = null
    this.finalStandings = []
  }
}

export const gameStore = new GameStore()
