class Sort:
    """
    Class that is used to collect information about sorts
    """
    def __init__(self, name, obj):
        """Construct a new sort.

        Keyword arguments:
        name -- the name of the action
        parameters -- a list of parameters described as variables
        """
        self.name = name
        self.objects = obj

    def addObject(self, obj):
        self.objects.add(obj)

    
    def __eq__(self, other):
        return (self.name == other.name and self.objects==other.objects)
    
    def __hash__(self):

        return hash(str(self.name))

    