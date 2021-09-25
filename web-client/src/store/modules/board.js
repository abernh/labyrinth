export const state = () => ({
    mazeSize: 0,
    cardsById: {},
    boardLayout: [],
    leftoverId: null,
    disabledShiftLocation: null
});

export const getters = {
    find: state => id => {
        return state.cardsById[id];
    },
    mazeCard: (state, getters) => location => {
        if (getters.isInside(location)) {
            const id = state.boardLayout[location.row][location.column];
            return state.cardsById[id];
        } else {
            throw new RangeError();
        }
    },
    isInside: state => location => {
        return (
            location.row >= 0 &&
            location.row < state.mazeSize &&
            location.column >= 0 &&
            location.column < state.mazeSize
        );
    }
};

const actions = {};

export const mutations = {
    update(state, apiState) {
        initializeBoard(state);
        const n = apiState.maze.mazeSize;
        state.mazeSize = n;
        fillBoard(state, apiState);
        const enabledShiftLocations = apiState.enabledShiftLocations;
        state.disabledShiftLocation = findDisabledShiftLocation(n, enabledShiftLocations);
        setPlayersOnCards(state, apiState.players);
    },
    move(state, move) {
        const sourceId = move.sourceCardId;
        const targetId = move.targetCardId;
        const player = move.playerId;
        const index = state.cardsById[sourceId].playerIds.indexOf(player);
        state.cardsById[sourceId].playerIds.splice(index, 1);
        state.cardsById[targetId].playerIds.push(player);
    }
};

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
};

function findDisabledShiftLocation(n, apiShiftLocations) {
    let allShiftLocations = getShiftLocations(n);
    for (let location of allShiftLocations) {
        if (!apiShiftLocations.find(apiLocation => locationEqual(apiLocation, location))) {
            return location;
        }
    }
    return null;
}

function locationEqual(locationA, locationB) {
    return locationA.row === locationB.row && locationA.column == locationB.column;
}

function getShiftLocations(n) {
    let allShiftLocations = [];
    for (let position = 1; position < n - 1; position += 2) {
        allShiftLocations.push({ row: 0, column: position });
        allShiftLocations.push({ row: position, column: 0 });
        allShiftLocations.push({ row: n - 1, column: position });
        allShiftLocations.push({ row: position, column: n - 1 });
    }
    return allShiftLocations;
}

function setPlayersOnCards(state, apiPlayers) {
    for (const player of apiPlayers) {
        state.cardsById[player.mazeCardId].playerIds.push(player.id);
    }
}

function fillBoard(state, apiState) {
    const apiMazeCards = apiState.maze.mazeCards;
    state.leftoverId = apiMazeCards[0].id;
    state.cardsById[state.leftoverId] = apiMazeCards[0];
    const n = apiState.maze.mazeSize;
    let index = 1;
    for (let row = 0; row < n; row++) {
        state.boardLayout.push([]);
        for (let col = 0; col < n; col++) {
            state.boardLayout[row].push(apiMazeCards[index].id);
            state.cardsById[apiMazeCards[index].id] = apiMazeCards[index];
            state.cardsById[apiMazeCards[index].id].playerIds = [];
            index++;
        }
    }
    return n;
}

function initializeBoard(state) {
    state.cardsById = {};
    state.boardLayout.splice(0, state.boardLayout.length);
}
