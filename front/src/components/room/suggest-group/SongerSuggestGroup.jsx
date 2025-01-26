import * as React from 'react';

export default function SongerSuggestGroup({room}) {
    const suggester = room.state.currentRound.suggester;
    return (
        <>
            <div>Game started. Please relax and enjoy till {suggester.nickname.toUpperCase()} suggest group</div>
        </>
    );
}