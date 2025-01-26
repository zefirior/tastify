import * as React from 'react';

export default function SuggesterSubmitTrack({room}) {
    const groupName = room.state.currentRound.groupName;

    return (
        <>
            <div>You suggest {groupName}</div>
            <div>Please wait your friends</div>
        </>
    );
}