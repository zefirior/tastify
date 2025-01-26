import * as React from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import CloseIcon from '@mui/icons-material/Close';
import Client from '../../../lib/backend.js';
import IconButton from '@mui/material/IconButton';

export default function SongerSubmitTrack({room}) {
    const suggesterNick = room.state.currentRound.suggester.nickname.toUpperCase();
    const groupName = room.state.currentRound.groupName;
    const [trackName, setTrackName] = React.useState('');
    return (
        <>
            <div>Now is the time to find tracks in your favorites</div>
            <div>{suggesterNick} suggested <bold>{groupName}</bold>. Please find its track or skip it</div>
            <Box>
                <TextField
                    id="outlined-basic"
                    label="Outlined"
                    variant="outlined"
                    value={groupName}
                    onChange={(e) => setTrackName(e.target.value)}
                />
                <Button
                    variant="contained"
                    color="primary"
                    onClick={() => {
                        Client.submitTrack(room.code, trackName).then(r => console.group('submitted track'));
                    }}
                >
                    Suggest
                </Button>
                <IconButton
                    aria-label="skip-track"
                    variant="contained"
                    color="error"
                    onClick={() => {
                        Client.skipTrack(room.code).then(r => console.group('skipped track'));
                    }}
                >
                    <CloseIcon />
                </IconButton>
            </Box>
        </>
    );
}