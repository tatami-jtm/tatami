from .match_result import MatchResult

class Match:

    def __init__(self, id, white, blue, tags=None):
        self._id = id
        self._white = white
        self._blue = blue
        self._tags = tags or []
        self._result = None

    def __repr__(self):
        return f"Match<{self.get_id()}>({repr(self.get_white())}, {repr(self.get_blue())}, {repr(self.get_tags())})"
    
    def get_id(self):
        return self._id

    def get_white(self):
        return self._white
    
    def get_blue(self):
        return self._blue

    def get_tags(self):
        return self._tags
    
    def set_result(self, match_result):
        match_result.set_match(self)
        self._result = match_result

    def get_result(self):
        return self._result

    def mk_result(self):
        self.set_result(result := MatchResult())
        return result