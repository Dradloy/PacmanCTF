class mcTree:
    def __init__(self, currGameState, parent = None):
        self.parent = parent
        self.children = []
        self.value = 0
        self.numVisits = 0
        self.score = None
        self.id = currGameState