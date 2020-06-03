"""Minimal module to keep track of attributes of GolModel
"""

from gol.rule import Rule

class GolModel:
    """Mostly to remind myself what things are called in the model
    """

    def __init__(self):
        self.state = None
        self.rule = Rule((2, 3), (3,))
        self.description = list()
        self.filename = ""
        self.name = ""
        self.author = ""
