import Client from '../../../lib/backend.js'
import * as React from 'react';
import Button from '@mui/material/Button';

export default function SuggesterSuggestGroup({room}) {
    const suggester = room.state.currentRound.suggester;


    return (
        <>
            <small>Game started. Please relax and enjoy till {suggester.nickname.toUpperCase()} suggest group</small>
        </>
    );
}