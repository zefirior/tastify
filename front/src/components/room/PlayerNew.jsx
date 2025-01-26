import Client from '../../lib/backend.js';
import Button from '@mui/material/Button';
import * as React from 'react';
import PlayersGrid from '../PlayersGrid.jsx';

export default function PlayerNew({room}) {

    function increment() {
        console.log('increment');
        Client.increment(room.code).then((room) => {
            console.log('incremented', room);
        });
    }

    return (
        <>
            <h1>Your game: {room.code}</h1>
            <PlayersGrid players={room.players} />
            <Button
                variant="contained"
                color="primary"
                size="small"
                sx={{flexShrink: 0}}
                onClick={increment}
            >Тыц me!</Button>
        </>
    );
}