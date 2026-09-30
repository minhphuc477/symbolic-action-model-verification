class ObjectState:
    """
    Class that is used to collect information about states
    """
    def __init__(self, name, param=None, sort=None):
        """Construct a new sort.

        Keyword arguments:
        name -- the name of the action
        sort -- the sort where the object resides
        """
        self.name = name
        if param==None:
            self.param=set()
        self.sort=sort

    
    def rename(self, name):
        self.name= name
    def set_parameter(self, param):
        if param not in self.param:
            self.param.add(param)

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, ObjectState):
            return NotImplemented
        else:
            return self.name == other.name

    def __hash__(self):

        return hash(self.__repr__())
        