export default function SuggesterSubmitTrack({room}) {
    const groupName = room.state.currentRound.groupName;
    
    const sarcasticPhrases = [
        "Ah yes, your musical genius strikes again! 🎵",
        "Look at you, expanding everyone's musical horizons! ✨",
        "Another masterpiece added to the playlist! 🎧",
        "Your music taste is... let's say, adventurous! 🌟",
        "Well, this will definitely get the party started! 🎉",
    ];

    const randomPhrase = sarcasticPhrases[Math.floor(Math.random() * sarcasticPhrases.length)];

    return (
        <>
            <div>You suggest {groupName}</div>
            <div>{randomPhrase}</div>
        </>
    );
}