import '../App.css';
import Page from './Page.jsx';
import {Link, useParams} from 'react-router';

export default function Room() {
    const {roomCode} = useParams();

    return (
        <Page>
            <h1>{`Room ${roomCode}`}</h1>
            <Link to='/'>Home</Link>
        </Page>
    );
}
