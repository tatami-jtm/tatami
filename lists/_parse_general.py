from .parserdefn import *

class RuleSetType(LT):
    def id(self):
        return 'ruleset-type'
    
    @classmethod
    def matches(cls, expression):
        return expression == "<!ruleset-list>"


class Comment(LT):
    def id(self):
        return 'comment'
    
    def is_comment(self):
        return True

    @classmethod
    def matches(cls, expression):
        return expression.startswith("--") and "\n" not in expression


class Keyword(LT):
    def id(self):
        return 'keyword:' + self.content

    @classmethod
    def matches(cls, expression):
        for char in expression:
            if char not in "_abcdefghijklmnopqrstuvwxyz":
                return False
        else:
            return True


class String(LT):
    def id(self):
        return 'string'
    
    @classmethod
    def matches(cls, expression):
        return len(expression) >= 2 and expression.startswith("'") and expression.endswith("'") and "'" not in expression[1:-1] and "\n" not in expression[1:-1]


class Number(LT):
    def id(self):
        return 'number'
    
    @classmethod
    def matches(cls, expression):
        for char in expression:
            if char not in "0123456789":
                return False
        else:
            return True


class ConnOp(LT):
    def id(self):
        return 'connection-operator'
    
    @classmethod
    def matches(cls, expression):
        return expression == "."


class ListOp(LT):
    def id(self):
        return 'list-operator'
    
    @classmethod
    def matches(cls, expression):
        return expression == ","


class BlockBegin(LT):
    def id(self):
        return 'block-begin'
    
    @classmethod
    def matches(cls, expression):
        return expression == "{"


class BlockEnd(LT):
    def id(self):
        return 'block-end'
    
    @classmethod
    def matches(cls, expression):
        return expression == "}"


class FighterNumber(LT):
    def id(self):
        return 'fighter-number'
    
    @classmethod
    def matches(cls, expression):
        if not expression.startswith("$") or len(expression) < 2:
            return False
        else:
            return Number.matches(expression[1:])


class FighterPlacement(LT):
    def id(self):
        return 'fighter-placement'
    
    @classmethod
    def matches(cls, expression):
        if not expression.startswith("%") or len(expression) < 2:
            return False
        else:
            return Number.matches(expression[1:])


class MatchID(LT):
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


class MatchWinner(IT):
    def id(self):
        'match-winner'
    
    @classmethod
    def matches(cls, tokens):
        return tokens == '<match-id> <connection-operator> <keyboard:winner>'


class MatchLoser(IT):
    def id(self):
        'match-winner'
    
    @classmethod
    def matches(cls, tokens):
        return tokens == '<match-id> <connection-operator> <keyboard:loser>'


class PlayerCodeAlt(Alt):
    def id(self):
        return 'player-code'
    
    @classmethod
    def matches(cls, tokens):
        return tokens in ['<fighter-number>', '<fighter-placement>', 'match-winner', 'match-loser']



ALL_TYPES = [
    RuleSetType,
    Comment,
    Keyword,
    String,
    Number,
    ConnOp,
    ListOp,
    BlockBegin,
    BlockEnd,
    FighterNumber,
    FighterPlacement,
    MatchID
]

ALL_RULES = [
    Rule(BASE_RULE,                 '<ruleset-type> ruleset'),
    Rule('ruleset',                 'rule ruleset', nest=0, nest_to=1),
    Rule('ruleset',                 'rule'),

    Rule('rule',                    'name-rule', always_reduce=True),
    Rule('rule',                    'require-rule', always_reduce=True),
    Rule('rule',                    'alloc-rule', always_reduce=True),
    Rule('rule',                    'match-rule'),
    Rule('rule',                    'order-rule'),
    Rule('rule',                    'score-rule', always_reduce=True),
    Rule('rule',                    'playoff-rule', always_reduce=True),

    Rule('player-code',             '<fighter-number>'),
    Rule('player-code',             '<fighter-placement>'),
    Rule('player-code',             '<match-id> <connection-operator> <keyword:winner>'),
    Rule('player-code',             '<match-id> <connection-operator> <keyword:loser>'),

    Rule('name-rule',               '<keyword:name> <string>', always_reduce=True),

    Rule('require-rule',            '<keyword:require> requirement', always_reduce=True),
    Rule('requirement',             '<keyword:exact> <number>', always_reduce=True),
    Rule('requirement',             '<keyword:min> <number> <keyword:max> <number>', always_reduce=True),
    Rule('requirement',             '<keyword:max> <number>'),

    Rule('alloc-rule',              '<keyword:alloc> <fighter-number>', always_reduce=True),

    Rule('match-rule',              '<keyword:match> <match-id> <block-begin> match-block <block-end>', always_reduce=True),

    Rule('match-block',             'mb-rule match-block', nest=0, nest_to=1),
    Rule('match-block',             'mb-rule'),

    Rule('mb-rule',                 'mb-white', always_reduce=True),
    Rule('mb-rule',                 'mb-blue', always_reduce=True),
    Rule('mb-rule',                 'mb-type', always_reduce=True),

    Rule('mb-white',                '<keyword:white> player-code', always_reduce=True),
    Rule('mb-blue',                 '<keyword:blue> player-code', always_reduce=True),

    Rule('mb-type',                 '<keyword:is> list-of-match-types'),
    Rule('list-of-match-types',     'match-type <list-operator> list-of-match-types', nest=0, nest_to=2),
    Rule('list-of-match-types',     'match-type'),

    Rule('match-type',              '<keyword:playoff>', always_reduce=True),
    Rule('match-type',              '<keyword:final>', always_reduce=True),
    Rule('match-type',              '<keyword:semifinal>', always_reduce=True),
    Rule('match-type',              '<keyword:repechage>', always_reduce=True),
    Rule('match-type',              '<keyword:thirdfinal>', always_reduce=True),


    Rule('order-rule',              '<keyword:order> order-list'),
    Rule('order-list',              'order-entry <list-operator> order-list', nest=0, nest_to=2),
    Rule('order-list',              'order-entry'),

    Rule('order-entry',             '<match-id>'),
    Rule('order-entry',             '<keyword:_clip>', always_reduce=True),

    Rule('score-rule',              '<keyword:score> <block-begin> score-block <block-end>', always_reduce=True),
    Rule('score-block',             'sb-rule score-block', nest=0, nest_to=1),
    Rule('score-block',             'sb-rule'),

    Rule('sb-rule',                 'sb-calc', always_reduce=True),
    Rule('sb-rule',                 'sb-resolve', always_reduce=True),
    Rule('sb-rule',                 'sb-first', always_reduce=True),
    Rule('sb-rule',                 'sb-second', always_reduce=True),
    Rule('sb-rule',                 'sb-third', always_reduce=True),
    Rule('sb-rule',                 'sb-fifth', always_reduce=True),

    Rule('sb-calc',                 '<keyword:calc> <keyword:points> <keyword:among> calc-group', always_reduce=True),
    Rule('calc-group',              '<keyword:all>', always_reduce=True),

    Rule('sb-resolve',              '<keyword:resolve> <keyword:playoff>', always_reduce=True),
    Rule('sb-resolve',              '<keyword:resolve> <match-id>', always_reduce=True),

    Rule('sb-first',                '<keyword:first> player-code', always_reduce=True),
    Rule('sb-second',               '<keyword:second> player-code', always_reduce=True),
    Rule('sb-third',                '<keyword:third> player-code'),
    Rule('sb-third',                '<keyword:third> player-code <list-operator> player-code', always_reduce=True),
    Rule('sb-fifth',                '<keyword:fifth> player-code'),
    Rule('sb-fifth',                '<keyword:fifth> player-code <list-operator> player-code', always_reduce=True),

    Rule('playoff-rule',            '<keyword:playoff> <block-begin> playoff-block <block-end>', always_reduce=True),
    Rule('playoff-block',           'pob-rule playoff-block', nest=0, nest_to=1),
    Rule('playoff-block',           'pob-rule'),

    Rule('pob-rule',                'pob-condition', always_reduce=True),
    Rule('pob-rule',                'pob-realloc', always_reduce=True),
    Rule('pob-rule',                'pob-condition', always_reduce=True),
    Rule('pob-rule',                'match-rule'),
    Rule('pob-rule',                'order-rule'),
    Rule('pob-rule',                'sb-first'),
    Rule('pob-rule',                'sb-second'),
    Rule('pob-rule',                'sb-third'),

    Rule('pob-condition',           '<keyword:if> pob-cond-equal2'),
    Rule('pob-condition',           '<keyword:if> pob-cond-equal3', always_reduce=True),
    Rule('pob-cond-equal2',         '<keyword:equal> <keyword:at> player-code <list-operator> player-code'),
    Rule('pob-cond-equal3',         '<keyword:equal> <keyword:at> player-code <list-operator> player-code <list-operator> player-code', always_reduce=True),

    Rule('pob-realloc',             '<keyword:realloc> pob-realloc-list'),
    Rule('pob-realloc-list',        '<fighter-number> <list-operator> pob-realloc-list', nest=0, nest_to=2),
    Rule('pob-realloc-list',        '<fighter-number>')
]