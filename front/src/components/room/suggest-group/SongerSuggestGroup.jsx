import * as React from 'react';

export default function SongerSuggestGroup({room}) {
    const suggester = room.state.currentRound.suggester;
    return (
        <>
            <div>Round has started. Please relax and enjoy till <span style={{ fontWeight: 'bold' }}>{suggester.nickname}</span> suggests group</div>
        </>
    );
}