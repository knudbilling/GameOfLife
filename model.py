from rule import Rule



class GolModel:

    def __init__(self):
        self.state = None
        self.rule = Rule((2, 3), (3,))
        self.description = list()
        self.filename = ""
        self.name = ""
        self.author = ""
