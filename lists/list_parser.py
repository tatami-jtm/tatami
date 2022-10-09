from ._parse_general import ALL_RULES
from .parserdefn import LTree, RTokenStream, ParserState

def parse_list(lexed_list):
    token_stream = RTokenStream.from_lexed_list(lexed_list)
    tree = LTree()
    
    parsed = parse_partial(ParserState(tree, token_stream), ALL_RULES)

    if parsed is not None:
        return parsed.tree[0]
    else:
        return None

def parse_partial(state, rules):
    while not state.tree.is_full():
        # if we are out of tokens without having a full _base, failure
        if state.token_stream.empty():
            return branch_to_rules(state, rules)
            #return None # signal for: no parsing found

        if (branch_result := branch_to_rules(state, rules)):
            return branch_result

        state = op_shift(state)

    # Once we have a full _base, we cannot have any more tokens
    if not state.token_stream.empty():
        return None # signal for: no parsing found
    
    return state.tree

def branch_to_rules(state, rules):
    for rule in rules:
        if not rule.matches(state.tree):
            continue

        if rule.always_reduce:
            state.tree = rule.apply(state.tree)
            return None # it does not matter what we do, because we directly work on state

        else:
            if (reduce := parse_partial(op_reduce(state, rule), rules)):
                return reduce
            if not state.token_stream.empty() and (shift := parse_partial(op_shift(state), rules)):
                return shift

    return None

def op_shift(state):
    return ParserState(state.tree.add_first(state.token_stream), state.token_stream.shift())

def op_reduce(state, rule):
    return ParserState(rule.apply(state.tree), state.token_stream)