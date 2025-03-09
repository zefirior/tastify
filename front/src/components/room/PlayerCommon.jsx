import Page from '../../pages/Page.jsx';
import {getOrSetPlayerUuid, RoomStatus, RoundStage} from '../../lib/backend.js';
import SuggesterSuggestGroup from './suggest-group/SuggesterSuggestGroup.jsx';
import SuggesterSubmitTrack from './submit-track/SuggesterSubmitTrack.jsx';
import SuggesterEndRound from './end-round/SuggesterEndRound.jsx';
import SongerSuggestGroup from './suggest-group/SongerSuggestGroup.jsx';
import SongerSubmitTrackActive from './submit-track/SongerSubmitTrackActive.jsx';
import SongerEndRound from './end-round/SongerEndRound.jsx';
import PlayerNew from './PlayerNew.jsx';
import PlayersGrid from '../PlayersGrid.jsx';
import * as React from 'react';
import SongerSubmitTrackWaiting from "./submit-track/SongerSubmitTrackWaiting.jsx";

export default function PlayerCommon({room}) {
    if (room.status === RoomStatus.NEW) {
        return <PlayerNew room={room} />;
    }

    const currentRound = room.state.currentRound;
    const suggesterUuid = currentRound.suggester.uuid;
    const stage = currentRound.stage;

    function chooseView() {
        const currentPlayer = getOrSetPlayerUuid();
        if (currentPlayer === suggesterUuid) {
            switch (stage) {
                case RoundStage.GROUP_SUGGESTION:
                    return <SuggesterSuggestGroup room={room} />;
                case RoundStage.TRACKS_SUBMISSION:
                    return <SuggesterSubmitTrack room={room} />;
                case RoundStage.END_ROUND:
                    return <SuggesterEndRound room={room} />;
            }
        } else {
            switch (stage) {
                case RoundStage.GROUP_SUGGESTION:
                    return <SongerSuggestGroup room={room} />;
                case RoundStage.TRACKS_SUBMISSION:
                    if (!currentRound.submittions.hasOwnProperty(currentPlayer)) {
                        return <SongerSubmitTrackActive room={room} />;
                    }
                    return <SongerSubmitTrackWaiting />
                case RoundStage.END_ROUND:
                    return <SongerEndRound room={room} />;
            }
        }
    }

    const timeLeft = currentRound.timeLeft;

    return (
        <Page>
            <PlayersGrid room={room} />
            <big>Time left: {timeLeft} sec</big>
            {chooseView()}
        </Page>
    );
}