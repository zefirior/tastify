import { observer } from 'mobx-react-lite'
import { gameStore } from '@/stores/GameStore'

export const ResultsPage = observer(() => {
  const { room, finalStandings, currentPlayer } = gameStore

  if (!room) return null

  const handlePlayAgain = () => {
    gameStore.leaveRoom()
  }

  // Use finalStandings if available, otherwise sort players by score
  const standings = finalStandings.length > 0
    ? finalStandings
    : room.players
        .slice()
        .sort((a, b) => b.score - a.score)
        .map(p => ({ player_id: p.id, name: p.name, score: p.score }))

  const winner = standings[0]
  const isWinner = currentPlayer && winner?.player_id === currentPlayer.id

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-void relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-gradient-to-b from-amber/10 to-transparent rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 w-full max-w-lg">
        {/* Winner announcement */}
        <div className="text-center mb-8 animate-slide-up">
          <p className="text-ash text-lg mb-2">Game Over!</p>
          <h1 className="text-4xl font-bold text-pearl mb-2">
            {isWinner ? '🎉 You Won!' : `${winner?.name} Wins!`}
          </h1>
          <p className="text-electric text-2xl font-mono">{winner?.score} points</p>
        </div>

        {/* Trophy card for winner */}
        <div className="bg-obsidian/80 backdrop-blur-xl rounded-2xl p-8 border border-amber/30 shadow-2xl mb-6 animate-slide-up animate-pulse-glow" style={{ animationDelay: '0.1s' }}>
          <div className="flex items-center justify-center gap-4">
            <span className="text-6xl">🏆</span>
            <div>
              <p className="text-2xl font-bold text-pearl">{winner?.name}</p>
              <p className="text-amber">Champion</p>
            </div>
          </div>
        </div>

        {/* Full standings */}
        <div className="bg-obsidian/80 backdrop-blur-xl rounded-2xl p-6 border border-smoke shadow-2xl mb-6 animate-slide-up" style={{ animationDelay: '0.2s' }}>
          <h2 className="text-xl font-semibold text-pearl mb-4">Final Standings</h2>
          <div className="space-y-3">
            {standings.map((player, index) => (
              <div
                key={player.player_id}
                className={`flex items-center justify-between p-4 rounded-xl ${
                  player.player_id === currentPlayer?.id
                    ? 'bg-neon/20 border border-neon/50'
                    : 'bg-slate/50'
                }`}
              >
                <div className="flex items-center gap-4">
                  <span className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                    index === 0 ? 'bg-gradient-to-br from-amber to-amber/70 text-void' :
                    index === 1 ? 'bg-gradient-to-br from-silver to-silver/70 text-void' :
                    index === 2 ? 'bg-gradient-to-br from-coral to-coral-dim text-pearl' :
                    'bg-smoke text-ash'
                  }`}>
                    {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : index + 1}
                  </span>
                  <span className="text-pearl font-medium text-lg">{player.name}</span>
                </div>
                <span className="text-electric font-bold text-xl font-mono">
                  {player.score}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Action */}
        <button
          onClick={handlePlayAgain}
          className="w-full py-4 px-6 bg-gradient-to-r from-neon to-electric text-void font-bold rounded-xl hover:opacity-90 transition-all animate-slide-up"
          style={{ animationDelay: '0.3s' }}
        >
          Play Again
        </button>
      </div>
    </div>
  )
})

