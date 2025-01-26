import Client from '../../../lib/backend.js';
import * as React from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';

export default function SuggesterSuggestGroup({room}) {
    const [groupName, setGroupName] = React.useState('');

    return (
        <>
            <div>Game started. Please suggest group</div>
            <Box>
                <TextField
                    id="outlined-basic"
                    label="Outlined"
                    variant="outlined"
                    value={groupName}
                    onChange={(e) => setGroupName(e.target.value)}
                />
                <Button
                    variant="contained"
                    color="primary"
                    onClick={() => {
                        Client.submitGroup(room.code, groupName).then(r => console.group('submitted group', r));
                    }}
                >
                    Suggest
                </Button>
            </Box>
        </>
    );
}