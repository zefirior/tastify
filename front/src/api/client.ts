import type { CreateRoomResponse, JoinRoomResponse, Room } from '@/types'

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

export const api = {
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
}

