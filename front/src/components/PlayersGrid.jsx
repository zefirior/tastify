import * as React from 'react';
import {
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow
} from '@mui/material';
import Typography from '@mui/material/Typography';

export default function PlayersGrid({room}) {
    const players = room.players;

    return (
        <>
            <Typography variant="h6" component="div">Players</Typography>
            <TableContainer component={Paper}>
                <Table size="small" aria-label="a dense table">
                    <TableHead>
                        <TableRow>
                            <TableCell>Nickname</TableCell>
                            <TableCell align="right">Score</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {players.map((player) => (
                            <TableRow
                                key={player.nickname}
                                sx={{'&:last-child td, &:last-child th': {border: 0}}}
                            >
                                <TableCell component="th" scope="row">
                                    {player.nickname}
                                </TableCell>
                                <TableCell align="right">{room.getPlayerScore(player.uuid)}</TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </>
    );
}