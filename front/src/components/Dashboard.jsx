import * as React from 'react';
import PlayersGrid from './PlayersGrid.jsx';
import QRCode from 'react-qr-code';

export default function Dashboard({room}) {
    return (
        <>
            <h1>Game dashboard: {room.code}</h1>
            <h2>Scan to join</h2>
            <QRCode
                title="Scan to join"
                value={`${import.meta.env['VITE_BASE_URL']}/room/${room.code}/join`}
            />
            <PlayersGrid players={room.players} />
        </>
    );
}