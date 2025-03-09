import Client, {RoundStage} from '../../lib/backend.js';
import * as React from 'react';
import PlayersGrid from '../PlayersGrid.jsx';
import QRCode from 'react-qr-code';
import Button from '@mui/material/Button';
import DashNew from './DashNew.jsx';
import DashSuggestGroup from './suggest-group/DashSuggestGroup.jsx';
import DashSubmitTrack from './submit-track/DashSubmitTrack.jsx';
import DashEndRound from './end-round/DashEndRound.jsx';
import Stack from '@mui/material/Stack';
import {Alert, Backdrop, Card, Paper} from '@mui/material';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

export default function DashRunning({room}) {
    let dashView = null;
    switch (room.state.currentRound.stage) {
        case RoundStage.GROUP_SUGGESTION:
            dashView = <DashSuggestGroup room={room} />;
            break;
        case RoundStage.TRACKS_SUBMISSION:
            dashView = <DashSubmitTrack room={room} />;
            break;
        case RoundStage.END_ROUND:
            dashView = <DashEndRound room={room} />;
            break;
    }

    const timeLeft = room.state.currentRound.timeLeft;

    return (
        <>
            <Stack spacing={2}>
                <Paper variant="elevation" color={'blue'} className="p-4 m-20">
                    <Typography gutterBottom variant="h5" component="div">
                        Room: {room.code}
                    </Typography>
                    {dashView}
                    <Typography variant="body3" sx={{ color: 'text.secondary' }}>
                        Time left: {timeLeft} sec
                    </Typography>
                </Paper>
                <Paper color="blue" className="p-4 m-20">
                    <PlayersGrid room={room} />
                </Paper>
            </Stack>

            <h1>Game dashboard: {room.code}</h1>
            <big>Time left: {timeLeft} sec</big>
            <PlayersGrid room={room} />
            {dashView}
        </>
    );
}
