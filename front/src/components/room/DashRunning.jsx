import Client, {RoundStage} from '../../lib/backend.js';
import * as React from 'react';
import PlayersGrid from '../PlayersGrid.jsx';
import QRCode from 'react-qr-code';
import Button from '@mui/material/Button';
import DashNew from './DashNew.jsx';
import DashSuggestGroup from './suggest-group/DashSuggestGroup.jsx';
import DashSubmitTrack from './submit-track/DashSubmitTrack.jsx';
import DashEndRound from './end-round/DashEndRound.jsx';

export default function DashRunning({room}) {
    let dashView = null;
    switch (room.state.currentRound.stage) {
        case RoundStage.GROUP_SUGGESTION:
            dashView = <DashSuggestGroup room={room} />;
            break;
        case RoundStage.TRACKS_SUBMISSION:
            dashView = <DashSubmitTrack room={room} />;
            break;
        case RoundStage.END_ROUND:
            dashView = <DashEndRound room={room} />;
            break;
    }

    return (
        <>
            <h1>Game dashboard: {room.code}</h1>
            {dashView}
            <PlayersGrid players={room.players} />
        </>
    );
}