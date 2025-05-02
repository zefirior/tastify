import * as React from 'react';

export default function SuggesterSubmitTrack({room}) {
    const groupName = room.state.currentRound.groupName;

    return (
        <>
            <div>You suggest {groupName}</div>
            <div>Enjoy the silence while your friends are thinking...</div>
        </>
    );
}
