import {getOrSetPlayerUuid, RoomStatus, RoundStage} from '../../lib/backend.js';
import SuggesterSuggestGroup from './suggest-group/SuggesterSuggestGroup.jsx';
import SuggesterSubmitTrack from './submit-track/SuggesterSubmitTrack.jsx';
import SongerSuggestGroup from './suggest-group/SongerSuggestGroup.jsx';
import SongerSubmitTrackActive from './submit-track/SongerSubmitTrackActive.jsx';
import PlayerNew from './PlayerNew.jsx';
import RoundSummary from './end-round/RoundSummary.jsx';
import SongerSubmitTrackWaiting from "./submit-track/SongerSubmitTrackWaiting.jsx";
import SuggesterEndRound from './end-round/SuggesterEndRound.jsx';

export default function PlayerCommon({room}) {
    if (room.status === RoomStatus.NEW) {
        return <PlayerNew room={room} />;
    }

    const currentRound = room.state.currentRound;
    const suggesterUuid = currentRound.suggester.uuid;
    const stage = currentRound.stage;

    function chooseView() {
        const currentPlayer = getOrSetPlayerUuid();
        if (stage === RoundStage.END_ROUND) {
            if (currentPlayer === suggesterUuid) {
                return (
                    <>
                        <RoundSummary room={room} />
                        <SuggesterEndRound room={room} />
                    </>
                );
            }
            return <RoundSummary room={room} />;
        }
        
        if (currentPlayer === suggesterUuid) {
            switch (stage) {
                case RoundStage.GROUP_SUGGESTION:
                    return <SuggesterSuggestGroup room={room} />;
                case RoundStage.TRACKS_SUBMISSION:
                    return <SuggesterSubmitTrack room={room} />;
            }
        } else {
            switch (stage) {
                case RoundStage.GROUP_SUGGESTION:
                    return <SongerSuggestGroup room={room} />;
                case RoundStage.TRACKS_SUBMISSION:
                    if (!Object.prototype.hasOwnProperty.call(currentRound.submissions, currentPlayer)) {
                        return <SongerSubmitTrackActive room={room} />;
                    }
                    return <SongerSubmitTrackWaiting />
            }
        }
    }

    const timeLeft = currentRound.timeLeft;

    return (
        <>
            <big>Time left: {timeLeft} sec</big>
            {chooseView()}
        </>
    );
}