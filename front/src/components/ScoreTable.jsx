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

export default function ScoreTable({room}) {
    return (
        <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
                Players
            </Typography>

            <TableContainer component={Paper} sx={{ mt: 2 }}>
                <Table size="small">
                    <TableHead>
                        <TableRow>
                            <TableCell>Nickname</TableCell>
                            <TableCell align="right">Score</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {room.players.map((player) => (
                            <TableRow
                                key={player.uuid}
                                sx={{'&:last-child td, &:last-child th': {border: 0}}}
                            >
                                <TableCell>
                                    {player.nickname}
                                    {player.uuid === room.state.currentRound?.suggester?.uuid ? ' (Suggester)' : ''}
                                </TableCell>
                                <TableCell align="right">
                                    {room.getPlayerScore(player.uuid)}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </Box>
    );
} 