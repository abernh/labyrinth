import { locationsEqual } from "@/model/game.js";

export default class Graph {
    constructor(game) {
        this.game = game;
        this._reachedLocations = [];
        for (var row = 0; row < this.game.n; row++) {
            this._reachedLocations.push([]);
            for (var col = 0; col < this.game.n; col++) {
                this._reachedLocations[row].push(false);
            }
        }
    }

    path(sourceLocation, targetLocation) {
        if (!this.game.isShifting) {
            this._setReached(sourceLocation, { parent: sourceLocation });
            let nextElements = [sourceLocation];
            var currentLocation;
            while ((currentLocation = nextElements.shift()) !== undefined) {
                if (locationsEqual(currentLocation, targetLocation)) {
                    return this._reachedToPath(currentLocation);
                }
                this._neighborLocations(currentLocation).forEach(neighbor => {
                    if (!this._getReached(neighbor)) {
                        this._setReached(neighbor, { parent: currentLocation });
                        nextElements.push(neighbor);
                    }
                });
            }
        }
        return [];
    }

    isReachable(sourceLocation, targetLocation) {
        let locations = this.reachableLocations(sourceLocation);
        for (var location of locations) {
            if (locationsEqual(location, targetLocation)) {
                return true;
            }
        }
        return false;
    }

    reachableLocations(sourceLocation) {
        if (!this.game.isShifting) {
            this._setReached(sourceLocation, true);
            let nextElements = [sourceLocation];
            let currentLocation;
            while ((currentLocation = nextElements.shift()) !== undefined) {
                this._neighborLocations(currentLocation).forEach(neighbor => {
                    if (!this._getReached(neighbor)) {
                        this._setReached(neighbor, true);
                        nextElements.push(neighbor);
                    }
                });
            }
        }
        return this._reachedToArray();
    }

    _neighborLocations(location) {
        let neighbors = [];
        let mazeCard = this.game.getMazeCard(location);
        let outPaths = this._outPaths(mazeCard);
        for (var outPath of outPaths) {
            let locationToTest = {
                row: location.row + outPath[0],
                column: location.column + outPath[1]
            };
            if (this.game.isInside(locationToTest)) {
                let cardToTest = this.game.getMazeCard(locationToTest);
                let mirroredOutPath = this._mirror(outPath[2]);
                if (cardToTest.hasRotationAwareOutPath(mirroredOutPath)) {
                    neighbors.push(locationToTest);
                }
            }
        }
        return neighbors;
    }

    _outPaths(mazeCard) {
        let result = [];
        if (mazeCard.hasRotationAwareOutPath("N")) {
            result.push([-1, 0, "N"]);
        }
        if (mazeCard.hasRotationAwareOutPath("E")) {
            result.push([0, 1, "E"]);
        }
        if (mazeCard.hasRotationAwareOutPath("S")) {
            result.push([1, 0, "S"]);
        }
        if (mazeCard.hasRotationAwareOutPath("W")) {
            result.push([0, -1, "W"]);
        }
        return result;
    }

    _mirror(outPath) {
        let outPaths = ["N", "E", "S", "W"];
        let mirroredIndex = (outPaths.indexOf(outPath) + 2) % 4;
        return outPaths[mirroredIndex];
    }

    _initReached() {
        let reached = [];
        for (var row = 0; row < this.game.n; row++) {
            reached.push([]);
            for (var col = 0; col < this.game.n; col++) {
                reached[row].push(false);
            }
        }
        return reached;
    }

    _getReached(location) {
        return this._reachedLocations[location.row][location.column];
    }

    _setReached(location, value) {
        this._reachedLocations[location.row][location.column] = value;
    }

    _reachedToArray() {
        let reached = [];
        for (var row = 0; row < this.game.n; row++) {
            for (var col = 0; col < this.game.n; col++) {
                if (this._reachedLocations[row][col]) {
                    reached.push({
                        row: row,
                        column: col
                    });
                }
            }
        }
        return reached;
    }

    _reachedToPath(location) {
        let path = [location];
        let current = location;
        while (!locationsEqual(this._getReached(current).parent, current)) {
            current = this._getReached(current).parent;
            path.push(current);
        }
        return path.reverse();
    }
}
