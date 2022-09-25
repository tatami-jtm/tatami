import re

# class LT
# base class for all lexical token (types)
class LT:
    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return '<' + self.id() + '>'

    def id(self):
        return 'generic-token'

    def is_comment(self):
        return False

    @classmethod
    def matches(cls, expression):
        return False
        

class RuleSetType(LT):
    def id(self):
        return 'ruleset-type'
    
    @classmethod
    def matches(cls, expression):
        return expression == "<!ruleset-list>"


class CommentType(LT):
    def id(self):
        return 'comment'
    
    def is_comment(self):
        return True

    @classmethod
    def matches(cls, expression):
        return expression.startswith("--") and "\n" not in expression


class KeywordType(LT):
    def id(self):
        return 'keyword:' + self.content

    @classmethod
    def matches(cls, expression):
        for char in expression:
            if char not in "_abcdefghijklmnopqrstuvwxyz":
                return False
        else:
            return True


class StringType(LT):
    def id(self):
        return 'string'
    
    @classmethod
    def matches(cls, expression):
        return len(expression) >= 2 and expression.startswith("'") and expression.endswith("'") and "'" not in expression[1:-1] and "\n" not in expression[1:-1]


class NumberType(LT):
    def id(self):
        return 'number'
    
    @classmethod
    def matches(cls, expression):
        for char in expression:
            if char not in "0123456789":
                return False
        else:
            return True


class ConnOpType(LT):
    def id(self):
        return 'connection-operator'
    
    @classmethod
    def matches(cls, expression):
        return expression == "."


class ListOpType(LT):
    def id(self):
        return 'list-operator'
    
    @classmethod
    def matches(cls, expression):
        return expression == ","


class BlockBeginType(LT):
    def id(self):
        return 'block-begin'
    
    @classmethod
    def matches(cls, expression):
        return expression == "{"


class BlockEndType(LT):
    def id(self):
        return 'block-end'
    
    @classmethod
    def matches(cls, expression):
        return expression == "}"


class FighterNumberType(LT):
    def id(self):
        return 'fighter-number'
    
    @classmethod
    def matches(cls, expression):
        if not expression.startswith("$") or len(expression) < 2:
            return False
        else:
            return NumberType.matches(expression[1:])


class FighterPlacementType(LT):
    def id(self):
        return 'fighter-placement'
    
    @classmethod
    def matches(cls, expression):
        if not expression.startswith("%") or len(expression) < 2:
            return False
        else:
            return NumberType.matches(expression[1:])


class MatchIDType(LT):
    def id(self):
        return 'match-id'
    
    @classmethod
    def matches(cls, expression):
        if not expression.startswith("#") or len(expression) < 2:
            return False
        else:
            for char in expression[1:]:
                if char not in "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
                    return False
            else:
                return True

ALL_TYPES = [
    RuleSetType,
    CommentType,
    KeywordType,
    StringType,
    NumberType,
    ConnOpType,
    ListOpType,
    BlockBeginType,
    BlockEndType,
    FighterNumberType,
    FighterPlacementType,
    MatchIDType
]