import { state, getters, mutations } from "@/store/modules/board.js";
import { loc } from "../testutils.js";

describe("mutations", () => {
    describe("update", () => {
        it("sets maze size correctly", () => {
            givenInitialBoardState();
            givenApiStateWithSize3();

            whenSetBoardFromApi();

            thenBoardSizeIs(3);
        });

        it("sets maze card id in 2d array correctly", () => {
            givenInitialBoardState();
            givenApiStateWithSize3();

            whenSetBoardFromApi();

            expect(getMazeCard(loc(1, 0))).toBe(3);
        });

        it("sets card by id correctly", () => {
            givenInitialBoardState();
            givenApiStateWithSize3();

            whenSetBoardFromApi();

            expect(board.cardsById["3"]).toEqual(
                expect.objectContaining({
                    outPaths: "NE",
                    id: 3,
                    location: {
                        column: 0,
                        row: 1
                    },
                    rotation: 180
                })
            );
        });

        it("sets leftover maze card id correctly", () => {
            givenInitialBoardState();
            givenApiStateWithSize3();

            whenSetBoardFromApi();

            expect(board.leftoverId).toBe(9);
        });

        it("disables shift location, if enabled locations is missing one", () => {
            givenInitialBoardState();
            givenApiStateWithSize3();

            whenSetBoardFromApi();

            expect(board.disabledShiftLocation).toEqual(loc(2, 1));
        });

        it("sets disabled shift location to null if all locations are enabled", () => {
            givenInitialBoardState();
            givenApiStateWithoutDisabledShiftLocations();

            whenSetBoardFromApi();

            expect(board.disabledShiftLocation).toEqual(null);
        });

        it("puts player ids on maze card", () => {
            givenInitialBoardState();
            givenApiStateWithSize3();

            whenSetBoardFromApi();
            const playerIds = board.cardsById["2"].playerIds;
            expect(Array.isArray(playerIds)).toBe(true);
            expect(new Set(playerIds)).toEqual(new Set([42, 17]));
            expect(playerIds.length).toBe(2);
        });

        it("leaves empty maze card player-ids empty", () => {
            givenInitialBoardState();
            givenApiStateWithSize3();

            whenSetBoardFromApi();
            expect(board.cardsById["3"].playerIds).toEqual([]);
        });

        it("overwrites existing state", () => {
            givenExistingBoardStateWithSize5();
            givenApiStateWithSize3();

            whenSetBoardFromApi();

            thenBoardSizeIs(3);
            expect(board.boardLayout[0][0]).toEqual(0);
            expect(board.cardsById).not.toHaveProperty("100");
            expect(board.cardsById).toHaveProperty("1");
            expect(board.cardsById["8"].playerIds).toEqual([]);
        });
    });
});

const { update } = mutations;

let board;
let apiState;

const givenInitialBoardState = function() {
    board = state();
};

const givenExistingBoardStateWithSize5 = function() {
    board = state();
    board.mazeSize = 5;
    let id = 8;
    for (let row = 0; row < board.mazeSize; row++) {
        board.boardLayout.push([]);
        for (let col = 0; col < board.mazeSize; col++) {
            const card = {
                id: id,
                location: { row: row, column: col },
                rotation: 0,
                outPaths: "NES"
            };
            board.boardLayout[row].push(card.id);
            board.cardsById[card.id] = card;
            board.cardsById[card.id].playerIds = [];
            id++;
        }
    }
    board.cardsById[8].playerIds = [1, 2, 3, 4, 5];
};

const givenApiStateWithSize3 = function() {
    apiState = JSON.parse(GET_STATE_RESULT_FOR_N_3);
};

const givenApiStateWithoutDisabledShiftLocations = function() {
    givenApiStateWithSize3();
    apiState.enabledShiftLocations.push(loc(2, 1));
};

const whenSetBoardFromApi = function() {
    update(board, apiState);
};

const thenBoardSizeIs = function(size) {
    expect(board.mazeSize).toEqual(size);
    expect(board.boardLayout.length).toEqual(size);
    for (let row = 0; row < size; row++) {
        expect(board.boardLayout[row].length).toEqual(size);
    }
};

const getMazeCard = function(location) {
    return board.boardLayout[location.row][location.column];
};

const GET_STATE_RESULT_FOR_N_3 = `{
    "maze": {
      "mazeSize": 3,
      "mazeCards": [{
          "outPaths": "NES",
          "id": 9,
          "location": null,
          "rotation": 0
      }, {
          "outPaths": "NES",
          "id": 0,
          "location": {
          "column": 0,
          "row": 0
          },
          "rotation": 180
      }, {
          "outPaths": "NE",
          "id": 1,
          "location": {
          "column": 1,
          "row": 0
          },
          "rotation": 180
      }, {
          "outPaths": "NS",
          "id": 2,
          "location": {
          "column": 2,
          "row": 0
          },
          "rotation": 90
      }, {
          "outPaths": "NE",
          "id": 3,
          "location": {
          "column": 0,
          "row": 1
          },
          "rotation": 180
      }, {
          "outPaths": "NE",
          "id": 4,
          "location": {
          "column": 1,
          "row": 1
          },
          "rotation": 270
      }, {
          "outPaths": "NS",
          "id": 5,
          "location": {
          "column": 2,
          "row": 1
          },
          "rotation": 0
      }, {
          "outPaths": "NS",
          "id": 6,
          "location": {
          "column": 0,
          "row": 2
          },
          "rotation": 180
      }, {
          "outPaths": "NES",
          "id": 7,
          "location": {
          "column": 1,
          "row": 2
          },
          "rotation": 180
      }, {
          "outPaths": "NE",
          "id": 8,
          "location": {
          "column": 2,
          "row": 2
          },
          "rotation": 0
      }]
    },
    "enabledShiftLocations": [
      {"column": 1, "row": 0},
      {"column": 0, "row": 1},
      {"column": 2, "row": 1}
    ],
    "players": [{
            "id": 42,
            "mazeCardId": 2,
            "pieceIndex": 0
          },{
            "id": 17,
            "pieceIndex": 1,
            "mazeCardId": 2
          }]
  }`;