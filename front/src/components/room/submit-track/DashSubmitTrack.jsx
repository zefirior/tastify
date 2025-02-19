import * as React from 'react';

export default function DashSubmitTrack({room}) {
    const suggesterNick = room.state.currentRound.suggester.nickname.toUpperCase();
    const groupName = room.state.currentRound.groupName;
    return (
        <>
            <div>Now is the time to find tracks in your favorites</div>
            <div>{suggesterNick} suggested <bold>{groupName}</bold>. Please find its track or skip it</div>
        </>
    );
}