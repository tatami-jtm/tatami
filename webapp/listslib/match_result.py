class MatchResult:

    def __init__(self):
        self._match = None

        self._points_white = None
        self._score_white = None
        self._data_white = None

        self._points_blue = None
        self._score_blue = None
        self._data_blue = None

        self._absolute_winner = None

        self._time = None

    @classmethod
    def mk(cls, white_pts, white_scr, white_data, blue_pts, blue_scr, blue_data, winner, time):
        mr = MatchResult()
        mr.set_points_white(white_pts)
        mr.set_score_white(white_scr)
        if white_data:
            mr.set_data_white(*white_data)
        mr.set_points_blue(blue_pts)
        mr.set_score_blue(blue_scr)
        if blue_data:
            mr.set_data_blue(*blue_data)
        mr.set_absolute_winner(winner)
        mr.set_time(time)
        return mr

    def is_white_winner(self):
        if self._absolute_winner == 'white':
            return True
        elif self._absolute_winner == 'blue':
            return False

        if None in (self._points_white, self._points_blue):
            return False

        return self._points_white > self._points_blue
    
    def is_blue_winner(self):
        if self._absolute_winner == 'blue':
            return True
        elif self._absolute_winner == 'white':
            return False

        if None in (self._points_white, self._points_blue):
            return False

        return self._points_blue > self._points_white
    
    def set_match(self, match):
        self._match = match
    
    def get_match(self):
        return self._match

    def set_absolute_winner(self, absolute_winner):
        self._absolute_winner = absolute_winner
    
    def get_absolute_winner(self):
        return self._absolute_winner

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

    def clearly_decided(self):
        return self.is_blue_winner() != self.is_white_winner()