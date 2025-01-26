import Client from '../../lib/backend.js';
import * as React from 'react';
import PlayersGrid from '../PlayersGrid.jsx';
import QRCode from 'react-qr-code';
import Button from '@mui/material/Button';

export default function DashNew({room}) {
    const [starting, setStarting] = React.useState(false);
    async function start() {
        setStarting(true);
        setTimeout(() => {
            setStarting(false);
        }, 2000);
        await Client.startGame(room.code).then(() => {
            console.log('game started');
        });
    }


    return (
        <>
            <h1>Game dashboard: {room.code}</h1>
            <h2>Scan to join</h2>
            <QRCode
                title="Scan to join"
                value={`${import.meta.env['VITE_BASE_URL']}/room/${room.code}/join`}
            />
            <Button
                variant="outlined"
                color="primary"
                size="small"
                loading={starting}
                sx={{flexShrink: 0}}
                onClick={start}
            >Start game</Button>
            <PlayersGrid room={room} />
        </>
    );
}