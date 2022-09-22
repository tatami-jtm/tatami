from .generators import generated_lists
from .list_compiler import compile_all_lists

__all__ = generated_lists

if __name__ == "__main__":
    print("LIST compilation tool")
    compile_all_lists()
