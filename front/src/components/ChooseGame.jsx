import Client from '../lib/backend.js';
import Box from '@mui/material/Box';
import InputLabel from '@mui/material/InputLabel';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import * as React from 'react';
import {FormControl, OutlinedInput} from '@mui/material';
import {useNavigate} from 'react-router';

export default function ChooseGame(props) {
    const [playerName, setPlayerName] = React.useState('');
    const [roomCode, setRoomCode] = React.useState(props.roomCode || '');
    const navigate = useNavigate();


    function createRoom() {
        console.log('create room');
        Client.createRoom().then((room) => {
            console.log('created room', room);
            navigate(`/room/${room.code}`);
        });
    }

    return (
        <>
            <h1>{'Choose your game'}</h1>
            <Box
                component="form"
                sx={{ '& > :not(style)': { m: 1 } }}
                noValidate
                autoComplete="off"
            >
                <Stack direction="row" spacing={1} useFlexGap>
                    <FormControl>
                        <InputLabel
                            className={'input-label'}
                            htmlFor="join-room-player-name"
                        >Fun name</InputLabel>
                        <OutlinedInput
                            id="join-room-player-name"
                            fullWidth
                            // size="small"
                            // sx={{width: '250px'}}
                            // defaultValue="Composed TextField sdfsd"
                            aria-label="Enter your player name"
                            // label="Player name"
                            placeholder="Fun name"
                            value={playerName}
                            onChange={(event) => setPlayerName(event.target.value)}
                        />
                    </FormControl>

                    <FormControl>
                        <InputLabel
                            htmlFor="join-room-code"
                        >Room code</InputLabel>
                        <OutlinedInput
                            id="join-room-code"
                            fullWidth
                            // size="small"
                            // sx={{width: '250px'}}
                            // defaultValue="Composed TextField sdfsd"
                            aria-label="Enter room code to join"
                            // label="Player name"
                            placeholder="Room code"
                            value={roomCode}
                            onChange={(event) => setRoomCode(event.target.value)}
                        />
                    </FormControl>

                    <Button
                        variant="contained"
                        color="primary"
                        size="small"
                        sx={{flexShrink: 0}}
                        href={`/room/${roomCode}`}
                    >
                        Join
                    </Button>
                    <span>or</span>
                    <Button
                        variant="contained"
                        color="secondary"
                        size="small"
                        sx={{flexShrink: 0}}
                        onClick={() => createRoom()}
                    >
                        Create
                    </Button>
                </Stack>
            </Box>
        </>
    );
}