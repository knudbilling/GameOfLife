from collections import defaultdict

class GolEngine():

    def advance(self, model):

        neighbour_count = defaultdict(int)
        for x, y in model.state:
            neighbour_count[(x+1, y+1)] += 1
            neighbour_count[(x+1, y)] += 1
            neighbour_count[(x+1, y-1)] += 1
            neighbour_count[(x, y+1)] += 1
            neighbour_count[(x, y-1)] += 1
            neighbour_count[(x-1, y+1)] += 1
            neighbour_count[(x-1, y)] += 1
            neighbour_count[(x-1, y-1)] += 1
        new_state = set()
        for position, count in neighbour_count.items():
            if count in model.rule.birth:
                new_state.add(position)
            elif count in model.rule.survival and position in model.state:
                new_state.add(position)
        model.state = new_state
        return model
