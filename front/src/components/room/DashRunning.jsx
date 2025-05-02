import {RoundStage} from '../../lib/backend.js';
import PlayersGrid from '../PlayersGrid.jsx';
import DashSuggestGroup from './suggest-group/DashSuggestGroup.jsx';
import DashSubmitTrack from './submit-track/DashSubmitTrack.jsx';
import DashEndRound from './end-round/DashEndRound.jsx';
import Stack from '@mui/material/Stack';
import {Paper} from '@mui/material';
import Typography from '@mui/material/Typography';

export default function DashRunning({room}) {
    const currentStage = room.state.currentRound.stage;
    const timeLeft = room.state.currentRound.timeLeft;

    let mainView;
    if (currentStage === RoundStage.END_ROUND) {
        mainView = <DashEndRound room={room} />;
    } else {
        mainView = (
            <>
                {currentStage === RoundStage.GROUP_SUGGESTION && <DashSuggestGroup room={room} />}
                {currentStage === RoundStage.TRACKS_SUBMISSION && <DashSubmitTrack room={room} />}
                <Paper color="blue" className="p-4 m-20">
                    <PlayersGrid room={room} />
                </Paper>
            </>
        );
    }

    return (
        <>
            <Stack spacing={2}>
                <Paper variant="elevation" color={'blue'} className="p-4 m-20">
                    <Typography gutterBottom variant="h5" component="div">
                        Room: {room.code}
                    </Typography>
                    <Typography variant="body3" sx={{ color: 'text.secondary' }}>
                        Time left: {timeLeft} sec
                    </Typography>
                </Paper>
                {mainView}
            </Stack>
        </>
    );
}
