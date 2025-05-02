import Typography from '@mui/material/Typography';

export default function DashSuggestGroup({room}) {
    const suggester = room.state.currentRound.suggester;
    return (
        <>
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                Round has started. Please relax and enjoy till <span style={{ fontWeight: 'bold' }}>{suggester.nickname}</span> suggests group
            </Typography>
        </>
    );
}