export type RoomStatus = 'waiting' | 'playing' | 'finished'
export type RoundStatus = 'active' | 'finished'

// Available game types
export type GameType = 'guess_number' // Add more as they are implemented

export interface Player {
  id: number
  name: string
  score: number
  current_guess: number | null
  is_host: boolean
  connected_at: string
}

export interface GameRound {
  id: number
  round_number: number
  target_number: number | null
  status: RoundStatus
  started_at: string
  finished_at: string | null
}

export interface Room {
  id: number
  code: string
  game_type: GameType
  status: RoomStatus
  host_id: number | null
  current_round_number: number
  created_at: string
  updated_at: string
  players: Player[]
  current_round: GameRound | null
}

export interface CreateRoomResponse {
  room: Room
  player_id: number
}

export interface JoinRoomResponse {
  room: Room
  player_id: number
}

export interface ActionResponse {
  success: boolean
  message: string | null
  data: Record<string, unknown> | null
  room: Room | null
}

export interface RoundResultPlayer {
  player_id: number
  player_name: string
  guess: number | null
  distance: number | null
  points_earned: number
}

export interface RoundResult {
  round_number: number
  target_number: number
  results: RoundResultPlayer[]
}

export interface FinalStanding {
  player_id: number
  name: string
  score: number
}

// Game info from API
export interface GameAction {
  name: string
  description: string
  fields: {
    name: string
    type: string
    required: boolean
    min?: number
    max?: number
    description: string
  }[]
}

export interface GameInfo {
  game_type: GameType
  display_name: string
  description: string
  is_default: boolean
  actions: GameAction[]
}

export interface GamesInfoResponse {
  games: GameInfo[]
  default_game: GameType
}

// WebSocket event types
export type WSEventType =
  | 'room_state'
  | 'room_updated'
  | 'player_joined'
  | 'player_left'
  | 'game_started'
  | 'round_started'
  | 'round_finished'
  | 'game_finished'
  | 'guess_submitted'
  | 'error'
  | 'pong'

export interface WSMessage<T = unknown> {
  event: WSEventType
  data: T
}
