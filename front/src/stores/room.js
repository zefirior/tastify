import { makeAutoObservable } from 'mobx';
import {createContext} from 'react';

class RoomStore {
    room = null; // The State

    constructor() {
        makeAutoObservable(this);
    }

    setRoom(room) {
        this.room = room
    }

    getRoom() {
        return this.room
    }

    clear() {
        this.room = null
    }
}

export const roomStore = new RoomStore();
export const RoomStoreContext = createContext(roomStore);