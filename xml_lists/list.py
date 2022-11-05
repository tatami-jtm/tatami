class List:

    meta = None

    @classmethod
    def get_name(cls):
        return cls.meta.get_name()
    
    @classmethod
    def require_min(cls):
        return cls.meta.require_min()
    
    @classmethod
    def require_max(cls):
        return cls.meta.require_max()

    def __init__(self):
        self.meta.init(self)
    
    def alloc(self, player):
        self.meta.alloc(self, player)
    
    def get_schedule(self, informational_only=False):
        return self.meta.get_schedule(self)

    def get_match_by_id(self, match_id):
        return self.meta.get_match_by_id(self, match_id)
    
    def enter_results(self, match_result):
        self.meta.enter_results(self, match_result)
    
    def completed(self):
        return self.meta.completed(self)
    
    def score(self):
        return self.meta.score(self)
    
    def get_first(self):
        return self.meta.get_first(self)
    
    def get_second(self):
        return self.meta.get_second(self)
    
    def get_third(self):
        return self.meta.get_third(self)
    
    def get_fifth(self):
        return self.meta.get_fifth(self)