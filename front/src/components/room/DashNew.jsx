import Client, {getJoinRoomUrl} from '../../lib/backend.js';
import * as React from 'react';
import PlayersGrid from '../PlayersGrid.jsx';
import QRCode from 'react-qr-code';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import {Alert, Backdrop, Paper} from '@mui/material';
import Typography from '@mui/material/Typography';

export default function DashNew({room}) {
    const [starting, setStarting] = React.useState(false);
    const [showAlert, setShowAlert] = React.useState(false);

    async function start() {
        if (room.players.length < 2) {
            setShowAlert(true);
            setTimeout(() => {
                setShowAlert(false);
            }, 2000);
            return;
        }

        setStarting(true);
        setTimeout(() => {
            setStarting(false);
        }, 5000);
        await Client.startGame(room.code)
            .catch((err) => {
                console.error(err);
            })
            .then(() => {
                console.log('game started');
            });
    }


    return (
        <Stack spacing={2}>
            <Backdrop
                sx={(theme) => ({ zIndex: theme.zIndex.drawer + 1 })}
                open={showAlert}
                onClick={() => setShowAlert(false)}
            >
                <Paper>
                    <Alert variant="filled" severity="info" sx={{minHeight: '100px'}}>
                        Need at least 2 players to start the game.
                    </Alert>
                </Paper>
            </Backdrop>
            <Paper variant="elevation" color={'blue'} className="p-4 m-20">
                <Stack>
                    <Box>
                        <Typography variant="h5" component="div">
                            Scan to join room: {room.code}
                        </Typography>
                        <div className="qr-back pt-20 background-white p-4 m-4 rounded-lg">
                            <QRCode
                                title="Scan to join"
                                value={getJoinRoomUrl(room.code)}
                            />
                        </div>
                    </Box>
                    <Box>
                        <Button
                            variant="outlined"
                            color="primary"
                            size="large"
                            loading={starting}
                            sx={{flexShrink: 0, margin: '10px'}}
                            onClick={start}
                        >Start game</Button>
                    </Box>
                </Stack>
            </Paper>
            <Paper color="blue" className="p-4 m-20">
                <PlayersGrid room={room} />
            </Paper>
        </Stack>
    );
}