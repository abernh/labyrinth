""" Mapper implementation, maps between Model objects and persistable data structures (DTOs).

These DTOs are structures built of dictionaries and lists,
which in turn are automatically translatable to structured text (JSON or XML)
"""
import copy
from datetime import timedelta

from labyrinth.model.game import Game, Board, Piece, MazeCard, Turns, Maze, Player, PlayerAction
import labyrinth.model.computer as computer
from labyrinth.mapper.shared import _objective_to_dto, _dto_to_board_location, _board_location_to_dto, _board_to_dto
from labyrinth.mapper.constants import (ID, OBJECTIVE, PLAYERS, MAZE, NEXT_ACTION, LOCATION, MAZE_CARDS, SHIFT_URL,
                                        PREVIOUS_SHIFT_LOCATION, MAZE_CARD_ID, ACTION, MOVE_URL, OUT_PATHS, ROTATION,
                                        PLAYER_ID, MAZE_SIZE, SCORE, PIECE_INDEX, IS_COMPUTER, COMPUTATION_METHOD,
                                        TURN_PREPARE_DELAY, LIBRARY_PATH)


def game_to_dto(game: Game):
    """Maps a game to a DTO, which can be restored with dto_to_game()

    :param game: an instance of model.Game
    :return: a structure which can be encoded into JSON and decoded into a Game
    """
    return {
        ID: game.identifier,
        PLAYERS: [_player_to_dto(player) for player in game.players],
        MAZE: _board_to_dto(game.board),
        NEXT_ACTION: _turns_to_next_action_dto(game.turns),
        TURN_PREPARE_DELAY: _timedelta_to_dto_(game.turns.prepare_delay),
        OBJECTIVE: _objective_to_dto(game.board.objective_maze_card),
        PREVIOUS_SHIFT_LOCATION: _board_location_to_dto(game.previous_shift_location)
    }


def replace_turn_state(game_dto, player_action):
    """ Returns a copy of the given game DTO, with the next action replaced by the given PlayerAction """
    result = copy.deepcopy(game_dto)
    result[NEXT_ACTION] = _player_action_to_dto(player_action)
    return result


def dto_to_game(game_dto):
    """ maps a DTO to a game
    to deserialize a persisted instance.

    :param game_dto: a dictionary representing the structure of the game,
    created by game_to_dto
    :return: a Game instance whose state is equal to the DTO
    """
    maze, leftover_card, maze_card_by_id = _dto_to_maze_cards_and_dictionary(game_dto[MAZE])
    objective_maze_card = maze_card_by_id[game_dto[OBJECTIVE]]
    board = Board(maze, leftover_card, objective_maze_card=objective_maze_card)
    players = [_dto_to_player(player_dto, None, board, maze_card_by_id)
               for player_dto in game_dto[PLAYERS]]
    board._pieces = [player.piece for player in players]
    turns_prepare_delay = _dto_to_timedelta(game_dto[TURN_PREPARE_DELAY])
    turns = _dto_to_turns(game_dto[NEXT_ACTION], players=players, prepare_delay=turns_prepare_delay)
    identifier = game_dto[ID]
    game = Game(identifier, board=board, players=players, turns=turns)
    for player in players:
        player._game = game
    game.previous_shift_location = _dto_to_board_location(game_dto[PREVIOUS_SHIFT_LOCATION])
    return game


def _dto_to_maze_cards_and_dictionary(maze_dto):
    leftover_card = None
    maze_card_by_id = {}
    maze_size = maze_dto[MAZE_SIZE]
    maze = Maze(maze_size=maze_size)
    for maze_card_dto in maze_dto[MAZE_CARDS]:
        maze_card, board_location = _dto_to_maze_card(maze_card_dto)
        if board_location is None:
            leftover_card = maze_card
        else:
            maze[board_location] = maze_card
        maze_card_by_id[maze_card.identifier] = maze_card
    return maze, leftover_card, maze_card_by_id


def _dto_to_timedelta(delta_dto):
    return timedelta(seconds=float(delta_dto))


def _player_to_dto(player: Player):
    """Maps a player to a DTO

    :param piece: an instance of model.Piece
    :return: a structure whose JSON representation is valid for the API
    """
    player_dto = {ID: player.identifier,
                  MAZE_CARD_ID: player.piece.maze_card.identifier,
                  SCORE: player.score,
                  PIECE_INDEX: player.piece.piece_index}
    if type(player) is computer.ComputerPlayer:
        player_dto[IS_COMPUTER] = True
        player_dto[COMPUTATION_METHOD] = player.compute_method_factory.SHORT_NAME
        player_dto[LIBRARY_PATH] = player.compute_method_factory.FULL_PATH
        player_dto[SHIFT_URL] = player.shift_url
        player_dto[MOVE_URL] = player.move_url
    return player_dto


def _turns_to_next_action_dto(turns: Turns):
    """ Maps an instance of Turns to a DTO, representing
    only the next action.
    """
    player_action = turns.next_player_action()
    return _player_action_to_dto(player_action)


def _player_action_to_dto(player_action):
    if not player_action:
        return None
    return {PLAYER_ID: player_action.player.identifier,
            ACTION: player_action.action}


def _timedelta_to_dto_(delta: timedelta):
    return str(delta.total_seconds())


def _dto_to_player(player_dto, game, board, maze_card_dict):
    """ maps a DTO to a Player

    :param player: a dictionary representing game's (sub-)structure of a player,
    as created by _player_to_dto
    :param maze_card_dict: a dictionary between maze card ids and MazeCard instances
    :raises KeyError: if maze_card_dict does not contain the maze card or objective id in player_dto
    :return: a Player instance
    """
    piece = Piece(player_dto[PIECE_INDEX], maze_card_dict[player_dto[MAZE_CARD_ID]])
    player = None
    if IS_COMPUTER in player_dto and player_dto[IS_COMPUTER]:
        player = computer.create_computer_player(
            compute_method=player_dto[COMPUTATION_METHOD],
            full_path=player_dto[LIBRARY_PATH],
            url_supplier=None,
            player_id=player_dto[ID],
            game=game,
            shift_url=player_dto[SHIFT_URL],
            move_url=player_dto[MOVE_URL],
            piece=piece)
    else:
        player = Player(identifier=player_dto[ID], game=game, piece=piece)
    player._board = board
    player.score = player_dto[SCORE]
    return player


def _dto_to_maze_card(maze_card_dto):
    """ Maps a DTO to a maze card and a board location

    :param maze_card_dto: a dictionary representing the game (sub-)structure of a maze card,
    as created by _maze_card_to_dto
    :return: a MazeCard instance and a BoardLocation instance (or None, for the leftover card)
    """
    maze_card = MazeCard(maze_card_dto[ID], maze_card_dto[OUT_PATHS], maze_card_dto[ROTATION])
    location = _dto_to_board_location(maze_card_dto[LOCATION])
    return maze_card, location


def _dto_to_turns(next_action_dto, players, prepare_delay=timedelta(0)):
    """ Maps a DTO to a Turns instance

    :param next_action_dto: a dictionary representing the next player action,
    as created by _turns_to_next_action_dto
    :param players: a list of players. The value of the PLAYER_ID field in the dto
    has to match one of the player's id
    :return: an instance of Turns
    """
    if not players:
        return Turns(prepare_delay=prepare_delay)
    player = next(player for player in players if player.identifier == next_action_dto[PLAYER_ID])
    action = next_action_dto[ACTION]
    return Turns(players=players, next_action=PlayerAction(player, action), prepare_delay=prepare_delay)
