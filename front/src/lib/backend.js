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
    constructor(code, randomNumber, role, players) {
        this.code = code;
        this.randomNumber = randomNumber;
        this.role = role;
        this.players = players || [];
    }
}

class BackendClient {
    constructor(url) {
        this.url = url;
    }

    async increment(code, playerUuid) {
        return await fetch(`${this.url}/room/${code}/user/${playerUuid}/increment`, {
            method: 'POST',
            body: JSON.stringify({player_uuid: playerUuid}),
            headers: {
                'Content-Type': 'application/json'
            },
        });
        // TODO: update room store
    }

    async getRoom(code) {
        return await fetch(`${this.url}/room/${code}`)
            .then(response => response.json())
            .then(data => this.mapRoom(data));
    }

    async createRoom() {
        return await fetch(`${this.url}/room`, {
            method: 'POST',
        })
            .then(response => response.json())
            .then(data => this.mapRoom(data));
    }

    mapRoom(data) {
        return new Room(
            data.room_code,
            data.random_number,
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
