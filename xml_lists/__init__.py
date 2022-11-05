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

    list_xml = load_list_xml(chosen_list)
    metalist = MetaList(list_xml)

    print("Name:",
        metalist.get_name())
    print("Requires:",
        metalist.require_min(), "--", metalist.require_max())
    print("Allocation order:",
        ", ".join(metalist._allocation_order))

    print(metalist._matches)