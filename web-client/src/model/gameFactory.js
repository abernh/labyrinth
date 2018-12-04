import Game from "@/model/game.js";
import MazeCard from "@/model/mazecard.js";
import Player from "@/model/player.js";

export default class GameFactory {
    constructor(initialPlayerLocations) {
        if (initialPlayerLocations === undefined) {
            initialPlayerLocations = [];
        }
        this._initialPlayerLocations = initialPlayerLocations;
    }

    createGame() {
        var game = new Game();

        var id = 0;
        for (var row = 0; row < game.n; row++) {
            game.mazeCards.push([]);
            for (var col = 0; col < game.n; col++) {
                game.mazeCards[row].push(
                    MazeCard.createNewRandom(id, row, col)
                );
                id++;
            }
        }

        if (this._initialPlayerLocations.length === 0) {
            this._initialPlayerLocations.push({
                row: Math.floor(Math.random() * game.n),
                column: Math.floor(Math.random() * game.n)
            });
        }

        for (var i = 0; i < this._initialPlayerLocations.length; i++) {
            let location = this._initialPlayerLocations[i];
            let playerMazeCard = game.getMazeCard(location);
            let player = new Player(i, playerMazeCard, i);
            playerMazeCard.addPlayer(player);
            game.addPlayer(player);
        }

        game.leftoverMazeCard = MazeCard.createNewRandom(id, -1, -1);
        return game;
    }
}
