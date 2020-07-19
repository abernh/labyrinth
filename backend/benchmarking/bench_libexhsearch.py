""" Usage:
bench_libexhsearch <task> <case>
where task is either 'profile' or 'result'
and 'case' is either the name of a specific test case, or
'all' for all test cases defined in test_exhaustive_search
"""
import timeit
import sys
from tests.unit.mazes import EXH_DEPTH_4_MAZE
from tests.unit.test_exhaustive_search import CASES_PARAMS
import app.model.algorithm.external_library as libexhsearch
import app.model.algorithm.util as algo_util
import tests.unit.factories as setup

BENCH_CASES_PARAMS = {
    "d4-generated-86s": (EXH_DEPTH_4_MAZE, "NE", [(4, 2)], (6, 7))
}


class CompletePathLibraryBinding(libexhsearch.ExternalLibraryBinding):
    """ The external libraries only return one action, but the tests require a complete path, i.e. a series of actions
    which reach the objective. The subclass in this module repeatedly calls the library to create such a path.
    It provides the same interface as exhaustive_search.Optimizer, so it can be used as a fixture. """

    def __init__(self, path, board, piece, previous_shift_location=None):
        board = algo_util.copy_board(board, pieces=[piece])
        piece = board.pieces[0]
        board.validate_moves = True
        board.maze.validation = True
        libexhsearch.ExternalLibraryBinding.__init__(self, path, board, piece, previous_shift_location)

    def find_optimal_actions(self):
        """ repeatedly calls library to retrieve all actions to reach the objective """
        has_reached = False
        actions = []
        steps = 0
        while not has_reached and steps < 20:
            shift_action, move_location = self.find_optimal_action()
            actions.extend([shift_action, move_location])
            self._board.shift(shift_action[0], shift_action[1])
            self._previous_shift_location = shift_action[0]
            has_reached = self._board.move(self._piece, move_location)
            steps += 1
        return actions


def _create_board(key):
    if key in BENCH_CASES_PARAMS:
        param_dict = setup.param_tuple_to_param_dict(*(BENCH_CASES_PARAMS[key]))
    else:
        param_dict = setup.param_tuple_to_param_dict(*(CASES_PARAMS[key]))
    board = setup.create_board_and_pieces(**param_dict)
    return board, board.pieces[0]


def _create_single_result_optimizer(key, previous_shift_location=None):
    """Creates a test case, instantiates an Optimizer with this case.

    :param key: a key for the test-case
    :return: an Optimizer instance, the board and the piece of the created test-case
    """
    board, piece = _create_board(key)
    optimizer = libexhsearch.ExternalLibraryBinding("./lib/libexhsearch.so",
                                                    board, piece, previous_shift_location=previous_shift_location)
    return optimizer, board, piece


def _create_complete_path_optimizer(key, previous_shift_location=None):
    """Creates a test case, instantiates an Optimizer with this case.

    :param key: a key for the test-case
    :return: an Optimizer instance, the board and the piece of the created test-case
    """
    board, piece = _create_board(key)
    optimizer = CompletePathLibraryBinding("./lib/libexhsearch.so",
                                           board, piece, previous_shift_location=previous_shift_location)
    return optimizer, board, piece


def _benchmark(name):
    repeat = 5
    runs = 1
    optimizer, _, _ = _create_single_result_optimizer(name)
    min_time = min(timeit.Timer(optimizer.find_optimal_action).repeat(repeat, runs)) / runs * 1000
    print("Test case {:<24} \t best of {}: {:.2f}ms".format(name, repeat, min_time))


def _results(name):
    optimizer, _, _ = _create_complete_path_optimizer(name)
    print("Test case {:<24} \t resulted in actions {}".format(name, optimizer.find_optimal_actions()))


def _main(argv):
    mode = "benchmark"
    case_name = "all"
    if len(argv) > 1:
        mode = argv[1]
    if len(argv) > 2:
        case_name = argv[2]
    cases = []
    if case_name == "all":
        cases = CASES_PARAMS.keys()
    else:
        cases = [case_name]
    for name in cases:
        if mode == "benchmark":
            _benchmark(name)
        elif mode == "result":
            _results(name)


if __name__ == "__main__":
    _main(sys.argv)
