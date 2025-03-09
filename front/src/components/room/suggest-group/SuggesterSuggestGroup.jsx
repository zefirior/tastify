import Client from '../../../lib/backend.js';
import * as React from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import {FormControl} from "@mui/material";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import SendIcon from '@mui/icons-material/Send';
import SearchIcon from '@mui/icons-material/Search';

export default function SuggesterSuggestGroup({room}) {
    const [searchName, setSearchName] = React.useState('');
    const [nameOptions, setNameOptions] = React.useState([]);
    const [groupName, setGroupName] = React.useState('');

    return (
        <>
            <div>The round has started. Please suggest a group</div>
            <Box>
                <TextField
                    id="band-name-search"
                    label="Start typing..."
                    variant="standard"
                    value={searchName}
                    onChange={(e) => setSearchName(e.target.value)}
                />
                <Button
                    variant="contained"
                    color="primary"
                    endIcon={<SearchIcon />}
                    size="small"
                    onClick={() => {
                        Client.searchGroup(searchName).then(r => {
                            console.log('search result', r); setNameOptions(r);
                        });
                    }}
                >
                    Search
                </Button>

                {nameOptions.length >0 && (
                    <>
                        <FormControl fullWidth>
                            <InputLabel id="demo-simple-select-label">Your suggestion</InputLabel>
                            <Select
                                id="band-name-suggestion"
                                variant="outlined"
                                value={groupName}
                                label="Choose the group"
                                onChange={(e) => setGroupName(e.target.value)}
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
                                Client.submitGroup(room.code, groupName).then(r => console.group('submitted group', r));
                            }}
                        >
                            Submit
                        </Button>
                    </>
                )}
            </Box>
        </>
    );
}
