import * as React from 'react';

export default function DashSubmitTrack({room}) {
    const suggesterNick = room.state.currentRound.suggester.nickname.toUpperCase();
    const groupName = room.state.currentRound.group.name;
    return (
        <>
            <small>Now is the time to find tracks in your favorites</small>
            <small>{suggesterNick} suggested <bold>{groupName}</bold>. Please find its track or skip it</small>
        </>
    );
}