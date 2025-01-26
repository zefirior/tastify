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

    function joinRoom() {
        console.log('join room');
        Client.joinRoom(roomCode, playerName).then(() => {
            console.log('joined room', roomCode);
            navigate(`/room/${roomCode}`);
        });
    }

    const isNotReadyToJoin = !playerName || !roomCode;

    return (
        <>
            <h1>{'Choose your game'}</h1>
            <Box
                component="form"
                sx={{ '& > :not(style)': { m: 1 } }}
                noValidate
                autoComplete="off"
            >
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} useFlexGap>
                    <div>
                        <FormControl className={'mb-2'}>
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

                        &nbsp;&nbsp;&nbsp;

                        <FormControl className={'mb-2'}>
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
                    </div>

                    <div>
                        <Button
                            variant="text"
                            color="primary"
                            size="small"
                            sx={{flexShrink: 0}}
                            disabled={isNotReadyToJoin}
                            onClick={() => joinRoom()}
                        >
                            Join
                        </Button>
                        <span>or&nbsp;&nbsp;&nbsp;</span>
                        <Button
                            variant="contained"
                            color="secondary"
                            size="small"
                            sx={{flexShrink: 0}}
                            onClick={() => createRoom()}
                        >
                            Create
                        </Button>
                    </div>
                </Stack>
            </Box>
        </>
    );
}