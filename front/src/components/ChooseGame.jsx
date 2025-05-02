import Client from '../lib/backend.js';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import * as React from 'react';
import { FormControl, InputLabel, OutlinedInput, Typography } from '@mui/material';
import { useNavigate } from 'react-router';

export default function ChooseGame(props) {
    const [playerName, setPlayerName] = React.useState('');
    const [roomCode, setRoomCode] = React.useState(props.roomCode || '');
    const navigate = useNavigate();

    function createRoom() {
        Client.createRoom().then((room) => {
            navigate(`/room/${room.code}`);
        });
    }

    function joinRoom() {
        Client.joinRoom(roomCode, playerName).then(() => {
            navigate(`/room/${roomCode}`);
        });
    }

    const isNotReadyToJoin = !playerName || !roomCode;

    return (
        <Box sx={{ width: '100%', minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={4}>
                {/* Create Game Card */}
                <Paper variant="elevation" color={'blue'} sx={{
                    p: 4,
                    width: 360,
                    height: 320,
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    transition: 'transform 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                        transform: 'scale(1.04)',
                    },
                }}>
                    <div style={{ width: '100%', textAlign: 'left' }}>
                        <Typography variant="h4" gutterBottom>
                            New Game
                        </Typography>
                        <Typography variant="body1" color="text.secondary" sx={{ mb: 3, fontSize: '1.2rem' }}>
                            {/* Replace this with your actual game description */}
                            Welcome to Tastify! Create a new game room and invite your friends to join. Enjoy a fun and interactive experience.
                        </Typography>
                    </div>
                    <Button
                        variant="outlined"
                        color="primary"
                        size="large"
                        onClick={createRoom}
                        sx={{ width: '100%', fontSize: '1.1rem', height: 48 }}
                    >
                        Create
                    </Button>
                </Paper>

                {/* Join Game Card */}
                <Paper variant="elevation" sx={{
                    p: 4,
                    width: 300,
                    height: 320,
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    transition: 'transform 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                        transform: 'scale(1.04)',
                    },
                }}>
                    <div style={{ width: '100%' }}>
                        <Typography variant="h4" gutterBottom>
                            Join Game
                        </Typography>
                        <FormControl fullWidth sx={{ mb: 2 }}>
                            <InputLabel htmlFor="join-room-player-name" sx={{ fontSize: '1.1rem' }}>Nick</InputLabel>
                            <OutlinedInput
                                id="join-room-player-name"
                                aria-label="Enter your nickname"
                                placeholder="Nick"
                                value={playerName}
                                onChange={(event) => setPlayerName(event.target.value)}
                                label="Nick"
                                sx={{ fontSize: '1.1rem', height: 48 }}
                            />
                        </FormControl>
                        <FormControl fullWidth sx={{ mb: 2 }}>
                            <InputLabel htmlFor="join-room-code" sx={{ fontSize: '1.1rem' }}>Room code</InputLabel>
                            <OutlinedInput
                                id="join-room-code"
                                aria-label="Enter room code to join"
                                placeholder="Room code"
                                value={roomCode}
                                onChange={(event) => setRoomCode(event.target.value)}
                                label="Room code"
                                sx={{ fontSize: '1.1rem', height: 48 }}
                            />
                        </FormControl>
                    </div>
                    <Button
                        variant="outlined"
                        color="primary"
                        size="large"
                        disabled={isNotReadyToJoin}
                        onClick={joinRoom}
                        sx={{ width: '100%', fontSize: '1.1rem', height: 48 }}
                    >
                        Join
                    </Button>
                </Paper>
            </Stack>
        </Box>
    );
}