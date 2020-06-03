"""Contains the engine to calculate game of life generations

Must contain a GolEngine class with an 'advance' method
"""

from collections import defaultdict
import copy

class GolEngine():
    """Contains everything needed for the engine to work
    """

    def advance(self, model):
        """Calculate the next generation

        Parameters:
        model (GolModel): the model containing the state and rule of the system

        Return:
        model (GolModel): the model containing the state of the newly calculated system
        """

        # Prepare to count neighbours
        neighbour_count = defaultdict(int)

        # Count neighbours. Think of it as a heat-map of neighbours.
        for x, y in model.state:
            neighbour_count[(x+1, y+1)] += 1
            neighbour_count[(x+1, y)] += 1
            neighbour_count[(x+1, y-1)] += 1
            neighbour_count[(x, y+1)] += 1
            neighbour_count[(x, y-1)] += 1
            neighbour_count[(x-1, y+1)] += 1
            neighbour_count[(x-1, y)] += 1
            neighbour_count[(x-1, y-1)] += 1

        # Prepare the state of the next tick/generation
        new_state = set()

        # Iterate through the "heat-map" and apply rules
        for position, count in neighbour_count.items():
            if count in model.rule.birth:
                new_state.add(position)
            elif count in model.rule.survival and position in model.state:
                new_state.add(position)

        # Make a shallow copy and replace the state
        new_model = copy.copy(model)
        new_model.state = new_state

        return new_model
