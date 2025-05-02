import Client from '../../../lib/backend.js';
import * as React from 'react';
import MenuItem from "@mui/material/MenuItem";
import SearchForm from "../submission-utils/SearchForm.jsx";
import SubmissionForm from "../submission-utils/SubmissionForm.jsx";
import Box from "@mui/material/Box";

export default function SuggesterSuggestGroup({room}) {
    const [searchName, setSearchName] = React.useState('');
    const [nameOptions, setNameOptions] = React.useState([]);
    const [selectedKey, setSelectedKey] = React.useState(null);

    return (
        <>
            <div>The round has started. It&#39;s you turn to suggest a group!</div>

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
                        selectedKey={selectedKey}
                        setSelectedKey={(key) => setSelectedKey(key)}
                        nameOptions={nameOptions}
                        optionBuilder={(option) => (
                            <MenuItem key={option.id} value={option.id}>
                                {option.name}
                            </MenuItem>
                        )}
                        onClick={() => {
                            if (selectedKey) {
                                const option = nameOptions.find(opt => opt.id === selectedKey);
                                Client.submitGroup(room.code, option)
                                    .then(r => console.group('submitted group', r));
                            }
                        }}
                    />
                </Box>
            )}
        </>
    );
}
