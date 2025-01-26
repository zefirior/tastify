import * as React from 'react';

export default function DashSuggestGroup({room}) {
    const suggester = room.state.currentRound.suggester;
    return (
        <>
            <small>Game started. Please relax and enjoy till {suggester.nickname.toUpperCase()} suggest group</small>
        </>
    );
}