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
            min_ = minel.attrib['of']

        if (maxel := require.find('max')) is not None:
            max_ = maxel.attrib['of']

        if (exactel := require.find('exact')) is not None:
            min_ = max_ = exactel.attrib['of']

        self._requirements = {'min': min_, 'max': max_}

    def __load_allocation_order(self):
        alloc = self._com.find('rules/alloc')
        self._allocation_order = []
        for child in alloc:
            self._allocation_order.append(child.attrib['id'])

    def __load_matches(self):
        self._matches = {}

        for match in self._com.findall('rules/match'):
            match_id = match.attrib['id']
            match_data = self.__load_single_match(match)

            self._matches[match_id] = match_data

    def __load_single_match(self, match_xml):
        if (white_fighter := match_xml.find('white/fighter')) is not None:
            white = {'fighter': white_fighter.attrib['id']}

        elif (white_winner := match_xml.find('white/winner')) is not None:
            white = {'winner': white_winner.attrib['match-id']}

        elif (white_loser := match_xml.find('white/loser')) is not None:
            white = {'loser': white_loser.attrib['match-id']}

        else:
            white = None

        if (blue_fighter := match_xml.find('blue/fighter')) is not None:
            blue = {'fighter': blue_fighter.attrib['id']}

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
        pass

    def alloc(self, obj, player):
        pass

    def get_schedule(self, obj):
        pass

    def get_match_by_id(self, obj, match_id):
        pass

    def enter_results(self, obj, match_id, match_result):
        pass

    def completed(self, obj):
        pass

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
