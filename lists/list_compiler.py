import sys
import os.path as osp

from .list_lexer import lex_list
from .list_parser import parse_list

# Load RULESETS_PATH
# to be the 'rulesets' folder in the directory of this file
RULESETS_PATH = osp.join(osp.dirname(osp.abspath(__file__)), "rulesets")


# Loads a single list with the given filename from the RULESETS_PATH
# (file extension is added automatically), lexes it, parses it and stores
# the loaded compilate in the syslists folder
def compile_list(filename):
    with open(osp.join(RULESETS_PATH, f"{filename}.ruleset.txt")) as f:
        ruleset = f.read()
    
    lexed_ruleset = lex_list(ruleset)
    parsed_ruleset = parse_list(ruleset)


# Loads all registered lists from the registry and
# compile_list()s every single of them
def compile_all_lists():
    with open(osp.join(RULESETS_PATH, "registry.txt")) as f:
        registered_lists = f.read().strip().split("\n")
    
    print("Registered lists for compilation:", ", ".join(registered_lists), file=sys.stderr)

    for list in registered_lists:
        compile_list(list)