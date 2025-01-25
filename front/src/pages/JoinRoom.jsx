import '../App.css';
import Page from './Page.jsx';
import ChooseGame from '../components/ChooseGame.jsx';
import {useParams} from "react-router";

export default function JoinRoom() {
    const {roomCode} = useParams();

    return (
        <Page>
            <ChooseGame
                roomCode={roomCode}
            />
        </Page>
    );
}
