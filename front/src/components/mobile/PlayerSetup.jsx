import * as React from 'react';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import TextField from '@mui/material/TextField';
import ArrowBackIosNewIcon from '@mui/icons-material/ArrowBackIosNew';
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';

function AvatarOne() {
    return (
        <svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <circle cx="32" cy="32" r="30" fill="#4876EE" />
            <circle cx="32" cy="26" r="10" fill="#fff" />
            <rect x="16" y="38" width="32" height="12" fill="#fff" />
        </svg>
    );
}

function AvatarTwo() {
    return (
        <svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="2" width="60" height="60" rx="10" fill="#00D3AB" />
            <circle cx="32" cy="26" r="10" fill="#fff" />
            <rect x="18" y="40" width="28" height="10" fill="#fff" />
        </svg>
    );
}

const avatars = [AvatarOne, AvatarTwo];

export default function PlayerSetup({ name, setName, avatarIndex, setAvatarIndex }) {
    const Avatar = avatars[avatarIndex];
    const total = avatars.length;
    const prev = () => setAvatarIndex((avatarIndex - 1 + total) % total);
    const next = () => setAvatarIndex((avatarIndex + 1) % total);

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <IconButton aria-label="previous avatar" onClick={prev}>
                    <ArrowBackIosNewIcon />
                </IconButton>
                <Avatar />
                <IconButton aria-label="next avatar" onClick={next}>
                    <ArrowForwardIosIcon />
                </IconButton>
            </Box>
            <TextField
                label="Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                fullWidth
            />
        </Box>
    );
}
