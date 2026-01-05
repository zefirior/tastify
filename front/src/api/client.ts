import type { 
  CreateRoomResponse, 
  JoinRoomResponse, 
  Room, 
  ActionResponse,
  GamesInfoResponse,
  GameType 
} from '@/types'

const API_BASE = '/api'

class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new ApiError(response.status, data.detail || 'An error occurred')
  }
  return response.json()
}

// Default game type - can be fetched from API
let defaultGameType: GameType = 'guess_number'

export const api = {
  /**
   * Set the default game type (called after fetching games info)
   */
  setDefaultGameType(gameType: GameType) {
    defaultGameType = gameType
  },

  /**
   * Get the current default game type
   */
  getDefaultGameType(): GameType {
    return defaultGameType
  },

  /**
   * Get list of available games
   */
  async getGamesInfo(): Promise<GamesInfoResponse> {
    const response = await fetch(`${API_BASE}/games`)
    const result = await handleResponse<GamesInfoResponse>(response)
    // Update default game type
    if (result.default_game) {
      defaultGameType = result.default_game
    }
    return result
  },

  /**
   * Create a new room for the specified game type
   */
  async createRoom(playerName: string, gameType?: GameType): Promise<CreateRoomResponse> {
    const game = gameType || defaultGameType
    const response = await fetch(`${API_BASE}/games/${game}/rooms`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_name: playerName }),
    })
    return handleResponse<CreateRoomResponse>(response)
  },

  /**
   * Join an existing room
   */
  async joinRoom(code: string, playerName: string, gameType?: GameType): Promise<JoinRoomResponse> {
    const game = gameType || defaultGameType
    const response = await fetch(`${API_BASE}/games/${game}/rooms/${code.toUpperCase()}/join`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_name: playerName }),
    })
    return handleResponse<JoinRoomResponse>(response)
  },

  /**
   * Get room state
   */
  async getRoom(code: string, gameType?: GameType): Promise<Room> {
    const game = gameType || defaultGameType
    const response = await fetch(`${API_BASE}/games/${game}/rooms/${code.toUpperCase()}`)
    return handleResponse<Room>(response)
  },

  /**
   * Execute a game action (start game, submit guess, etc.)
   */
  async executeAction(
    code: string, 
    playerId: number, 
    action: Record<string, unknown>,
    gameType?: GameType
  ): Promise<ActionResponse> {
    const game = gameType || defaultGameType
    const response = await fetch(
      `${API_BASE}/games/${game}/rooms/${code.toUpperCase()}/actions?player_id=${playerId}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(action),
      }
    )
    return handleResponse<ActionResponse>(response)
  },

  /**
   * Start the game (convenience method)
   */
  async startGame(code: string, playerId: number, gameType?: GameType): Promise<ActionResponse> {
    return this.executeAction(code, playerId, { action: 'start_game' }, gameType)
  },

  /**
   * Submit a guess (convenience method for guess_number game)
   */
  async submitGuess(code: string, playerId: number, guess: number, gameType?: GameType): Promise<ActionResponse> {
    return this.executeAction(code, playerId, { action: 'submit_guess', guess }, gameType)
  },

  // Legacy API methods (kept for backward compatibility)
  legacy: {
    async createRoom(playerName: string): Promise<CreateRoomResponse> {
      const response = await fetch(`${API_BASE}/rooms`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ player_name: playerName }),
      })
      return handleResponse<CreateRoomResponse>(response)
    },

    async joinRoom(code: string, playerName: string): Promise<JoinRoomResponse> {
      const response = await fetch(`${API_BASE}/rooms/${code.toUpperCase()}/join`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ player_name: playerName }),
      })
      return handleResponse<JoinRoomResponse>(response)
    },

    async getRoom(code: string): Promise<Room> {
      const response = await fetch(`${API_BASE}/rooms/${code.toUpperCase()}`)
      return handleResponse<Room>(response)
    },

    async startGame(code: string, playerId: number): Promise<Room> {
      const response = await fetch(
        `${API_BASE}/rooms/${code.toUpperCase()}/start?player_id=${playerId}`,
        { method: 'POST' }
      )
      return handleResponse<Room>(response)
    },

    async submitGuess(code: string, playerId: number, guess: number): Promise<Room> {
      const response = await fetch(`${API_BASE}/rooms/${code.toUpperCase()}/guess`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ player_id: playerId, guess }),
      })
      return handleResponse<Room>(response)
    },
  },
}
