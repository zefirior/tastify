import { useState } from 'react'
import { observer } from 'mobx-react-lite'
import { gameStore } from '@/stores/GameStore'

export const HomePage = observer(() => {
  const [mode, setMode] = useState<'menu' | 'create' | 'join'>('menu')
  const [playerName, setPlayerName] = useState('')
  const [roomCode, setRoomCode] = useState('')

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!playerName.trim()) return
    await gameStore.createRoom(playerName.trim())
  }

  const handleJoin = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!playerName.trim() || !roomCode.trim()) return
    await gameStore.joinRoom(roomCode.trim(), playerName.trim())
  }

  const isLoading = gameStore.gameStatus === 'loading'

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-void relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-neon/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-electric/10 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-12 animate-slide-up">
          <h1 className="text-6xl font-bold mb-3">
            <span className="bg-gradient-to-r from-neon to-electric bg-clip-text text-transparent">
              Tastify
            </span>
          </h1>
          <p className="text-ash text-lg">Guess the number, beat your friends</p>
        </div>

        {/* Main content */}
        <div className="bg-obsidian/80 backdrop-blur-xl rounded-2xl p-8 border border-smoke shadow-2xl animate-slide-up" style={{ animationDelay: '0.1s' }}>
          {mode === 'menu' && (
            <div className="space-y-4">
              <button
                onClick={() => setMode('create')}
                className="w-full py-4 px-6 bg-gradient-to-r from-neon to-neon-bright text-white font-semibold rounded-xl hover:opacity-90 transition-all hover:scale-[1.02] active:scale-[0.98]"
              >
                Create Room
              </button>
              <button
                onClick={() => setMode('join')}
                className="w-full py-4 px-6 bg-slate text-pearl font-semibold rounded-xl border border-smoke hover:bg-smoke transition-all hover:scale-[1.02] active:scale-[0.98]"
              >
                Join Room
              </button>
            </div>
          )}

          {mode === 'create' && (
            <form onSubmit={handleCreate} className="space-y-6">
              <div>
                <label className="block text-sm text-ash mb-2">Your Name</label>
                <input
                  type="text"
                  value={playerName}
                  onChange={(e) => setPlayerName(e.target.value)}
                  placeholder="Enter your name"
                  maxLength={50}
                  className="w-full px-4 py-3 bg-slate border border-smoke rounded-xl text-pearl placeholder-ash focus:outline-none focus:border-neon transition-colors"
                  autoFocus
                />
              </div>

              {gameStore.error && (
                <p className="text-coral text-sm">{gameStore.error}</p>
              )}

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setMode('menu')}
                  disabled={isLoading}
                  className="flex-1 py-3 px-4 bg-slate text-silver rounded-xl hover:bg-smoke transition-colors disabled:opacity-50"
                >
                  Back
                </button>
                <button
                  type="submit"
                  disabled={isLoading || !playerName.trim()}
                  className="flex-1 py-3 px-4 bg-gradient-to-r from-neon to-neon-bright text-white font-semibold rounded-xl hover:opacity-90 transition-all disabled:opacity-50"
                >
                  {isLoading ? 'Creating...' : 'Create'}
                </button>
              </div>
            </form>
          )}

          {mode === 'join' && (
            <form onSubmit={handleJoin} className="space-y-6">
              <div>
                <label className="block text-sm text-ash mb-2">Your Name</label>
                <input
                  type="text"
                  value={playerName}
                  onChange={(e) => setPlayerName(e.target.value)}
                  placeholder="Enter your name"
                  maxLength={50}
                  className="w-full px-4 py-3 bg-slate border border-smoke rounded-xl text-pearl placeholder-ash focus:outline-none focus:border-neon transition-colors"
                  autoFocus
                />
              </div>

              <div>
                <label className="block text-sm text-ash mb-2">Room Code</label>
                <input
                  type="text"
                  value={roomCode}
                  onChange={(e) => setRoomCode(e.target.value.toUpperCase())}
                  placeholder="ABCDEF"
                  maxLength={6}
                  className="w-full px-4 py-3 bg-slate border border-smoke rounded-xl text-pearl placeholder-ash focus:outline-none focus:border-neon transition-colors font-mono text-center text-2xl tracking-widest uppercase"
                />
              </div>

              {gameStore.error && (
                <p className="text-coral text-sm">{gameStore.error}</p>
              )}

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setMode('menu')}
                  disabled={isLoading}
                  className="flex-1 py-3 px-4 bg-slate text-silver rounded-xl hover:bg-smoke transition-colors disabled:opacity-50"
                >
                  Back
                </button>
                <button
                  type="submit"
                  disabled={isLoading || !playerName.trim() || roomCode.length !== 6}
                  className="flex-1 py-3 px-4 bg-gradient-to-r from-electric to-electric-dim text-void font-semibold rounded-xl hover:opacity-90 transition-all disabled:opacity-50"
                >
                  {isLoading ? 'Joining...' : 'Join'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  )
})

