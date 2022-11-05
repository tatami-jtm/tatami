from .match import Match
from .fighter import BlankFighter

ARBITRARY_MAX_VALUE = 1 << 16


class MetaList:

    def __init__(self, compilate):
        self._com = compilate

        self.__load_name()
        self.__load_requirements()
        self.__load_allocation_order()
        self.__load_matches()
        self.__load_match_order()

    def __load_name(self):
        self._name = self._com.find('meta/name').attrib['is']

    def __load_requirements(self):
        require = self._com.find('meta/require')

        min_ = 0
        max_ = ARBITRARY_MAX_VALUE

        if (minel := require.find('min')) is not None:
            min_ = int(minel.attrib['of'])

        if (maxel := require.find('max')) is not None:
            max_ = int(maxel.attrib['of'])

        if (exactel := require.find('exact')) is not None:
            min_ = max_ = int(exactel.attrib['of'])

        self._requirements = {'min': min_, 'max': max_}

    def __load_allocation_order(self):
        alloc = self._com.find('rules/alloc')
        self._allocation_order = []
        for child in alloc:
            self._allocation_order.append(int(child.attrib['id']))

    def __load_matches(self):
        self._matches = {}

        for match in self._com.findall('rules/match'):
            match_id = match.attrib['id']
            match_data = self.__load_single_match(match)

            self._matches[match_id] = match_data

        for match in self._com.findall('rules/playoff/match'):
            match_id = match.attrib['id']
            match_data = self.__load_single_match(match)

            self._matches[match_id] = match_data

    def __load_single_match(self, match_xml):
        if (white_fighter := match_xml.find('white/fighter')) is not None:
            white = {'fighter': int(white_fighter.attrib['id'])}

        elif (white_winner := match_xml.find('white/winner')) is not None:
            white = {'winner': white_winner.attrib['match-id']}

        elif (white_loser := match_xml.find('white/loser')) is not None:
            white = {'loser': white_loser.attrib['match-id']}

        else:
            white = None

        if (blue_fighter := match_xml.find('blue/fighter')) is not None:
            blue = {'fighter': int(blue_fighter.attrib['id'])}

        elif (blue_winner := match_xml.find('blue/winner')) is not None:
            blue = {'winner': blue_winner.attrib['match-id']}

        elif (blue_loser := match_xml.find('blue/loser')) is not None:
            blue = {'loser': blue_loser.attrib['match-id']}

        else:
            blue = None

        tags = []
        for tag in match_xml.findall('is'):
            tags.append(tag.attrib['a'])

        return {
            'white': white,
            'blue': blue,
            'tags': tags
        }

    def __load_match_order(self):
        self._match_order = []

        for item in self._com.find('rules/order'):
            if item.tag == 'match':
                self._match_order.append({'match': item.attrib['id']})
            elif item.tag == 'clip':
                self._match_order.append({'clip': True})

    # Managing functions:

    def get_name(self):
        return self._name

    def require_min(self):
        return self._requirements['min']

    def require_max(self):
        return self._requirements['max']

    def init(self, obj):
        obj._fighters = [BlankFighter for _ in range(self.require_max())]
        obj._fighter_count = 0
        obj._match_order = self._match_order[::]
        obj._match_results = {}
        obj._match_objs = {}

    def alloc(self, obj, player):
        if obj._fighter_count == self.require_max():
            raise IndexError(
                f"attempting to allocate more than {self.require_max()} fighters")

        obj._fighters[self._allocation_order[obj._fighter_count] - 1] = player
        obj._fighter_count += 1

    def get_schedule(self, obj, informational_only):
        if not informational_only:
            self.match_cleanup(obj)

        schedule = []

        for order_item in obj._match_order:
            if 'match' in order_item:
                # it's a match
                match = self.get_match_by_id(obj, order_item['match'], informational_only=informational_only)
                if match is None:
                    # nothing to do, yet
                    continue

                if match.get_id() in obj._match_results:
                    # do not (re-)schedule resolved matches
                    continue

                schedule.append({'type': 'match', 'match': match})

            else:
                # prevent continuous clips
                if len(schedule) == 0 or schedule[-1]['type'] == 'clip':
                    continue

                schedule.append({'type': 'clip'})
                # it's a clip

        return schedule

    def _evaluate_fighter_ref(self, obj, ref):
        if 'fighter' in ref:
            return obj._fighters[ref['fighter'] - 1]

        if 'winner' in ref or 'loser' in ref:
            if 'winner' in ref: match_id = ref['winner']
            if 'loser' in ref:  match_id = ref['loser']

            if match_id not in obj._match_results:
                return None

            result = obj._match_results[match_id]

            if result.is_white_winner():
                if 'winner' in ref: return result.get_match().get_white()
                else:               return result.get_match().get_blue()
            elif result.is_blue_winner():
                if 'winner' in ref: return result.get_match().get_blue()
                else:               return result.get_match().get_white()
            elif result.get_absolute_winner() == 'blank':
                return BlankFighter
            else:
                # undecided yet (strangely the result is in, though)
                return None

    def get_match_by_id(self, obj, match_id, informational_only=False):
        if match_id in obj._match_objs:
            return obj._match_objs[match_id]
        
        else:
            match = self._matches[match_id]
            white = self._evaluate_fighter_ref(obj, match['white'])
            blue = self._evaluate_fighter_ref(obj, match['blue'])

            if None in (white, blue):
                return None

            new_match = Match(match_id, white, blue, match['tags'])

            if not informational_only:
                obj._match_objs[match_id] = new_match

            return new_match

    def enter_results(self, obj, match_result):
        match_id = match_result.get_match().get_id()

        obj._match_results[match_id] = match_result

        if match_id in obj._match_order:
            obj._match_order.remove(match_id)

    # should be called regularly
    def match_cleanup(self, obj):
        for matchid in self._matches.keys():
            match = self.get_match_by_id(obj, matchid)

            if match is None: # unable to calculate so far
                continue
            
            white_disqualified = match.get_white().is_disqualified()
            blue_disqualified = match.get_blue().is_disqualified()

            if white_disqualified and blue_disqualified:
                mr = match.mk_result()
                mr.set_absolute_winner('blank')
                mr.set_data_white((), (), True)
                mr.set_data_blue((), (), True)
                self.enter_results(obj, mr)

            elif blue_disqualified:
                mr = match.mk_result()
                mr.set_absolute_winner('white')
                mr.set_data_white((), (), False)
                mr.set_data_blue((), (), True)
                self.enter_results(obj, mr)
            elif white_disqualified:
                mr = match.mk_result()
                mr.set_absolute_winner('blue')
                mr.set_data_white((), (), True)
                mr.set_data_blue((), (), False)
                self.enter_results(obj, mr)

    def completed(self, obj):
        for obligatory_match in self._match_order:
            if 'match' not in obligatory_match: continue

            if obligatory_match['match'] not in obj._match_results:
                return False
            
            if not obj._match_results[obligatory_match['match']].clearly_decided():
                return False
        
        return True

    def score(self, obj):
        pass

    def get_first(self, obj):
        pass

    def get_second(self, obj):
        pass

    def get_third(self, obj):
        pass

    def get_fifth(self, obj):
        pass
