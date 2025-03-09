import Client from '../../../lib/backend.js';
import * as React from 'react';
import MenuItem from "@mui/material/MenuItem";
import SearchForm from "../submission-utils/SearchForm.jsx";
import SubmissionForm from "../submission-utils/SubmissionForm.jsx";
import Box from "@mui/material/Box";

export default function SuggesterSuggestGroup({room}) {
    const [searchName, setSearchName] = React.useState('');
    const [nameOptions, setNameOptions] = React.useState([]);
    const [groupName, setGroupName] = React.useState('');

    return (
        <>
            <div>The round has started. Please suggest a group</div>

            <SearchForm
                textPrefix=""
                searchName={searchName}
                setSearchName={setSearchName}
                onSearchCLick={() => {
                    Client.searchGroup(searchName).then(r => {
                        console.log('group search result', r);
                        setNameOptions(r);
                    });
                }}>
            </SearchForm>

            {nameOptions.length >0 && (
                <Box>
                    <SubmissionForm
                        name={groupName}
                        setName={setGroupName}
                        nameOptions={nameOptions}
                        optionBuilder={(option) => (
                            <MenuItem key={option.id} value={option.name}>
                                {option.name}
                            </MenuItem>
                        )}
                        onClick={() => {
                            Client.submitGroup(room.code, groupName)
                                .then(r => console.group('submitted group', r));
                        }}
                    />
                </Box>
            )}
        </>
    );
}
