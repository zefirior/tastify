import * as React from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import CloseIcon from '@mui/icons-material/Close';
import Client from '../../../lib/backend.js';
import IconButton from '@mui/material/IconButton';
import SearchIcon from "@mui/icons-material/Search";
import SendIcon from "@mui/icons-material/Send";
import {FormControl} from "@mui/material";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";

export default function SongerSubmitTrackActive({room}) {
    const suggesterNick = room.state.currentRound.suggester.nickname.toUpperCase();
    const groupName = room.state.currentRound.groupName;
    const [trackName, setTrackName] = React.useState('');

    const [searchName, setSearchName] = React.useState('');
    const [nameOptions, setNameOptions] = React.useState([]);

    return (
        <>
            <div>Now is the time to find tracks in your favorites</div>
            <div>{suggesterNick} suggested <bold>{groupName}</bold>. Please find its track or skip it</div>

            <Box display="flex" alignItems="center">
                <span>{groupName} - </span>
                <TextField
                    id="track-name-search"
                    label="Start typing..."
                    variant="standard"
                    value={searchName}
                    onChange={(e) => setSearchName(e.target.value)}
                    sx={{ marginLeft: 1 }}
                />
            </Box>
            <Button
                variant="contained"
                color="primary"
                endIcon={<SearchIcon />}
                size="small"
                onClick={() => {
                    Client.searchTrack(searchName).then(r => {
                        console.log('search result', r); setNameOptions(r);
                    });
                }}
            >
                Search
            </Button>

            {nameOptions.length >0 && (
                <Box>
                    <FormControl fullWidth>
                        <InputLabel id="demo-simple-select-label">Your suggestion</InputLabel>
                        <Select
                            id="band-name-suggestion"
                            variant="outlined"
                            value={trackName}
                            label="Choose the group"
                            onChange={(e) => setTrackName(e.target.value)}
                        >
                            {nameOptions.map((option) => (
                                <MenuItem key={option.id} value={option.name}>
                                    {option.name}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                    <Button
                        variant="contained"
                        color="primary"
                        endIcon={<SendIcon />}
                        onClick={() => {
                            Client.submitTrack(room.code, trackName).then(console.log);
                        }}
                    >
                        Suggest
                    </Button>
                    <IconButton
                        aria-label="skip-track"
                        variant="contained"
                        color="error"
                        onClick={() => {
                            Client.skipTrack(room.code).then(console.log);
                        }}
                    >
                        <CloseIcon />
                    </IconButton>
                </Box>
            )}
        </>
    );
}
