import '../App.css';
import Page from './Page.jsx';
import {useNavigate, useParams} from 'react-router';
import {useContext, useEffect, useRef} from 'react';
import { observer } from "mobx-react";
import Client, {getJoinRoomPath, getJoinRoomUrl, getOrSetPlayerUuid, RoomStatus, UserRole} from '../lib/backend.js';
import {RoomStoreContext} from '../stores/room.js';
import DashCommon from '../components/room/DashCommon.jsx';
import PlayerCommon from '../components/room/PlayerCommon.jsx';

const Room = observer(() => {
    const {roomCode} = useParams();

    const store = useContext(RoomStoreContext);
    const pollingRef = useRef(null);
    const navigate = useNavigate();

    useEffect(() => {
        const startPolling = () => {
            pollingRef.current = setInterval(async () => {
                try {
                    const room = await Client.getRoom(roomCode);
                    store.setRoom(room);
                } catch (error) {
                    console.error(error.message);
                }
            }, 2000); // Poll every 0.25 seconds
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

    if (room.status === RoomStatus.FINISHED) {
        return navigate('/');
    }
    if (!room.role) {
        return navigate(getJoinRoomPath(room.code));
    }

    return (
        <Page>
            {room.role === UserRole.ADMIN
                ? <DashCommon room={room} />
                : <PlayerCommon room={room} />}
        </Page>
    );
});

export default Room;
