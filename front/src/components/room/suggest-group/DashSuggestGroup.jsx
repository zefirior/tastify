import * as React from 'react';
import Typography from '@mui/material/Typography';

export default function DashSuggestGroup({room}) {
    const suggester = room.state.currentRound.suggester;
    return (
        <>
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                Game started. Please relax and enjoy till {suggester.nickname.toUpperCase()} suggest group
            </Typography>
        </>
    );
}