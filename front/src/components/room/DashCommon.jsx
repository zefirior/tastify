import {RoomStatus} from '../../lib/backend.js';
import DashNew from './DashNew.jsx';
import DashRunning from './DashRunning.jsx';

export default function DashCommon({room}) {
    return (
        <>
            {room.status === RoomStatus.NEW
                ? <DashNew room={room} />
                : <DashRunning room={room} />}
        </>
    );
}
