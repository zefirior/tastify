import {action, makeAutoObservable, makeObservable, observable, observe} from 'mobx';
import {createContext} from 'react';
import {getOrSetPlayerUuid} from "../lib/backend.js";

class DebugUser {
    constructor(uuid, nickname) {
        this.uuid = uuid;
        this.nickname = nickname;
    }
}

const DEBUG_USERS_KEY = 'debugUsers';

class DebugUsersStore {
    touch = 0;

    constructor() {
        makeAutoObservable(this);
        this.value = 0;

        if (!localStorage.getItem(DEBUG_USERS_KEY)) {
            this.#setData(new Map());
        }
    }

    setNick(uuid, nickname) {
        let user = new DebugUser(uuid, nickname);
        this.setUser(user);
    }

    setUser(user) {
        let data = this.#getData();
        data.set(user.uuid, user)
        this.#setData(data);
    }

    setIfNotExists(user) {
        if (!this.getUser(user.uuid)) {
            this.setUser(user)
        }
    }

    getUser(uuid) {
        this.#ensureCurrentUserInStore()
        let ignore = this.touch
        return this.#getData().get(uuid)
    }

    removeUser(uuid) {
        let data = this.#getData();
        data.delete(uuid)
        this.#setData(data);
    }

    getUsers() {
        this.#ensureCurrentUserInStore()
        let ignore = this.touch
        return Array.from(this.#getData().values())
    }

    #ensureCurrentUserInStore() {
        const currentUser = getOrSetPlayerUuid();
        if (!this.#getData().get(currentUser)) {
            this.setUser(new DebugUser(currentUser, 'me (auto)'))
        }
    }

    #setData(data) {
        let str = JSON.stringify(Object.fromEntries(data));
        localStorage.setItem(DEBUG_USERS_KEY, str);
        this.touch++;
    }

    #getData() {
        let str = localStorage.getItem(DEBUG_USERS_KEY);
        return new Map(Object.entries(JSON.parse(str)));
    }
}

export const debugUsersStore = new DebugUsersStore();
export const DebugUsersStoreContext = createContext(debugUsersStore);