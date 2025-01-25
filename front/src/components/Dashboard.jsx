import Client from '../lib/backend.js';
import Box from '@mui/material/Box';
import InputLabel from '@mui/material/InputLabel';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import * as React from 'react';
import {FormControl, OutlinedInput} from '@mui/material';
import {Link, useNavigate} from 'react-router';
import {useContext} from 'react';
import {RoomStoreContext} from '../stores/room.js';
import PlayersGrid from './PlayersGrid.jsx';

export default function Dashboard({room}) {
    return (
        <>
            <h1>Game dashboard: {room.code}</h1>
            <PlayersGrid players={room.players} />
        </>
    );
}