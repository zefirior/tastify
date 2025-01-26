import {v4 as uuidv4} from 'uuid';

export const UserRole = Object.freeze({
    ADMIN:   Symbol("ADMIN"),
    PLAYER:  Symbol("PLAYER"),
});

export const RoundStage = Object.freeze({
    GROUP_SUGGESTION:   Symbol("GROUP_SUGGESTION"),
    TRACKS_SUBMISSION:  Symbol("TRACKS_SUBMISSION"),
    END_ROUND:  Symbol("END_ROUND"),
});

export const RoomStatus = Object.freeze({
    NEW:       Symbol("NEW"),
    RUNNING:   Symbol("RUNNING"),
    FINISHED:  Symbol("FINISHED"),
});

class Player {
    constructor(nickname, score, role) {
        this.nickname = nickname;
        this.score = score;
        this.role = role;
    }
}

class Room {
    constructor(code, role, players) {
        this.code = code;
        this.role = role;
        this.players = players || [];
    }
}

export function getOrSetPlayerUuid() {
    const playerUuid = localStorage.getItem('playerUuid');
    if (playerUuid) {
        return playerUuid;
    }
    const newPlayerUuid = uuidv4().toString();
    localStorage.setItem('playerUuid', newPlayerUuid);
    return newPlayerUuid
}

class BackendClient {
    constructor(url) {
        this.url = url;
    }

    async startGame(code) {
        return await fetch(`${this.url}/room/${code}/start?user_uuid=${getOrSetPlayerUuid()}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
        });
        // TODO: update room store
    }

    async nextTurn(code) {
        return await fetch(`${this.url}/room/${code}/next_turn?user_uuid=${getOrSetPlayerUuid()}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
        });
        // TODO: update room store
    }

    async increment(code) {
        return await fetch(`${this.url}/room/${code}/user/${getOrSetPlayerUuid()}/increment`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
        });
        // TODO: update room store
    }

    async joinRoom(code, nickname) {
        const url = `${this.url}/room/${code}/join?user_uuid=${getOrSetPlayerUuid()}&nickname=${nickname}`;
        return await fetch(url,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
            });
    }

    async getRoom(code) {
        const url = `${this.url}/room/${code}?user_uuid=${getOrSetPlayerUuid()}`;
        return await fetch(url)
            .then(response => response.json())
            .then(data => this.mapRoom(data));
    }

    async createRoom() {
        return await fetch(`${this.url}/room?admin_uuid=${getOrSetPlayerUuid()}`, {
            method: 'POST',
        })
            .then(response => response.json())
            .then(data => this.mapRoom(data));
        // TODO: update room store
    }

    mapRoom(data) {
        console.log('Mapping room', data);
        return new Room(
            data.code,
            data.role === 'ADMIN' ? UserRole.ADMIN : UserRole.PLAYER,
            data.players.map(player => new Player(
                player.nickname,
                player.score,
                player.role === 'ADMIN' ? UserRole.ADMIN : UserRole.PLAYER
            )),
        );
    }
}

const url = import.meta.env['VITE_BACKEND_URL'] || 'http://localhost:8000';
const Client = new BackendClient(url);
export default Client;
