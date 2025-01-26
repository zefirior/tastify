import '../App.css';
import Page from './Page.jsx';
import {useParams} from 'react-router';
import {useContext, useEffect, useRef} from 'react';
import { observer } from "mobx-react";
import Client, {UserRole} from '../lib/backend.js';
import {RoomStoreContext} from '../stores/room.js';
import PlayerBoard from '../components/PlayerBoard.jsx';
import Dashboard from '../components/Dashboard.jsx';

const Room = observer(() => {
    const {roomCode} = useParams();

    const store = useContext(RoomStoreContext);
    const pollingRef = useRef(null);

    useEffect(() => {
        const startPolling = () => {
            pollingRef.current = setInterval(async () => {
                console.log('Polling...');
                try {
                    const room = await Client.getRoom(roomCode);
                    store.setRoom(room);
                } catch (error) {
                    console.error(error.message);
                }
            }, 250); // Poll every 0.25 seconds
        };
        startPolling();

        return () => {
            console.log('Clearing interval...');
            clearInterval(pollingRef.current);
            store.clear();
        };
    }, [roomCode, store]);

    if (!store.getRoom()) {
        return (
            <Page>
                <h1>{`Room ${roomCode}: Loading...`}</h1>
            </Page>
        );
    }
    const room = store.getRoom();
    console.log('Rendering room', room);
    return (
        <Page>
            {room.role === UserRole.ADMIN
                ? <Dashboard room={room} />
                : <PlayerBoard room={room} />}
        </Page>
    );
});

export default Room;
