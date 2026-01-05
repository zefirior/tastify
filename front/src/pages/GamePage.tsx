import { useState, useEffect } from 'react'
import { observer } from 'mobx-react-lite'
import { gameStore } from '@/stores/GameStore'

export const GamePage = observer(() => {
  const { room, currentPlayer, lastRoundResult } = gameStore
  const [guess, setGuess] = useState('')
  const [timeLeft, setTimeLeft] = useState(30)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Timer countdown
  useEffect(() => {
    if (!room?.current_round?.started_at) return

    const updateTimer = () => {
      const startedAt = new Date(room.current_round!.started_at).getTime()
      const elapsed = (Date.now() - startedAt) / 1000
      const remaining = Math.max(0, 30 - elapsed)
      setTimeLeft(Math.ceil(remaining))
    }

    updateTimer()
    const interval = setInterval(updateTimer, 100)
    return () => clearInterval(interval)
  }, [room?.current_round?.started_at])

  // Reset guess when new round starts
  useEffect(() => {
    setGuess('')
  }, [room?.current_round_number])

  if (!room || !currentPlayer) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const guessNum = parseInt(guess)
    if (isNaN(guessNum) || guessNum < 1 || guessNum > 100) return

    setIsSubmitting(true)
    await gameStore.submitGuess(guessNum)
    setIsSubmitting(false)
  }

  const hasGuessed = currentPlayer.current_guess !== null
  const isRoundActive = room.current_round?.status === 'active'

  // Calculate timer color based on time left
  const timerColor = timeLeft > 10 ? 'text-mint' : timeLeft > 5 ? 'text-amber' : 'text-coral'

  return (
    <div className="min-h-screen flex flex-col bg-void relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-neon/5 rounded-full blur-3xl" />
      </div>

      {/* Header */}
      <header className="relative z-10 p-4 flex justify-between items-center border-b border-smoke">
        <div className="flex items-center gap-4">
          <span className="text-2xl font-bold bg-gradient-to-r from-neon to-electric bg-clip-text text-transparent">
            Tastify
          </span>
          <span className="px-3 py-1 bg-slate rounded-lg text-ash text-sm font-mono">
            {room.code}
          </span>
        </div>
        <div className="text-right">
          <p className="text-ash text-sm">Round</p>
          <p className="text-2xl font-bold text-pearl">{room.current_round_number}/3</p>
        </div>
      </header>

      {/* Main content */}
      <main className="relative z-10 flex-1 flex flex-col items-center justify-center p-4">
        {/* Timer or Next Round indicator */}
        <div className="mb-8 animate-slide-up">
          {lastRoundResult ? (
            <>
              <div className="text-4xl font-bold text-electric text-center">
                Round Complete!
              </div>
              <p className="text-center text-ash mt-2">Next round starting soon...</p>
            </>
          ) : (
            <>
              <div className={`text-8xl font-bold font-mono ${timerColor} transition-colors`}>
                {timeLeft}
              </div>
              <p className="text-center text-ash mt-2">seconds remaining</p>
            </>
          )}
        </div>

        {/* Guess input */}
        {isRoundActive && !hasGuessed && (
          <form onSubmit={handleSubmit} className="w-full max-w-sm animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <div className="bg-obsidian/80 backdrop-blur-xl rounded-2xl p-6 border border-smoke">
              <label className="block text-center text-ash mb-4">
                Guess a number between 1 and 100
              </label>
              <input
                type="number"
                min={1}
                max={100}
                value={guess}
                onChange={(e) => setGuess(e.target.value)}
                placeholder="?"
                className="w-full px-4 py-4 bg-slate border border-smoke rounded-xl text-pearl text-center text-4xl font-mono focus:outline-none focus:border-neon transition-colors"
                autoFocus
              />
              <button
                type="submit"
                disabled={isSubmitting || !guess}
                className="w-full mt-4 py-4 px-6 bg-gradient-to-r from-neon to-electric text-void font-bold rounded-xl hover:opacity-90 transition-all disabled:opacity-50"
              >
                {isSubmitting ? 'Submitting...' : 'Lock In'}
              </button>
            </div>
          </form>
        )}

        {/* Waiting state after guess - only show if no round results yet */}
        {isRoundActive && hasGuessed && !lastRoundResult && (
          <div className="text-center animate-slide-up">
            <div className="bg-obsidian/80 backdrop-blur-xl rounded-2xl p-8 border border-smoke">
              <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br from-mint to-mint-bright flex items-center justify-center">
                <span className="text-3xl">✓</span>
              </div>
              <p className="text-pearl text-xl font-semibold">Guess submitted!</p>
              <p className="text-5xl font-mono font-bold text-electric mt-2">
                {currentPlayer.current_guess}
              </p>
              <p className="text-ash mt-4">Waiting for other players...</p>
            </div>
          </div>
        )}

        {/* Round results */}
        {lastRoundResult && (
          <div className="w-full max-w-md animate-slide-up">
            <div className="bg-obsidian/80 backdrop-blur-xl rounded-2xl p-6 border border-smoke">
              <div className="text-center mb-6">
                <p className="text-ash text-sm">The target was</p>
                <p className="text-5xl font-mono font-bold text-electric">
                  {lastRoundResult.target_number}
                </p>
              </div>

              <div className="space-y-3">
                {lastRoundResult.results.map((result, index) => (
                  <div
                    key={result.player_id}
                    className="flex items-center justify-between p-3 bg-slate/50 rounded-xl"
                  >
                    <div className="flex items-center gap-3">
                      <span className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                        index === 0 ? 'bg-amber text-void' :
                        index === 1 ? 'bg-silver text-void' :
                        index === 2 ? 'bg-coral-dim text-pearl' :
                        'bg-smoke text-ash'
                      }`}>
                        {index + 1}
                      </span>
                      <span className="text-pearl">{result.player_name}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-ash text-sm mr-3">
                        {result.guess !== null ? result.guess : '—'}
                      </span>
                      <span className="text-mint font-bold">+{result.points_earned}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Scoreboard footer */}
      <footer className="relative z-10 p-4 border-t border-smoke">
        <div className="flex justify-center gap-6 overflow-x-auto">
          {room.players
            .slice()
            .sort((a, b) => b.score - a.score)
            .map((player) => (
              <div
                key={player.id}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl ${
                  player.id === currentPlayer.id ? 'bg-neon/20 border border-neon/50' : 'bg-slate/50'
                }`}
              >
                <span className="text-pearl font-medium">{player.name}</span>
                <span className="text-electric font-bold">{player.score}</span>
                {player.current_guess !== null && isRoundActive && (
                  <span className="w-2 h-2 bg-mint rounded-full" title="Has guessed" />
                )}
              </div>
            ))}
        </div>
      </footer>
    </div>
  )
})

