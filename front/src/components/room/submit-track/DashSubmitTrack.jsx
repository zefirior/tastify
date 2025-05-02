import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import Box from '@mui/material/Box';

export default function DashSubmitTrack({room}) {
    if (!room?.state?.currentRound?.suggester) {
        console.error('DashSubmitTrack: Missing required room state properties', room);
        return null;
    }

    // Players who haven't submitted tracks yet:
    const pendingPlayers = room.players?.filter(player => {
        const hasSubmitted = Object.hasOwn(room.state.currentRound.submissions || {}, player.uuid);
        const isSuggester = player.uuid === room.state.currentRound.suggester.uuid;

        return !hasSubmitted && !isSuggester;
    }) || [];

    const suggesterNick = room.state.currentRound.suggester.nickname.toUpperCase();
    const groupName = room.state.currentRound.group?.name || '';
    return (
        <Box>
            <Typography variant="body2" sx={{color: 'text.secondary', mb: 2}}>
                <span style={{ fontWeight: 'bold' }}>{suggesterNick}</span> suggested <span className={'font-bold'}>{groupName}</span>.
                Now is the time to find their tracks in your liked songs.
                Please submit a track or skip the round.
            </Typography>

            {pendingPlayers.length > 0 && (
                <>
                    <Typography variant="body2" sx={{color: 'text.secondary', mt: 2, mb: 1}}>
                        Waiting for submissions from:
                    </Typography>
                    <List dense>
                        {pendingPlayers.map((player) => (
                            <ListItem key={player.uuid}>
                                <ListItemText
                                    primary={player.nickname}
                                    sx={{ '& .MuiTypography-root': { color: 'text.secondary' } }}
                                />
                            </ListItem>
                        ))}
                    </List>
                </>
            )}
        </Box>
    );
}
