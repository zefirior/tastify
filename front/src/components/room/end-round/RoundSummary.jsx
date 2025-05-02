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
    const roundSubmissions = currentRound.submissions || {};
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
        <Box sx={{ mt: 2, width: '100%' }}>
            <Card variant="outlined" sx={{ mb: 2, width: '100%' }}>
                <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
                    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems={{ sm: 'center' }} justifyContent="space-between" sx={{ width: '100%' }}>
                        <Box>
                            <Typography variant="subtitle1">
                                Round Suggester: <Box component="span" sx={{ fontWeight: 'bold' }}>{suggester.nickname}</Box>{isCurrentPlayerSuggester ? ' (You)' : ''}
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

            <TableContainer component={Paper} sx={{ width: '100%' }}>
                <Table size="small" sx={{ '& .MuiTableCell-root': { py: 1 }, width: '100%' }}>
                    <TableHead>
                        <TableRow>
                            <TableCell width="30%">Player</TableCell>
                            <TableCell width="40%">Submitted Song</TableCell>
                            <TableCell width="15%" align="right">Round Points</TableCell>
                            <TableCell width="15%" align="right">Total Score</TableCell>
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
