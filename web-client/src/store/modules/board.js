import Vue from "vue";

export const state = () => ({
    mazeSize: 0,
    cardsById: {},
    boardLayout: [],
    leftoverId: null,
    disabledShiftLocation: null
});

export const getters = {
    mazeCardById: state => id => {
        return state.cardsById[id];
    },
    leftoverMazeCard: state => {
        return leftoverMazeCard(state);
    },
    mazeCard: state => location => {
        return mazeCardAtLocation(state, location);
    },
    isInside: state => location => {
        return isInside(location, state.mazeSize);
    },
    oppositeLocation: state => location => {
        return getOppositeLocation(location, state.mazeSize);
    },
    mazeCardsRowMajorOrder: (state, getters) => {
        return [].concat.apply([], state.boardLayout).map(getters.mazeCardById);
    }
};

const actions = {
    update({ commit }, apiState) {
        commit("emptyBoard");
        commit("fillBoard", apiState);
        const n = apiState.maze.mazeSize;
        const enabledShiftLocations = apiState.enabledShiftLocations;
        const disabledShiftLocation = findDisabledShiftLocation(n, enabledShiftLocations);
        commit("setDisabledShiftLocation", disabledShiftLocation);
        commit("setPlayersOnCardsFromApi", apiState.players);
    },
    movePlayer({ commit, getters }, move) {
        const sourceCard = getters.mazeCardById(move.sourceCardId);
        const playerIndexInSource = sourceCard.playerIds.indexOf(move.playerId);
        commit("movePlayer", { ...move, playerIndex: playerIndexInSource });
    },
    shift({ commit, getters, state }, shiftAction) {
        const location = shiftAction.location;
        if (locationsEqual(location, state.disabledShiftLocation)) {
            throw new ValueError("Shifting at " + location + " is not allowed.");
        }

        const n = state.mazeSize;

        let shiftLocations = generateShiftLocations(location, n);
        if (shiftLocations.length === n) {
            commit("setLeftoverRotation", shiftAction.leftoverRotation);
            commit("shiftAlongLocations", shiftLocations);
            commit("setDisabledShiftLocation", getOppositeLocation(location, n));
            commit("transferPlayers", {
                source: getters.leftoverMazeCard.id,
                target: getters.mazeCard(location).id
            });
        } else {
            throw new ValueError();
        }
    },
    rotateLeftoverClockwise({ commit, state }) {
        const oldRotation = state.cardsById[state.leftoverId].rotation;
        commit("setLeftoverRotation", (oldRotation + 90) % 360);
    }
};

export const mutations = {
    emptyBoard(state) {
        state.boardLayout.splice(0, state.boardLayout.length);
    },
    fillBoard(state, apiState) {
        state.mazeSize = apiState.maze.mazeSize;
        const apiMazeCards = apiState.maze.mazeCards;
        if (!apiMazeCards) {
            return;
        }
        if (state.leftoverId !== apiMazeCards[0].id) {
            state.leftoverId = apiMazeCards[0].id;
            Vue.set(state.cardsById, state.leftoverId, createCardFromApi(apiMazeCards[0]));
        }
        const n = apiState.maze.mazeSize;
        let index = 1;
        for (let row = 0; row < n; row++) {
            state.boardLayout.push([]);
            for (let col = 0; col < n; col++) {
                Vue.set(
                    state.cardsById,
                    apiMazeCards[index].id,
                    createCardFromApi(apiMazeCards[index])
                );
                state.boardLayout[row].push(apiMazeCards[index].id);
                index++;
            }
        }
    },
    setDisabledShiftLocation(state, shiftLocation) {
        state.disabledShiftLocation = shiftLocation;
    },
    setPlayersOnCardsFromApi(state, apiPlayers) {
        for (const player of apiPlayers) {
            state.cardsById[player.mazeCardId].playerIds.push(player.id);
        }
    },
    movePlayer(state, move) {
        const sourceId = move.sourceCardId;
        const targetId = move.targetCardId;
        state.cardsById[sourceId].playerIds.splice(move.playerIndex, 1);
        state.cardsById[targetId].playerIds.push(move.playerId);
    },
    shiftAlongLocations(state, locations) {
        const n = state.mazeSize;
        const pushedOut = locations[n - 1];
        const inserted = locations[0];
        let layout = state.boardLayout;
        let oldLeftoverId = state.leftoverId;
        state.leftoverId = layout[pushedOut.row][pushedOut.column];
        for (let i = n - 1; i > 0; i--) {
            const from = locations[i - 1];
            const to = locations[i];
            layout[to.row][to.column] = layout[from.row][from.column];
            setLocation(state, idAtLocation(state, to), to);
        }
        setLocation(state, oldLeftoverId, inserted);
        layout[inserted.row][inserted.column] = oldLeftoverId;
        setLocation(state, state.leftoverId, null);
    },
    transferPlayers(state, transfer) {
        const sourceMazeCard = state.cardsById[transfer.source];
        const targetMazeCard = state.cardsById[transfer.target];
        while (sourceMazeCard.playerIds.length) {
            targetMazeCard.playerIds.push(sourceMazeCard.playerIds.pop());
        }
    },
    setLeftoverRotation(state, rotation) {
        state.cardsById[state.leftoverId].rotation = rotation;
    }
};

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
};

export function mazeCardAtLocation(state, location) {
    if (isInside(location, state.mazeSize)) {
        const id = state.boardLayout[location.row][location.column];
        return state.cardsById[id];
    } else {
        throw new RangeError();
    }
}

function setLocation(state, cardId, location) {
    state.cardsById[cardId] = { ...state.cardsById[cardId], location: location };
}

function idAtLocation(state, location) {
    if (isInside(location, state.mazeSize)) {
        return state.boardLayout[location.row][location.column];
    } else {
        throw new RangeError();
    }
}

export function isInside(location, mazeSize) {
    return (
        location.row >= 0 &&
        location.row < mazeSize &&
        location.column >= 0 &&
        location.column < mazeSize
    );
}

function createCardFromApi(apiCard) {
    return { ...apiCard, playerIds: [] };
}

function generateShiftLocations(location, n) {
    let shiftLocations = [];
    if (location.row === 0) {
        shiftLocations = columnLocations(location.column, n);
    } else if (location.row === n - 1) {
        shiftLocations = columnLocations(location.column, n);
        shiftLocations.reverse();
    } else if (location.column === n - 1) {
        shiftLocations = rowLocations(location.row, n);
        shiftLocations.reverse();
    } else if (location.column === 0) {
        shiftLocations = rowLocations(location.row, n);
    }
    return shiftLocations;
}

function findDisabledShiftLocation(n, apiShiftLocations) {
    let allShiftLocations = getShiftLocations(n);
    for (let location of allShiftLocations) {
        if (!apiShiftLocations.find(apiLocation => locationsEqual(apiLocation, location))) {
            return location;
        }
    }
    return null;
}

export function locationsEqual(locationA, locationB) {
    return locationA?.row === locationB?.row && locationA?.column == locationB?.column;
}

export function getShiftLocations(n) {
    let allShiftLocations = [];
    for (let position = 1; position < n - 1; position += 2) {
        allShiftLocations.push({ row: 0, column: position });
        allShiftLocations.push({ row: position, column: 0 });
        allShiftLocations.push({ row: n - 1, column: position });
        allShiftLocations.push({ row: position, column: n - 1 });
    }
    return allShiftLocations;
}

function columnLocations(column, n) {
    var locations = [];
    for (let row = 0; row < n; row++) {
        locations.push({ row: row, column: column });
    }
    return locations;
}

function rowLocations(row, n) {
    var locations = [];
    for (let column = 0; column < n; column++) {
        locations.push({ row: row, column: column });
    }
    return locations;
}

function getOppositeLocation(borderLocation, n) {
    let oppositeLocation = null;
    if (borderLocation.row === 0) {
        oppositeLocation = { row: n - 1, column: borderLocation.column };
    } else if (borderLocation.row === n - 1) {
        oppositeLocation = { row: 0, column: borderLocation.column };
    } else if (borderLocation.column === n - 1) {
        oppositeLocation = { row: borderLocation.row, column: 0 };
    } else if (borderLocation.column === 0) {
        oppositeLocation = { row: borderLocation.row, column: n - 1 };
    }
    return oppositeLocation;
}

function leftoverMazeCard(state) {
    return state.cardsById[state.leftoverId];
}

export function loc(row, column) {
    return { row: row, column: column };
}
