import * as React from 'react';
import Box from '@mui/material/Box';
import Client from '../../../lib/backend.js';
import MenuItem from "@mui/material/MenuItem";
import SearchForm from "../submission-utils/SearchForm.jsx";
import SubmissionForm from "../submission-utils/SubmissionForm.jsx";

export default function SongerSubmitTrackActive({room}) {
    const suggesterNick = room.state.currentRound.suggester.nickname.toUpperCase();
    const groupName = room.state.currentRound.group.name;

    const [searchName, setSearchName] = React.useState('');
    const [nameOptions, setNameOptions] = React.useState([]);
    const [selectedKey, setSelectedKey] = React.useState(null);

    return (
        <>
            <div>{suggesterNick} suggested {groupName}</div>
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
                }}
                skipBtn={true}
                onSkipBtnClick={() => {
                    Client.skipTrack(room.code).then(console.log);
                }
            }/>

            {nameOptions.length >0 && (
                <Box>
                    <SubmissionForm
                        selectedKey={selectedKey}
                        setSelectedKey={(value) => {
                            // Find the full option object by id or name
                            setSelectedKey(value);
                        }}
                        nameOptions={nameOptions}
                        optionBuilder={(option) => (
                            <MenuItem key={option.id} value={option.id}>
                                {option.name}
                            </MenuItem>
                        )}
                        onClick={() => {
                            if (selectedKey) {
                                const option = nameOptions.find(opt => opt.id === selectedKey);
                                Client.submitTrack(room.code, option)
                                    .then(r => console.log('submitted track', r));
                            }
                        }}
                    />
                </Box>
            )}
        </>
    );
}
