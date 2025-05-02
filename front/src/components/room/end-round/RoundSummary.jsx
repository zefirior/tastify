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
    Box,
    Card,
    CardContent,
    Stack
} from '@mui/material';
import { getOrSetPlayerUuid } from '../../../lib/backend.js';

export default function RoundSummary({room}) {
    const currentRound = room.state.currentRound;
    const roundSubmissions = currentRound.submittions || {};
    const roundResults = currentRound.results || {};
    const currentPlayerUuid = getOrSetPlayerUuid();

    // Find suggester
    const suggester = room.players.find(player => player.uuid === currentRound.suggester.uuid);
    const isCurrentPlayerSuggester = suggester.uuid === currentPlayerUuid;

    // Sort remaining players by round points (desc), then by total points (desc)
    const otherPlayers = room.players
        .filter(player => player.uuid !== suggester.uuid)
        .sort((a, b) => {
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
        <Box sx={{ mt: 2 }}>
            <Card variant="outlined" sx={{ mb: 2 }}>
                <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
                    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems={{ sm: 'center' }}>
                        <Box>
                            <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                                Round Suggester: {suggester.nickname} {isCurrentPlayerSuggester ? '(You)' : ''}
                            </Typography>
                            <Typography variant="body2">
                                Selected Band: <Box component="span" sx={{ fontWeight: 'bold' }}>{currentRound.groupName}</Box>
                            </Typography>
                        </Box>
                        <Stack direction="row" spacing={2}>
                            <Typography variant="body2">
                                Round Points: <Box component="span" sx={{ fontWeight: 'bold' }}>{roundResults[suggester.uuid] || 0}</Box>
                            </Typography>
                            <Typography variant="body2">
                                Total Score: <Box component="span" sx={{ fontWeight: 'bold' }}>{room.getPlayerScore(suggester.uuid)}</Box>
                            </Typography>
                        </Stack>
                    </Stack>
                </CardContent>
            </Card>

            <TableContainer component={Paper}>
                <Table size="small" sx={{ '& .MuiTableCell-root': { py: 1 } }}>
                    <TableHead>
                        <TableRow>
                            <TableCell>Player</TableCell>
                            <TableCell>Submitted Song</TableCell>
                            <TableCell align="right">Round Points</TableCell>
                            <TableCell align="right">Total Score</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {otherPlayers.map((player) => {
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
                                    </TableCell>
                                    <TableCell>
                                        {submission || 'No submission'}
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
