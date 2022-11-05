from .list_compiler import *
from .metalist import *

if __name__ == "__main__":
    all_lists = get_all_lists()
    chosen_list = all_lists[2]

    print("Avail. lists:",
        ", ".join(all_lists))
    print("Attempting to compile:",
        chosen_list)

    print()

    list_cls = compile_list(chosen_list)
    metalist = list_cls.meta

    print("Name:",
        metalist.get_name())
    print("Requires:",
        metalist.require_min(), "--", metalist.require_max())
    print("Allocation order:",
        ", ".join(map(str, metalist._allocation_order)))
    
    example_list = list_cls()
    example_list.alloc('ABC')
    example_list.alloc('DEF')

    print(example_list.get_schedule())