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

    print("Schedule:", example_list.get_schedule())

    print("Resolving first fight.")

    first_match = example_list.get_schedule()[0]['match']
    fmr = first_match.mk_result()
    fmr.set_points_white(1)
    fmr.set_score_white(10)
    fmr.set_points_blue(0)
    fmr.set_score_blue(0)
    fmr.set_time(120)
    example_list.enter_results(fmr)

    print("Schedule:", example_list.get_schedule())

    print(example_list.completed())

    second_match = example_list.get_schedule()[0]['match']
    smr = second_match.mk_result()
    smr.set_points_white(0)
    smr.set_score_white(0)
    smr.set_points_blue(1)
    smr.set_score_blue(7)
    smr.set_time(120)
    example_list.enter_results(smr)

    print("Schedule:", example_list.get_schedule())

    print(example_list.completed())