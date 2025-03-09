import * as React from 'react';
import Typography from '@mui/material/Typography';

export default function DashSubmitTrack({room}) {
    const suggesterNick = room.state.currentRound.suggester.nickname.toUpperCase();
    const groupName = room.state.currentRound.groupName;
    return (
        <Typography variant="body2" sx={{color: 'text.secondary'}}>
            Now is the time to find tracks in your favorites.
            {suggesterNick} suggested <p className={'font-bold'}>{groupName}</p>. Please find its track or skip it
        </Typography>
    );
}