import {v4 as uuidv4} from 'uuid';

export const UserRole = Object.freeze({
    ADMIN:   Symbol("ADMIN"),
    PLAYER:  Symbol("PLAYER"),
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

function getOrSetPlayerUuid() {
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

    async increment(code, playerUuid) {
        return await fetch(`${this.url}/room/${code}/user/${getOrSetPlayerUuid()}/inc`, {
            method: 'POST',
            body: JSON.stringify({player_uuid: playerUuid}),
            headers: {
                'Content-Type': 'application/json'
            },
        });
        // TODO: update room store
    }

    async joinRoom(code, nickname) {
        const url = `${this.url}/room/${code}/join?` + new URLSearchParams({
            user_uuid: getOrSetPlayerUuid(),
            nickname: nickname,
        }.toString());
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
        return await fetch(`${this.url}/room`, {
            method: 'POST',
        })
            .then(response => response.json())
            .then(data => this.mapRoom(data));
        // TODO: update room store
    }

    mapRoom(data) {
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

const Client = new BackendClient('http://localhost:8000');
export default Client;
