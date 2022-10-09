from lib2to3.pgen2 import token
from ._parse_general import ALL_TYPES

def lex_list(ruleset):
    token_stream = []
    current_token_type = None
    begin_ptr = 0
    end_ptr = 1
    max_position = len(ruleset) - 1

    while begin_ptr <= max_position:
        if current_token_type is None:
            if ruleset[begin_ptr] in " \n\t":
                begin_ptr += 1
                end_ptr += 1
                continue

            for type in ALL_TYPES:
                if type.matches(ruleset[begin_ptr:end_ptr]):
                    current_token_type = type
                    break
            else:
                if end_ptr == max_position:
                    raise ValueError(f"cannot lex further than pos. {begin_ptr}; lexing error")
                else:
                    end_ptr += 1
        else:
            if end_ptr == max_position + 1: # Reaching the end of the ruleset
                token_stream += [current_token_type(ruleset[begin_ptr:end_ptr])]
                break
            elif not current_token_type.matches(ruleset[begin_ptr:end_ptr+1]): # Reaching the end of the token
                token_stream += [current_token_type(ruleset[begin_ptr:end_ptr])]
                begin_ptr, end_ptr = end_ptr, end_ptr + 1
                current_token_type = None
            else:
                end_ptr += 1

    #print(token_stream)
    return token_stream