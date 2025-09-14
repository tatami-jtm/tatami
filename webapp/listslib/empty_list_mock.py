from .list_compiler import compile_list
from .fighter import Fighter

class EmptyListMock:

    def __init__(self, event_class, list_system):
        self.event_class = event_class
        self.list_system = list_system

        self.the_list = compile_list(self.list_system.list_file)()

        for n in range(self.the_list.require_max()):
            self.the_list.alloc(Fighter(f'f{n}', '', ''))

        self.assigned_to_position = None
        self.title = ""

    def get_list(self):
        return self.the_list
    
    def cut_title(self):
        return ''