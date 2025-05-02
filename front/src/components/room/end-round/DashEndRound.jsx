import * as React from 'react';
import Typography from '@mui/material/Typography';
import ScoreTable from '../../ScoreTable.jsx';

export default function DashEndRound({ room }) {
    // Defensive checks for nested properties
    const submissions = room?.state?.currentRound?.submissions || {};
    // Get the first submission object from the submissions dictionary
    const firstSubmission = Object.values(submissions)[0];
    const trackId = firstSubmission?.id;

    if (trackId) {
        console.log('DashEndRound: found trackId', trackId);
    }

    return (
        <>
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                Round finished
            </Typography>

            <ScoreTable room={room} />

            {trackId ? (
                <iframe
                    style={{ borderRadius: '12px' }}
                    src={`https://open.spotify.com/embed/track/${trackId}?utm_source=generator`}
                    width="100%"
                    height="152"
                    frameBorder="0"
                    allowFullScreen=""
                    allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                    loading="lazy"
                    title="Spotify Player"
                ></iframe>
            ) : (
                <Typography variant="body2" sx={{ color: 'error.main', mt: 2 }}>
                    Unfortunately, nobody recognized the suggested band :(
                </Typography>
            )}
        </>
    );
}
