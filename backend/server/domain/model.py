""" The model of the game.

Game is the container for the entire state.
It consists of a Board, a leftover MazeCard, and a list of Players

Board manages the current state of the board, it manages a 2-d array of MazeCards.

MazeCard represents a single maze card, with outward connections and a rotation.

A Player represents a player, with a unique ID
and a reference to a maze card the piece is currently positioned on.
BoardLocation is a wrapper for a row and a column.
"""
from itertools import cycle, islice
from random import choice, randint
from .exceptions import InvalidStateException, PlayerNotFoundException, \
    InvalidLocationException, InvalidShiftLocationException, \
    MoveUnreachableException, InvalidRotationException
from .validation import MoveValidator


class BoardLocation:
    """A board location, defined by the row and the column.
    The location does now know the extent of the board"""

    def __init__(self, row, column):
        self.row = row
        self.column = column

    def add(self, row_delta, column_delta):
        """ Returns a new BoardLocation by adding the deltas to the current location """
        return BoardLocation(self.row + row_delta, self.column + column_delta)

    def __eq__(self, other):
        return isinstance(self, type(other)) and \
            self.column == other.column and \
            self.row == other.row

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.row, self.column))

    def __str__(self):
        return "({}, {})".format(self.row, self.column)


class Player:
    """ Represents a player
    Each player has a unique ID and,
    if positioned on the board, a reference to a MazeCard instance
    """

    def __init__(self, identifier=0, maze_card=None):
        self._id = identifier
        self.maze_card = maze_card

    @property
    def identifier(self):
        """ Getter for read-only identifier """
        return self._id


class MazeCard:
    """ Represents one maze card
    The doors field defines the type of the card.
    It is a string made up of the letters 'N', 'E', 'S', 'W', defining the paths
    going out of this maze card in the directions Up, Right, Down and Left, respectively.
    There are three types of cards, the straight line (NS), the corner(NE) and the T-junction (NES).
    A card also has a rotation in degrees, one of 0, 90, 180, and 270.
    This rotation has to be taken into account when determining the actual outgoing connections.
    Each MazeCard is identified with a unique ID.
    """
    STRAIGHT = "NS"
    CORNER = "NE"
    T_JUNCT = "NES"
    next_id = 0
    _DIRECTION_TO_DOOR = {(-1, 0): "N", (0, 1): "E", (1, 0): "S", (0, -1): "W"}

    def __init__(self, identifier=0, doors=STRAIGHT, rotation=0):
        self._doors = doors
        self._rotation = rotation
        self._id = identifier

    @property
    def identifier(self):
        """ Getter of read-only identifier """
        return self._id

    @property
    def rotation(self):
        """ Getter of rotation """
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        """ Setter of rotation, validates new value """
        if value % 90 != 0:
            raise InvalidRotationException("Rotation {} is not divisible by 90".format(value))
        self._rotation = value % 360

    @property
    def doors(self):
        """ Getter of read-only doors """
        return self._doors

    def has_out_path(self, direction):
        """ Returns whether there is an outgoing path
        in a given direction, taking the rotation into account.

        :param direction: a tuple describing the direction of the path, e.g. (-1, 0) for north
        :return: true iff there is a path in the given direction
        """
        door = self._DIRECTION_TO_DOOR[direction]
        door_index = "NESW".find(door)
        turns = (self._rotation // 90)
        adapted_index = (door_index - turns + 4) % 4
        adapted_door = "NESW"[adapted_index]
        return adapted_door in self._doors

    def out_paths(self):
        """ Returns an iterator over all directions
        with outgoing paths, taking rotation into account.
        """
        for direction in self._DIRECTION_TO_DOOR:
            if self.has_out_path(direction):
                yield direction

    @classmethod
    def reset_ids(cls):
        """ Resets the instance counter, such that a newly generated instance will have ID of 0 """
        cls.next_id = 0

    @classmethod
    def generate_random(cls, doors=None, rotation=None):
        """Generates a new instance, with autoincreasing ID.

        If parameters are None, they are set randomly.
        """
        if doors is None:
            doors = choice([cls.STRAIGHT, cls.CORNER, cls.T_JUNCT])
        if rotation is None:
            rotation = choice([0, 90, 180, 270])
        maze_card = MazeCard(cls.next_id, doors, rotation)
        cls.next_id = cls.next_id + 1
        return maze_card


class Board:
    """ Represent the state of the board.
    The state is maintained in a 2-d array of MazeCard instances.
    """

    BOARD_SIZE = 7

    def __init__(self):
        self._maze_cards = [[None for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        self._insert_locations = set()
        for position in range(1, Board.BOARD_SIZE, 2):
            self._insert_locations.add(BoardLocation(0, position))
            self._insert_locations.add(BoardLocation(position, 0))
            self._insert_locations.add(BoardLocation(Board.BOARD_SIZE - 1, position))
            self._insert_locations.add(BoardLocation(position, Board.BOARD_SIZE - 1))

    def generate_random(self):
        """ Generates a random board state.
        Corners of the board are fixed as corners,
        Other unshiftable border pieces are t-junctions.
        """
        MazeCard.reset_ids()
        fixed_cards = {BoardLocation(0, 0): (MazeCard.CORNER, 90),
                       BoardLocation(0, self.BOARD_SIZE-1): (MazeCard.CORNER, 180),
                       BoardLocation(self.BOARD_SIZE-1, self.BOARD_SIZE-1): (MazeCard.CORNER, 270),
                       BoardLocation(self.BOARD_SIZE-1, 0): (MazeCard.CORNER, 0)}

        def card_at(location):
            if location in fixed_cards:
                return MazeCard.generate_random(fixed_cards[location][0], fixed_cards[location][1])
            return MazeCard.generate_random()

        self._maze_cards = [
            [card_at(BoardLocation(row, column)) for column in range(self.BOARD_SIZE)]
            for row in range(self.BOARD_SIZE)]

    def random_maze_card(self):
        """ Returns a random MazeCard of the current board """
        return self._maze_cards[randint(0, self.BOARD_SIZE-1)][randint(0, self.BOARD_SIZE-1)]

    def __getitem__(self, location):
        """ Retrieves the maze card at a given location

        :param location: a BoardLocation instance
        :raises InvalidLocationException: if location is outside of the board
        :return: the MazeCard instance
        """
        self._validate_location(location)
        return self._maze_cards[location.row][location.column]

    def __setitem__(self, location, maze_card):
        """ Sets the maze card at a given location

        :param location: a BoardLocation instance
        :raises InvalidLocationException: if location is outside of the board
        :param maze_card: the maze card to set
        """
        self._validate_location(location)
        self._maze_cards[location.row][location.column] = maze_card

    def maze_card_location(self, maze_card):
        """ Returns the BoardLocation of the given MazeCard,
        or None if the card is not on the board """
        for location in self.board_locations():
            if self[location] == maze_card:
                return location
        return None

    def shift(self, insert_location, inserted_maze_card):
        """ Performs a shifting action on the board

        :param insert_location: the location of the inserted maze card
        :param inserted_maze_card: the maze card to insert
        :raises InvalidShiftLocationException: for invalid insert location
        :return: the pushed out maze card
        """
        self._validate_location(insert_location)
        if insert_location not in self._insert_locations:
            raise InvalidShiftLocationException(
                "Location {} is not shiftable (fixed maze cards)".format(str(insert_location)))
        direction = self._determine_shift_direction(insert_location)
        shift_line_locations = []
        current_location = insert_location
        while current_location is not None:
            shift_line_locations.append(current_location)
            current_location = Board._neighbor(current_location, direction)
        pushed_out = self[shift_line_locations[-1]]
        self._shift_all(shift_line_locations)
        self[shift_line_locations[0]] = inserted_maze_card
        return pushed_out

    def _shift_all(self, shift_locations):
        """ Shifts the maze cards along the given locations """
        for source, target in reversed(list(zip(shift_locations, shift_locations[1:]))):
            self[target] = self[source]

    @classmethod
    def _determine_shift_direction(cls, shift_location):
        """ Returns the direction to shift to for a given location

        :param shift_location: the location of the pushed in maze card
        :raises InvalidShiftLocationException: if the location is not on the border
        :return: the direction as a tuple
        """
        if shift_location.row == cls.BOARD_SIZE - 1:
            return (-1, 0)
        if shift_location.row == 0:
            return (1, 0)
        if shift_location.column == cls.BOARD_SIZE - 1:
            return (0, -1)
        if shift_location.column == 0:
            return (0, 1)
        raise InvalidShiftLocationException(
            "Location {} is not shiftable (not on border)".format(str(shift_location)))

    @classmethod
    def _neighbor(cls, location, direction):
        """ Determines the neighbor of a location, if possible.

        :param location: the location the neighbor is requested for
        :param direction: a tuple describing the position of the requested neighbor,
        relative to the given location, e.g. (-1, 0) for the northern neighbor
        :return: a new location in the given direction,
        or None, if the location is outside of the board's extent
        """
        new_location = location.add(*direction)
        if not cls.is_inside(new_location):
            new_location = None
        return new_location

    @classmethod
    def is_inside(cls, location):
        """ Determines if the given location is inside the board """
        return location.row >= 0 and \
            location.column >= 0 and \
            location.row < cls.BOARD_SIZE and \
            location.column < cls.BOARD_SIZE

    @classmethod
    def board_locations(cls):
        """ Returns an iterator of all BoardLocations """
        for row in range(cls.BOARD_SIZE):
            for column in range(cls.BOARD_SIZE):
                yield BoardLocation(row, column)

    @classmethod
    def _validate_location(cls, location):
        if not cls.is_inside(location):
            raise InvalidLocationException("Location {} is outside of the board.".format(str(location)))


class Game:
    """
    The state of a game of labyrinth.
    """
    MAX_PLAYERS = 4

    def __init__(self):
        self._players = []
        self._board = Board()
        self._leftover_card = MazeCard()

    @property
    def leftover_card(self):
        """ Getter for leftover card """
        return self._leftover_card

    @leftover_card.setter
    def leftover_card(self, value):
        """ Setter for leftover card """
        self._leftover_card = value

    @property
    def board(self):
        """ Getter for board """
        return self._board

    @property
    def players(self):
        """ Getter for players """
        return self._players

    @players.setter
    def players(self, players):
        """ Setter for players """
        self._players = players

    def accepts_players(self):
        """ Determines if there are empty seats for players to join """
        return len(self._players) < Game.MAX_PLAYERS

    def add_player(self):
        """ Adds a player and returns his id.

        :return: id of the added player, None if the game is full
        """
        if self.accepts_players():
            player_id = len(self._players)
            player = Player(player_id)
            self._players.append(player)
            return player_id
        return None

    def init_game(self):
        """ Randomly initializes the game state, with the currently connected players.
        Players starting locations are the corners of the board, clockwise starting from (0, 0) """
        self._board.generate_random()
        self._leftover_card = MazeCard.generate_random()
        start_locations = [
            BoardLocation(0, 0),
            BoardLocation(0, self._board.BOARD_SIZE - 1),
            BoardLocation(self._board.BOARD_SIZE - 1, self._board.BOARD_SIZE - 1),
            BoardLocation(self._board.BOARD_SIZE - 1, 0)]
        circular_locations = list(islice(cycle(start_locations), self.MAX_PLAYERS))
        for player, location in zip(self._players, circular_locations):
            player.maze_card = self._board[location]

    def shift(self, player_id, new_leftover_location, leftover_rotation):
        """ Performs a shifting action

        :param player_id: the shifting player's id
        :param new_leftover_location: the new location of the leftover MazeCard
        :param leftover_rotation: the rotation of the leftover MazeCard, in degrees
        (one of 0, 90, 180, 270)
        :raises InvalidShiftLocationException: for invalid insert location
        :raises InvalidRotationException: for invalid rotation value
        :raises PlayerNotFoundException: for invalid player id
        """
        self.find_player(player_id)
        self._leftover_card.rotation = leftover_rotation
        pushed_card = self._leftover_card
        self._leftover_card = self._board.shift(new_leftover_location, self._leftover_card)
        for player in self._find_players_by_maze_card(self._leftover_card):
            player.maze_card = pushed_card

    def move(self, player_id, target_location):
        """ Performs a move action

        :param player_id: the moving player's id
        :param target_location: the board location to move to
        :raises PlayerNotFoundException: for invalid player id
        :raises InvalidLocationException: for invalid target location
        :raises MoveUnreachableException: if there is no valid path to the target location
        :raises InvalidStateException: for invalid state
        """
        player = self.find_player(player_id)
        player_location = self._board.maze_card_location(player.maze_card)
        if not MoveValidator(self._board).validate_move(player_location, target_location):
            raise MoveUnreachableException("Locations {} and {} are not connected".format(
                player_location, target_location))
        target = self._board[target_location]
        player.maze_card = target

    def find_player(self, player_id):
        """ Finds player by id.

        :param player_id: the id of the player to find
        :raises InvalidStateException: if more than two players with given id
        :raises PlayerNotFoundException: if no player with given id
        :return: an instance of Player
        """

        match = [player for player in self._players if player.identifier is player_id]
        if len(match) > 1:
            raise InvalidStateException("More than one player with id {}".format(player_id))
        elif not match:
            raise PlayerNotFoundException("No matching player for id {} in this game".format(player_id))
        return match[0]

    def _find_players_by_maze_card(self, maze_card):
        """ Finds player whose maze_card field matches the given maze card

        :param maze_card: an instance of MazeCard
        """
        return [player for player in self._players if player.maze_card is maze_card]