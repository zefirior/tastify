import * as React from 'react';

export default function SongerSuggestGroup({room}) {
    const suggester = room.state.currentRound.suggester;
    return (
        <>
            <div>Round has started. Please relax and enjoy till {suggester.nickname.toUpperCase()} suggests group</div>
        </>
    );
}