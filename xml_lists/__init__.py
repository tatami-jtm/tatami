from .list_compiler import *
from .metalist import *

if __name__ == "__main__":
    all_lists = get_all_lists()
    chosen_list = all_lists[0]

    print("Avail. lists:", ", ".join(all_lists))
    print("Attempting to compile:", chosen_list)

