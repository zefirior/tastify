import * as React from 'react';
import Typography from '@mui/material/Typography';

export default function DashSubmitTrack({room}) {
    const suggesterNick = room.state.currentRound.suggester.nickname.toUpperCase();
    const groupName = room.state.currentRound.groupName;
    return (
        <Typography variant="body2" sx={{color: 'text.secondary'}}>
            {suggesterNick} suggested <p className={'font-bold'}>{groupName}</p>
            Now is the time to find their tracks in your liked songs.
            Please submit a track or skip the round.
        </Typography>
    );
}
