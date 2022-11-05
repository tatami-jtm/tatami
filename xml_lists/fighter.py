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
    
    """
        Returns the (global) ID for the fighter;

        this is intended to be a keyword under which the
        fighter can be identified in the global system, such
        as a database ID.
    """
    def get_id(self):
        return self.id
    
    """
        Returns the name of the fighter;

        this is the name that will be shown in lists and
        results, i.e. the natural name of the fighter
    """
    def get_name(self):
        return self.name
    
    """
        Returns the affiliation of the fighter;

        this might be a sports club or a state (or any other
        institution) depending on the specifics of this
        tournament.
    """
    def get_affil(self):
        return self.affil