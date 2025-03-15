import {Paper} from "@mui/material";
import * as React from "react";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import {observer} from "mobx-react";
import {useContext} from "react";
import {RoomStoreContext} from "../../stores/room.js";
import {getOrSetPlayerUuid, RoundStage, setPlayerUuid, UserRole} from "../../lib/backend.js";
import {DebugUsersStoreContext} from "../../stores/debug-users.js";
import IconButton from "@mui/material/IconButton";
import {v4 as uuidv4} from "uuid";


const DebugUserRole = Object.freeze({
    GUEST:   Symbol("GUEST"),
    WAITER:  Symbol("WAITER"),
    SUGGEST_GROUP:  Symbol("SUGGEST_GROUP"),
    SUGGEST_TRACK:  Symbol("SUGGEST_TRACK"),
    ADMIN:  Symbol("ADMIN"),
});


class DebugUser {
    constructor(uuid, nickname, role, is_active) {
        this.uuid = uuid;
        this.nickname = nickname;
        this.role = role;
        this.is_active = is_active;
    }
}


function collectDebugUsers(roomStore, userStore) {
    let data = new Map();
    userStore.getUsers().forEach((user) => {
        let is_active = user.uuid === getOrSetPlayerUuid()
        data.set(user.uuid, new DebugUser(user.uuid, user.nickname, DebugUserRole.GUEST, is_active));
    })

    let room = roomStore.getRoom();
    if (!room || !room.players) {
        console.log("No players in room store: ", room)
        return data
    }

    room.players.forEach((player) => {
        let uuid = player.uuid;
        let round = room.state.currentRound;
        let is_active = player.uuid === getOrSetPlayerUuid()
        let role = DebugUserRole.ADMIN;
        if (player.role !== UserRole.ADMIN) {
            if (!round) {
                role = DebugUserRole.WAITER;
            } else if (round.stage === RoundStage.GROUP_SUGGESTION && round.suggester.uuid === uuid) {
                role = DebugUserRole.SUGGEST_GROUP;
            } else {
                role = DebugUserRole.SUGGEST_TRACK;
            }
        }
        data.set(uuid, new DebugUser(uuid, player.nickname, role, is_active));
    })
    return data
}


function getRoleString(role) {
    switch (role) {
        case DebugUserRole.GUEST:
            return "GUEST";
        case DebugUserRole.WAITER:
            return "WAITER";
        case DebugUserRole.SUGGEST_GROUP:
            return "SUGGEST_GROUP";
        case DebugUserRole.SUGGEST_TRACK:
            return "SUGGEST_TRACK";
        case DebugUserRole.ADMIN:
            return "ADMIN";
    }
}


const UserSwitcher = observer(() => {
    const roomStore = useContext(RoomStoreContext);
    const userStoreStore = useContext(DebugUsersStoreContext);

    let users = collectDebugUsers(roomStore, userStoreStore);

    let [newUserNickname, setNewUserNickname] = React.useState('');

    return (
        <Paper className={"user-switcher"}>
            <Box spacing={20}>
                <Typography className={"mb-5"} variant="h5" component="div">
                    Act under user
                </Typography>

                {Array.from(users.values()).map((user) => {
                    return (
                        <Box className={"user-switcher-row"} key={user.uuid}>
                            <TextField
                                label={getRoleString(user.role)}
                                value={user.nickname}
                                variant="standard"
                                onChange={(e) => userStoreStore.setNick(user.uuid, e.target.value)}
                            />
                            <Button
                                variant={user.is_active ? 'contained' : 'outlined'}
                                onClick={user.is_active ? null : () => setPlayerUuid(user.uuid)}
                            >
                                {user.is_active ? 'Active' : 'Switch'}
                            </Button>
                            <IconButton
                                aria-label="delete"
                                onClick={() => userStoreStore.removeUser(user.uuid)}
                                disabled={user.is_active}
                            >
                                <DeleteIcon />
                            </IconButton>
                        </Box>
                    );
                })}
                <Box className={"user-switcher-row"}>
                    <TextField
                        label="New user"
                        placeholder={"Enter nickname"}
                        value={newUserNickname}
                        variant="outlined"
                        onChange={(e) => setNewUserNickname(e.target.value)}
                    />
                    <IconButton
                        aria-label="add"
                        variant="outlined"
                        onClick={() => {
                            console.log("Adding new user: ", newUserNickname);
                            userStoreStore.setNick(uuidv4().toString(), newUserNickname);
                            setNewUserNickname('');
                        }}
                    >
                        <AddIcon />
                    </IconButton>
                </Box>
            </Box>
        </Paper>
    )
});

export default UserSwitcher;
