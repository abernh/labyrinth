import labyrinth.model.external_library as external


class CompletePathLibraryBinding(external.ExternalLibraryBinding):
    """ The external libraries only return one action, but the tests require a complete path, i.e. a series of actions
    which reach the objective. This subclass repeatedly calls the library to create such a path."""

    def __init__(self, path, board, previous_shift_location=None):
        self._piece = board.pieces[0]
        external.ExternalLibraryBinding.__init__(self, path, board, self._piece, previous_shift_location)

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
