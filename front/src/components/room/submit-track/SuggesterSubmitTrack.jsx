import * as React from 'react';

export default function SuggesterSubmitTrack({room}) {
    const groupName = room.state.currentRound.group.name;

    return (
        <>
            <small>You suggest {groupName}</small>
            <small>Please wait your friends</small>
        </>
    );
}