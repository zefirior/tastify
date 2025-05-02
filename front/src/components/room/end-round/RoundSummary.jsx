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
import { getOrSetPlayerUuid } from '../../../lib/backend.js';

export default function RoundSummary({room}) {
    const currentRound = room.state.currentRound;
    const roundSubmissions = currentRound.submittions || {};
    const roundResults = currentRound.results || {};
    const currentPlayerUuid = getOrSetPlayerUuid();

    // Sort players: suggester first, then by round points (desc), then by total points (desc)
    const sortedPlayers = [...room.players].sort((a, b) => {
        // Suggester always comes first
        if (a.uuid === currentRound.suggester.uuid) return -1;
        if (b.uuid === currentRound.suggester.uuid) return 1;

        // Sort by round points
        const aRoundPoints = roundResults[a.uuid] || 0;
        const bRoundPoints = roundResults[b.uuid] || 0;
        if (aRoundPoints !== bRoundPoints) {
            return bRoundPoints - aRoundPoints; // descending order
        }

        // If round points are equal, sort by total points
        const aTotalPoints = room.getPlayerScore(a.uuid);
        const bTotalPoints = room.getPlayerScore(b.uuid);
        return bTotalPoints - aTotalPoints; // descending order
    });

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
                        {sortedPlayers.map((player) => {
                            const isSuggester = player.uuid === currentRound.suggester.uuid;
                            const isCurrentPlayer = player.uuid === currentPlayerUuid;
                            const submission = roundSubmissions[player.uuid];
                            
                            return (
                                <TableRow
                                    key={player.uuid}
                                    sx={{'&:last-child td, &:last-child th': {border: 0}}}
                                >
                                    <TableCell>
                                        {player.nickname}
                                        {isCurrentPlayer ? ' (You)' : ''}
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
