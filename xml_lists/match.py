class Match:

    def __init__(self, white, blue):
        self._white = white
        self._blue = blue
        self._result = None
    
    def get_white(self):
        return self._white
    
    def get_blue(self):
        return self._blue
    
    def set_result(self, match_result):
        match_result.set_match(self)
        self._result = match_result

    def get_result(self):
        return self._result