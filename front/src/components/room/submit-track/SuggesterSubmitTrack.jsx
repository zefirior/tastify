import * as React from 'react';

export default function SuggesterSubmitTrack({room}) {
    const groupName = room.state.currentRound.group.name;

    return (
        <>
            <div>You suggest <span style={{ fontWeight: 'bold' }}>{groupName}</span></div>
            <div>Enjoy the silence while your friends are thinking</div>
        </>
    );
}
