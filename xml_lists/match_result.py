class MatchResult:

    def __init__(self):
        self._match = None

        self._points_white = None
        self._score_white = None
        self._data_white = None

        self._points_blue = None
        self._score_blue = None
        self._data_blue = None

        self._time = None

    def is_white_winner(self):
        if None in (self._points_white, self._points_blue):
            return False

        return self._points_white > self._points_blue
    
    def is_blue_winner(self):
        if None in (self._points_white, self._points_blue):
            return False

        return self._points_blue > self._points_white
    
    def set_match(self, match):
        self._match = match
    
    def get_match(self):
        return self.match

    def set_points_white(self, pts):
        self._points_white = pts
    
    def get_points_white(self):
        return self._points_white

    def set_score_white(self, scr):
        self._score_white = scr
    
    def get_score_white(self):
        return self._score_white

    def set_data_white(self, pos, neg, disq):
        self._data_white = (pos, neg, disq)
    
    def get_data_white(self):
        return self._data_white

    def set_points_blue(self, pts):
        self._points_blue = pts
    
    def get_points_blue(self):
        return self._points_blue

    def set_score_blue(self, scr):
        self._score_blue = scr
    
    def get_score_blue(self):
        return self._score_blue

    def set_data_blue(self, pos, neg, disq):
        self._data_blue = (pos, neg, disq)
    
    def get_data_blue(self):
        return self._data_blue
    
    def set_time(self, time):
        self._time = time
    
    def get_time(self):
        return self._time