import '../App.css';
import Page from './Page.jsx';
import ChooseGame from '../components/ChooseGame.jsx';
import {useNavigate, useParams} from 'react-router';
import {useEffect, useState} from 'react';
import Client from '../lib/backend.js';

export default function JoinRoom() {
    const {roomCode} = useParams();
    const navigate = useNavigate();
    let [goToRoom, setGoToRoom] = useState(false);

    if (goToRoom) {
        navigate(`/room/${roomCode}`);
    }

    useEffect(() => {
        Client.getRoom(roomCode)
            .then((room) => {
                if (room.role) {
                    setGoToRoom(true);
                }
            })
    }, [roomCode]);

    return (
        <Page>
            <ChooseGame
                roomCode={roomCode}
            />
        </Page>
    );
}
