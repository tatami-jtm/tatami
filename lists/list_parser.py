from ._parse_general import ALL_RULES
from .parserdefn import LTree, RTokenStream, ParserState

def _flat_repr(x):
    return repr(x).replace("\t", "").replace("\n", "")

def parse_list(lexed_list):
    token_stream = RTokenStream.from_lexed_list(lexed_list)
    tree = LTree()
    
    parsed = parse_partial(ParserState(tree, token_stream), ALL_RULES)

    if parsed is not None:
        return parsed.tree[0]
    else:
        return None

def parse_partial(state, rules, level=0):
    #print('-' + '-'*level)
    while not state.tree.is_full():
        # if we are out of tokens without having a full _base, last attempt
        if state.token_stream.empty():
            return last_branch(state, rules)

        if (branch_result := branch_to_rules(state, rules, level)):
            return branch_result

        state = op_shift(state)

    # Once we have a full _base, we cannot have any more tokens
    if not state.token_stream.empty():
        return None # signal for: no parsing found
    
    return state.tree

def branch_to_rules(state, rules, level):
    for rule in rules:
        if rule.only_full_exact_match and not state.token_stream.empty():
            continue

        if not rule.matches(state.tree):
            continue

        if rule.always_reduce:
            state.tree = rule.apply(state.tree)
            return branch_to_rules(state, rules, level)
        else:
            #print('B:', rule)
            if (reduce := parse_partial(op_reduce(state, rule), rules, level+1)):
                return reduce
            if not state.token_stream.empty() and (shift := parse_partial(op_shift(state), rules, level+1)):
                return shift

    return None

def last_branch(state, rules):
    applied = True
    while applied:
        applied = False

        for rule in rules:
            if not rule.matches(state.tree):
                continue
        
            state.tree = rule.apply(state.tree)
            applied = True
            break
    
    if state.tree.is_full():
        return state.tree
    else:
        return None

def op_shift(state):
    return ParserState(state.tree.add_first(state.token_stream), state.token_stream.shift())

def op_reduce(state, rule):
    return ParserState(rule.apply(state.tree), state.token_stream)