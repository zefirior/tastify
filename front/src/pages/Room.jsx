import '../App.css';
import Page from './Page.jsx';
import {Link, useParams} from 'react-router';
import {useEffect, useRef, useState} from 'react';

export default function Room() {
    const {roomCode} = useParams();
    const [randomNumber, setRandomNumber] = useState('null');

    const pollingRef = useRef(null);

    useEffect(() => {
        const url = `http://localhost:8000/room/${roomCode}`;
        const startPolling = () => {
            pollingRef.current = setInterval(async () => {
                console.log('Polling...');
                try {
                    const response = await fetch(url);
                    if (!response.ok) {
                        throw new Error(`Response status: ${response.status}`);
                    }

                    const json = await response.json();
                    console.log(json);
                    setRandomNumber(json.random_number);
                } catch (error) {
                    console.error(error.message);
                }
            }, 1000); // Poll every 1 seconds
        };
        startPolling();

        return () => {
            console.log('Clearing interval...');
            clearInterval(pollingRef.current);
        };
    }, [roomCode]);

    return (
        <Page>
            <h1>{`Room ${roomCode}: ${randomNumber}`}</h1>
            <Link to='/'>Home</Link>
        </Page>
    );
}
