import sys

from .generators import generated_lists
from .list_compiler import compile_all_lists, compile_list

__all__ = generated_lists

if __name__ == "__main__":
    print("LIST compilation tool", file=sys.stderr)
    compile_list('pool2')
    #compile_all_lists()
