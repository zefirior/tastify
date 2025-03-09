import * as React from 'react';
import Box from '@mui/material/Box';
import CloseIcon from '@mui/icons-material/Close';
import Client from '../../../lib/backend.js';
import IconButton from '@mui/material/IconButton';
import MenuItem from "@mui/material/MenuItem";
import SearchForm from "../submission-utils/SearchForm.jsx";
import SubmissionForm from "../submission-utils/SubmissionForm.jsx";

export default function SongerSubmitTrackActive({room}) {
    const suggesterNick = room.state.currentRound.suggester.nickname.toUpperCase();
    const groupName = room.state.currentRound.groupName;
    const [trackName, setTrackName] = React.useState('');

    const [searchName, setSearchName] = React.useState('');
    const [nameOptions, setNameOptions] = React.useState([]);

    return (
        <>
            <div>{suggesterNick} suggested <bold>{groupName}</bold></div>
            <div>Now is the time to find their tracks in your liked songs.</div>
            <div>Please submit a track or skip the round.</div>

            <SearchForm
                textPrefix={groupName + " - "}
                searchName={searchName}
                setSearchName={setSearchName}
                onSearchCLick={() => {
                    Client.searchTrack(groupName, searchName).then(r => {
                        console.log('search result', r); setNameOptions(r);
                    });
                }}>
            </SearchForm>

            {nameOptions.length >0 && (
                <Box>
                    <SubmissionForm
                        name={trackName}
                        setName={setTrackName}
                        nameOptions={nameOptions}
                        optionBuilder={(option) => (
                            <MenuItem key={option.id} value={option.name}>
                                {option.name}
                            </MenuItem>
                        )}
                        onClick={() => {
                            Client.submitTrack(room.code, trackName).then(r => console.group('submitted track', r));
                        }}
                    />
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
