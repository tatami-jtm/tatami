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

    def set_option(self, opt):
        self.meta.set_option(self, opt)

    def has_option(self, opt):
        return self.meta.has_option(self, opt)
    
    def alloc(self, player):
        self.meta.alloc(self, player)
    
    def get_schedule(self, informational_only=False):
        return self.meta.get_schedule(self, informational_only)

    def get_match_by_id(self, match_id, informational_only=True):
        return self.meta.get_match_by_id(self, match_id, informational_only)
    
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
    
    def get_fourth(self):
        return self.meta.get_fourth(self)
    
    def get_fifth(self):
        return self.meta.get_fifth(self)
    
    def get_sixth(self):
        return self.meta.get_sixth(self)
    
    def import_struct(self, struct):
        return self.meta.import_struct(self, struct)
    
    def export_struct(self):
        return self.meta.export_struct(self)
    
    def is_playoff(self, match_id):
        return self.meta.is_playoff(self, match_id)
    
    def get_included_templates(self):
        return self.meta.get_included_templates(self)