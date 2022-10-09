# class BaseToken
# base class for all lexical (or inferred) token
from turtle import left


class BaseToken:
    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return self.id()

    def id(self):
        return 'generic-token'

    def kenn(self):
        return self.id()

    def is_lexical(self):
        return False

    def core(self):
        return self

    @classmethod
    def matches(cls, expression):
        return NotImplemented

# class LT
# base class for all lexical token (types)
class LT (BaseToken):
    def __repr__(self):
        return '<' + self.id() + '>'

    def id(self):
        return 'lex-token'

    def is_comment(self):
        return False

    def is_lexical(self):
        return True

    def kenn(self):
        return '<' + self.id() + '>'


# class IT
# base class for inferred tokens
class IT(BaseToken):
    def __repr__(self):
        return self.id() + '(\n' + repr(self.content).replace('\n', '\n\t') + '\n)'

    def id(self):
        return 'inf-token'

    def kenn(self):
        return self.id() + '(' + repr(self.content) + ')'


# class Alternative
# base class for alternative tokens
# this is when multiple tokens - sometimes - have the same meaning
class Alt(IT):
    def id(self):
        return 'alternative'

    def core(self):
        return self.content


# class PT
# class for parser-generated tokens; this class should not be used manually!
class PT(IT):
    def __init__(self, name, content):
        super().__init__(content)

        self.name = name
    
    def __repr__(self):
        return self.id() + '(\n\t' + ", \n\t".join(repr(i).replace('\n', '\n\t') for i in self.content) + '\n)'

    def id(self):
        return self.name

    def kenn(self):
        return self.name


BASE_RULE = '_base'

# class Rule
# base class for parser rules
class Rule:
    def __init__(self, name, right_side, nest=None, nest_to=None, always_reduce=False):
        self.name = name
        self.right_side = right_side
        self.nest = nest
        self.nest_to = nest_to
        self.always_reduce = always_reduce

    def __repr__(self):
        return self.name + " => " + self.right_side

    def matches(self, tree):
        return tree.rmatch(self.right_side) is not None

    def apply(self, tree):
        if not (match := tree.rmatch(self.right_side)):
            raise ValueError("Rule.apply fails because tree does not match right side of rule")

        if self.nest is None:
            return tree.rreplace(match, PT(self.name, match))
        else:
            return tree.rreplace(match, PT(self.name, [match[self.nest]] + match[self.nest_to].content))

class LTree:
    def __init__(self, tokens = None):
        if tokens is None:
            self.tree = []
        else:
            self.tree = tokens[:]

    def add_first(self, from_stream):
        if from_stream.empty():
            raise ValueError("LTree.add_last fails because the given stream is empty.")

        return LTree(self.tree + [from_stream.tokens[0]])
    
    def rmatch(self, right_side):
        index = len(self.tree) - 1
        match = []

        for part in right_side.split(" ")[::-1]:
            if index < 0:
                return None

            if self.tree[index].kenn() != part:
                return None
            
            match = [self.tree[index]] + match
            index -= 1

        return match
    
    def rreplace(self, match, summary):
        if self.tree[-len(match):] != match:
            raise ValueError("LTree.rreplace failed because given match is invalid.")
        
        new_tree = LTree(self.tree[:-len(match)] + [summary])
        return new_tree

    def is_full(self):
        return len(self.tree) == 1 and self.tree[0].kenn() == BASE_RULE


class RTokenStream:
    def __init__(self):
        self.tokens = []
    
    def empty(self):
        return len(self.tokens) == 0

    def shift(self):
        if self.empty():
            raise ValueError("RTokenStream.shift fails because there are no tokens to shift.")

        return RTokenStream.from_lexed_list(self.tokens[1:])

    @classmethod
    def from_lexed_list(cls, list):
        rts = cls()
        rts.tokens = list[:]
        return rts


class ParserState:
    def __init__(self, tree, stream):
        self.tree = tree
        self.token_stream = stream