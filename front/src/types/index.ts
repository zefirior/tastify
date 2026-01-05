export type RoomStatus = 'waiting' | 'playing' | 'finished'
export type RoundStatus = 'active' | 'finished'

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

