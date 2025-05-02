import * as React from 'react';
import Client from '../../../lib/backend.js';
import Button from '@mui/material/Button';

export default function SuggesterEndRound({room}) {
    const [loading, setLoading] = React.useState(false);
    async function nextTurn() {
        setLoading(true);
        setTimeout(() => {
            setLoading(false);
        }, 2000);
        await Client.nextTurn(room.code).then(() => {
            console.log('game started');
        });
    }

    return (
        <>
            <Button
                color="success"
                variant="contained"
                loading={loading}
                onClick={nextTurn}
            >Next round</Button>
        </>
    );
}
