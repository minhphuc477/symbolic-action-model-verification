class Action:
    """
    Class that is used to collect information about actions
    """
    def __init__(self, name, parameters=[]):
        """Construct a new sort.

        Keyword arguments:
        name -- the name of the action
        parameters -- a list of parameters described as variables
        """
        self.name = name
        self.parameters = parameters

    def __repr__(self):
        return str(self.name)
    
    def __eq__(self, other):
        return (
            self.name == other.name
        )
    """
    def __hash__(self):

        return hash(self.__repr__())
    """
