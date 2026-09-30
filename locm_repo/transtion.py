class Transition:
    """
    Class that is used to collect information about Transitions
    """
    def __init__(self, name, action, obj, sort, start=None, end=None):
        """Construct a new sort.

        Keyword arguments:
        name -- the name of the action
        parameters -- a list of parameters described as variables
        """
        self.name = name
        self.action = action
        self.obj=obj
        self.sort=sort
        self.start = start
        self.end = end

    def update(self, start=None, end=None):
        if start:
            self.start=start
        if end:
            self.end=end
    def get_start(self):
        return self.start
    def get_end(self):
        return self.end

    def __repr__(self):
        return str(self.name)

    def __eq__(self, other):

        return self.name == other

    def __hash__(self):

        return hash(self.__repr__())

