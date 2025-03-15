import Client from '../../lib/backend.js';
import Button from '@mui/material/Button';
import * as React from 'react';
import PlayersGrid from '../PlayersGrid.jsx';

export default function PlayerNew({room}) {
    return (
        <>
            <h1>Your game: {room.code}</h1>
            <PlayersGrid room={room} />
        </>
    );
}