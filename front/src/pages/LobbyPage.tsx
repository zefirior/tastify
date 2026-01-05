import { observer } from 'mobx-react-lite'
import { gameStore } from '@/stores/GameStore'

export const LobbyPage = observer(() => {
  const { room, isHost, canStartGame } = gameStore

  if (!room) return null

  const handleStart = () => {
    gameStore.startGame()
  }

  const handleLeave = () => {
    gameStore.leaveRoom()
  }

  const copyCode = () => {
    navigator.clipboard.writeText(room.code)
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-void relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/3 left-1/3 w-96 h-96 bg-neon/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/3 right-1/3 w-96 h-96 bg-electric/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      </div>

      <div className="relative z-10 w-full max-w-lg">
        {/* Room code card */}
        <div className="bg-obsidian/80 backdrop-blur-xl rounded-2xl p-8 border border-smoke shadow-2xl mb-6 animate-slide-up">
          <div className="text-center">
            <p className="text-ash text-sm mb-2">Room Code</p>
            <button
              onClick={copyCode}
              className="group relative"
            >
              <span className="text-5xl font-mono font-bold tracking-[0.3em] bg-gradient-to-r from-neon to-electric bg-clip-text text-transparent">
                {room.code}
              </span>
              <span className="absolute -right-8 top-1/2 -translate-y-1/2 text-ash opacity-0 group-hover:opacity-100 transition-opacity text-sm">
                📋
              </span>
            </button>
            <p className="text-ash text-sm mt-3">Share this code with your friends</p>
          </div>
        </div>

        {/* Players list */}
        <div className="bg-obsidian/80 backdrop-blur-xl rounded-2xl p-6 border border-smoke shadow-2xl mb-6 animate-slide-up" style={{ animationDelay: '0.1s' }}>
          <h2 className="text-xl font-semibold text-pearl mb-4">
            Players ({room.players.length})
          </h2>
          <div className="space-y-3">
            {room.players.map((player, index) => (
              <div
                key={player.id}
                className="flex items-center justify-between p-3 bg-slate/50 rounded-xl animate-fade-in"
                style={{ animationDelay: `${index * 0.05}s` }}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-neon to-electric flex items-center justify-center text-void font-bold">
                    {player.name.charAt(0).toUpperCase()}
                  </div>
                  <span className="text-pearl font-medium">{player.name}</span>
                </div>
                {player.is_host && (
                  <span className="px-3 py-1 bg-amber/20 text-amber text-xs font-semibold rounded-full">
                    HOST
                  </span>
                )}
              </div>
            ))}
          </div>

          {room.players.length < 2 && (
            <p className="text-ash text-sm mt-4 text-center">
              Waiting for more players to join...
            </p>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-4 animate-slide-up" style={{ animationDelay: '0.2s' }}>
          <button
            onClick={handleLeave}
            className="flex-1 py-4 px-6 bg-slate text-silver font-semibold rounded-xl border border-smoke hover:bg-smoke transition-all"
          >
            Leave
          </button>
          
          {isHost && (
            <button
              onClick={handleStart}
              disabled={!canStartGame}
              className="flex-1 py-4 px-6 bg-gradient-to-r from-mint to-mint-bright text-void font-semibold rounded-xl hover:opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Start Game
            </button>
          )}
        </div>

        {isHost && !canStartGame && room.players.length < 2 && (
          <p className="text-ash text-sm text-center mt-4">
            You need at least 2 players to start
          </p>
        )}
      </div>
    </div>
  )
})

