""" This module provides a binding to an external library.

It models the structs with ctypes and defines a class which implements the algorithm interface by
binding to a library at a given path """
import ctypes
from server.model.game import BoardLocation


class LOCATION(ctypes.Structure):
    """ corresponds to game.BoardLocation """
    _fields_ = [("row", ctypes.c_short), ("column", ctypes.c_short)]


class NODE(ctypes.Structure):
    """ corresponds to game.MazeCard
    The doors are represented as a bitfield """
    _fields_ = [("node_id", ctypes.c_uint), ("out_paths", ctypes.c_ubyte), ("rotation", ctypes.c_short)]


class GRAPH(ctypes.Structure):
    """ corresponds to game.Maze """
    _fields_ = [
        ("extent", ctypes.c_ulonglong),
        ("num_nodes", ctypes.c_ulonglong),
        ("nodes", ctypes.POINTER(NODE))
    ]


class ACTION(ctypes.Structure):
    """ return type of algolibs function call: shift location, rotation and move location """
    _fields_ = [
        ("shift_location", LOCATION),
        ("rotation", ctypes.c_short),
        ("move_location", LOCATION),
    ]


class ExternalLibraryBinding:
    """ Binds to an external library at given path. 
    Translates the game datastructures to the ctypes structures and back """
    _DOOR_TO_BIT = {"N": 1, "E": 2, "S": 4, "W": 8}

    def __init__(self, path, board, piece, previous_shift_location=None):
        self._library = ctypes.cdll.LoadLibrary(path)
        self._library.find_action.restype = ACTION
        self._board = board
        self._board.clear_pieces()
        self._board.pieces.append(piece)
        self._piece = piece
        self._previous_shift_location = previous_shift_location
        if self._previous_shift_location is None:
            self._previous_shift_location = BoardLocation(-1, -1)

    def find_optimal_action(self):
        """ finds optimal action by calling the external library """
        graph = self._create_graph(self._board)
        start_location = self._board.maze.maze_card_location(self._piece.maze_card)
        start_location = self._create_location(start_location)
        previous_shift_location = self._create_location(self._previous_shift_location)
        objective_id = self._board.objective_maze_card.identifier
        action = self._library.find_action(ctypes.byref(graph), ctypes.byref(start_location), objective_id,
                                           ctypes.byref(previous_shift_location))
        return self._map_returned_action(action)

    @staticmethod
    def _create_node(maze_card):
        """ creates a NODE from a MazeCard """
        out_paths = 0
        for maze_card_door in maze_card.doors:
            out_paths = out_paths | ExternalLibraryBinding._DOOR_TO_BIT[maze_card_door]
        return NODE(maze_card.identifier, out_paths, maze_card.rotation)

    @staticmethod
    def _create_graph(board):
        """ creates a GRAPH function argument

        :param board: an instance of server.model.game.board
        """
        maze = board.maze
        extent = maze.maze_size
        node_array = [ExternalLibraryBinding._create_node(maze[location]) for location in maze.maze_locations]
        node_array.append(ExternalLibraryBinding._create_node(board.leftover_card))
        nodes = (NODE * len(node_array))(*node_array)
        return GRAPH(extent=extent, num_nodes=len(node_array), nodes=nodes)

    @staticmethod
    def _create_location(board_location):
        """ creates a LOCATION from a BoardLocation """
        return LOCATION(board_location.row, board_location.column)

    @staticmethod
    def _map_returned_action(action):
        """ creates an action tuple (shift_location, rotation), move_location from an ACTION """
        return (BoardLocation(action.shift_location.row, action.shift_location.column), action.rotation), \
            BoardLocation(action.move_location.row, action.move_location.column)