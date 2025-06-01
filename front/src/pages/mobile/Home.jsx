import * as React from 'react';
import HeaderBar from '../../components/HeaderBar.jsx';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import PlayerSetup from '../../components/mobile/PlayerSetup.jsx';

export default function MobileHome() {
    const [roomCode, setRoomCode] = React.useState('');
    const [playerName, setPlayerName] = React.useState('');
    const [avatarIndex, setAvatarIndex] = React.useState(0);

    function startGame() {
        // Placeholder for future logic
        console.log('start with', roomCode, playerName, avatarIndex);
    }

    return (
        <Box sx={{ width: '100%' }}>
            <HeaderBar />
            <Stack spacing={2} sx={{ mt: 10, width: '100%', maxWidth: 320, mx: 'auto' }}>
                <TextField
                    label="Room code"
                    value={roomCode}
                    onChange={(e) => setRoomCode(e.target.value)}
                    fullWidth
                />
                <PlayerSetup
                    name={playerName}
                    setName={setPlayerName}
                    avatarIndex={avatarIndex}
                    setAvatarIndex={setAvatarIndex}
                />
                <Button variant="contained" onClick={startGame} fullWidth>
                    Start
                </Button>
            </Stack>
        </Box>
    );
}
