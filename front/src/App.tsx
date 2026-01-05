import { observer } from 'mobx-react-lite'
import { gameStore } from '@/stores/GameStore'
import { HomePage } from '@/pages/HomePage'
import { LobbyPage } from '@/pages/LobbyPage'
import { GamePage } from '@/pages/GamePage'
import { ResultsPage } from '@/pages/ResultsPage'

const App = observer(() => {
  const { room } = gameStore

  // No room - show home page
  if (!room) {
    return <HomePage />
  }

  // Room exists, render based on status
  switch (room.status) {
    case 'waiting':
      return <LobbyPage />
    case 'playing':
      return <GamePage />
    case 'finished':
      return <ResultsPage />
    default:
      return <HomePage />
  }
})

export default App

