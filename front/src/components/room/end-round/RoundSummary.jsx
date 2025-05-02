import * as React from 'react';
import {
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography,
    Box
} from '@mui/material';

export default function RoundSummary({room}) {
    const currentRound = room.state.currentRound;
    const roundSubmissions = currentRound.submittions || {};
    const roundResults = currentRound.results || {};

    return (
        <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
                Round Summary
            </Typography>
            
            <Typography variant="subtitle1" gutterBottom>
                Selected Band: {currentRound.groupName}
            </Typography>

            <TableContainer component={Paper} sx={{ mt: 2 }}>
                <Table size="small">
                    <TableHead>
                        <TableRow>
                            <TableCell>Player</TableCell>
                            <TableCell>Submitted Song</TableCell>
                            <TableCell align="right">Round Points</TableCell>
                            <TableCell align="right">Total Score</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {room.players.map((player) => {
                            const isSuggester = player.uuid === currentRound.suggester.uuid;
                            const submission = roundSubmissions[player.uuid];
                            
                            return (
                                <TableRow
                                    key={player.uuid}
                                    sx={{'&:last-child td, &:last-child th': {border: 0}}}
                                >
                                    <TableCell>
                                        {player.nickname}
                                        {isSuggester ? ' (Suggester)' : ''}
                                    </TableCell>
                                    <TableCell>
                                        {isSuggester ? '-' : (submission || 'No submission')}
                                    </TableCell>
                                    <TableCell align="right">
                                        {roundResults[player.uuid] || 0}
                                    </TableCell>
                                    <TableCell align="right">
                                        {room.getPlayerScore(player.uuid)}
                                    </TableCell>
                                </TableRow>
                            );
                        })}
                    </TableBody>
                </Table>
            </TableContainer>
        </Box>
    );
}
