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
    constructor(uuid, nickname, role) {
        this.uuid = uuid;
        this.nickname = nickname;
        this.role = role;
    }
}

class CurrentRound {
    constructor(timeLeft, groupName, stage, suggester, submissions) {
        this.timeLeft = timeLeft;
        this.groupName = groupName;
        this.stage = stage;
        this.suggester = suggester;
        this.submittions = submissions;
    }
}

class RoomState {
    constructor(currentRound, totalResults) {
        this.currentRound = currentRound;
        this.totalResults = totalResults;
    }
}

class Room {
    constructor(code, role, status, players, state) {
        this.code = code;
        this.role = role;
        this.status = status;
        this.players = players || [];
        this.state = state;
    }

    getPlayerScore(playerUuid) {
        if (!this.state) {
            return 0;
        }
        if (!this.state.totalResults) {
            return 0;
        }
        return this.state.totalResults[playerUuid] || 0;
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

    async searchGroup(query) {
        let options = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
        };
        return await fetch(`${this.url}/search/group?q=${query}`, options)
            .then(response => response.json());
    }

    async searchTrack(groupName, query) {
        let options = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
        };
        return await fetch(`${this.url}/search/track?group_id=${groupName}&q=${query}`, options)
            .then(response => response.json());
    }

    async submitGroup(code, groupId) {
        return await fetch(`${this.url}/room/${code}/submit/group?user_uuid=${getOrSetPlayerUuid()}&group_id=${groupId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
        });
        // TODO: update room store
    }

    async submitTrack(code, trackId) {
        return await fetch(`${this.url}/room/${code}/submit/track?user_uuid=${getOrSetPlayerUuid()}&track_id=${trackId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
        });
        // TODO: update room store
    }

    async skipTrack(code) {
        return await fetch(`${this.url}/room/${code}/submit/track?user_uuid=${getOrSetPlayerUuid()}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
        });
        // TODO: update room store
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
        return await fetch(`${this.url}/room/${code}/next-round?user_uuid=${getOrSetPlayerUuid()}`, {
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
        return new Room(
            data.code,
            this.mapRole(data.role),
            this.mapStatus(data.status),
            data.players.map(player => this.mapPlayer(player)),
            this.mapState(data.game_state),
        );
    }

    mapState(data) {
        if (!data) {
            return null;
        }

        return new RoomState(
            this.mapCurrentRound(data.current_round),
            data.total_results,
        );
    }

    mapCurrentRound(data) {
        if (!data) {
            return null;
        }

        return new CurrentRound(
            data.timeleft,
            data.group_id,
            this.mapStage(data.current_stage),
            new Player(data.suggester.uuid, data.suggester.nickname, UserRole.PLAYER),
            data.submissions,
        );
    }

    mapPlayer(data) {
        return new Player(
            data.uuid,
            data.nickname,
            this.mapRole(data.role),
        );
    }

    mapRole(rawRole) {
        switch (rawRole) {
            case 'ADMIN':
                return UserRole.ADMIN;
            case 'PLAYER':
                return UserRole.PLAYER;
        }
    }

    mapStage(rawStage) {
        switch (rawStage) {
            case 'GROUP_SUGGESTION':
                return RoundStage.GROUP_SUGGESTION;
            case 'TRACKS_SUBMISSION':
                return RoundStage.TRACKS_SUBMISSION;
            case 'END_ROUND':
                return RoundStage.END_ROUND;
        }
    }

    mapStatus(rawStatus) {
        switch (rawStatus) {
            case 'NEW':
                return RoomStatus.NEW;
            case 'RUNNING':
                return RoomStatus.RUNNING;
            case 'FINISHED':
                return RoomStatus.FINISHED;
        }
    }
}

const url = import.meta.env['VITE_BACKEND_URL'] || 'http://localhost:8000';
const Client = new BackendClient(url);
export default Client;
