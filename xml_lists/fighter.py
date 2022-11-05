class Fighter:

    """
        Initializes a new Fighter object;

        see .get_id, .get_name and .get_affil for the
        interpretation of the parameters
    """
    def __init__(self, id, name, affil):
        self._id = id
        self._name = name
        self._affil = affil

        self._disqualified = False

    def __repr__(self):
        return f"Fighter({repr(self.get_id())}, {repr(self.get_name())}, {repr(self.get_affil())})"
    
    """
        Returns the (global) ID for the fighter;

        this is intended to be a keyword under which the
        fighter can be identified in the global system, such
        as a database ID.
    """
    def get_id(self):
        return self._id
    
    """
        Returns the name of the fighter;

        this is the name that will be shown in lists and
        results, i.e. the natural name of the fighter
    """
    def get_name(self):
        return self._name
    
    """
        Returns the affiliation of the fighter;

        this might be a sports club or a state (or any other
        institution) depending on the specifics of this
        tournament.
    """
    def get_affil(self):
        return self._affil

    def disqualify(self):
        self._disqualified = True

    def is_disqualified(self):
        return self._disqualified

class _BlankFighter(Fighter):

    def __init__(self):
        super().__init__('__blank', '-', '-')
    
    def is_disqualified(self):
        return True

BlankFighter = _BlankFighter()