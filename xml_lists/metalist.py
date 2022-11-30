from .match import Match
from .fighter import BlankFighter

ARBITRARY_MAX_VALUE = 1 << 16

"""
    MetaList

    is the working-core facility for all match lists, it extracts the data from the
    loaded XML rulesets and is called by List instances to make everything work.
"""
class MetaList:

    """
        __init__(compilate)

        Initializes the MetaList, being given a compilate (the ElementTree of the XML ruleset)
        and then loading the name, the requirements and all other technical details of the list
    """
    def __init__(self, compilate):
        self._com = compilate

        self.__load_name()
        self.__load_requirements()
        self.__load_allocation_order()
        self.__load_matches()
        self.__load_match_order()
        self.__load_score_rules()

    """
        __load_name()

        Loads the list type name attribute out of the compilate and stores it in ._name

        XML:

            <ruleset>
                <meta>
                    <name is="..." />
                </meta>
            </ruleset>
    """
    def __load_name(self):
        self._name = self._com.find('meta/name').attrib['is']

    """
        __load_requirements()

        Loads and interpretes the requirements (in the form of either exact or min/max) out of
        the compilate and stores them in a {min:..., max:...} dictionary.

        Default values used are 0 and ARBITRARY_MAX_VALUE == 65536 (I consider it safe to presume,
        for now, that no list will ever support more than 65536 participants, already due to
        practical concerns; however in case such support were needed, it could easily be added
        by increasing the number; also: this number is unlikely to be used anyway since most lists
        - if not all - will have a maximum requirement, even if no minimum one)

        XML:

            <ruleset>
                <meta>
                    <require>
                        <min of="..." />
                        <max of="..." />        or:
                        <exact of="..." />
                    </require>
                </meta>
            </ruleset>
    """
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

    """
        __load_allocation_order()

        Loads the order, in which fighters will be allocated, from the compilate and stores it in _allocation_order.
        This order is to be understood in the way, that the first entered fighter will be put into the position set
        by the first allocate directive, the second into the position set by the second directive etc.

        For POOL lists, this is likely to be just 1, 2, 3, ... up to max
        For KO lists, this is likely to be binary swapping at the main axes
        for PREPOOLED lists, this is likely to be swapping between the two pools

        XML:

            <ruleset>
                <rules>
                    <alloc>
                        <fighter id="..." />
                        <fighter id="..." />
                        <fighter id="..." />
                        <fighter id="..." />
                    </alloc>
                </rules>
            </ruleset>
    """
    def __load_allocation_order(self):
        alloc = self._com.find('rules/alloc')
        self._allocation_order = []
        for child in alloc:
            self._allocation_order.append(int(child.attrib['id']))

    """
        __load_matches()

        Loads the general matches and the playoff matches into the list management; each match has an *unique* ID
        (they must be unique among all general *and* playoff matches) under which it will be refered to later.

        XML:

            <ruleset>
                <rules>
                    <match id="BvC">
                        ...
                    </match>
                </rules>
            </ruleset>
    """
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

    """
        __load_single_match()

        Called for every match by __load_matches; parses the inner workings of a match (<white>, <blue> and <is />)
        and transforms that into an abstract match dictionary, which is then returned

        XML:

            <match id="BvC">
                <white><fighter id="1" /></white>
                <blue><winner match-id="AvB" /></blue>
                <is a="repechage" />
            </match>
    """
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

    """
        __load_match_order()

        Loads the match order (but only for the general matches, not for playoffs) from the compilate.
        Each match is identified by the global ID; there may be <clip />s between matches to indicate
        where the list should be clipped and either a break or an other list should be put.

        XML:

            <ruleset>
                <rules>
                    <order>
                        <match id="..." />
                        <clip />
                        <match id="..." />
                    </order>
                </rules>
            </ruleset>
    """
    def __load_match_order(self):
        self._match_order = []

        for item in self._com.find('rules/order'):
            if item.tag == 'match':
                self._match_order.append({'match': item.attrib['id']})
            elif item.tag == 'clip':
                self._match_order.append({'clip': True})

    """
        __load_score_rules()

        Loads the score rules and parses them into a single, unified command/attr representation.

        XML:

            <score>
                <calc-points among="all" />

                <resolve-playoffs />

                <first>
                    <placed on="... />
                </first>
                <second>
                    <winner match-id="..." />
                </second>
                <third>
                    <loser match-id="..." />
                    <fighter id="..." />
                </third>
            </score>
    """
    def __load_score_rules(self):
        self._score_rules = []

        for rule in self._com.findall('rules/score/*'):
            cmd = rule.tag
            props = {
                k: v for k,v in rule.items()
            }
            attr = []

            for child in rule:
                attr += [{child.tag: {
                    k: v for k,v in child.items()
                }}]
            
            self._score_rules.append({
                "cmd": cmd,
                "attr": attr,
                "props": props
            })

    # Managing functions:

    """
        get_name()

        Returns the name of this list type (as previously loaded)
    """
    def get_name(self):
        return self._name

    """
        require_min()

        Returns the minimum fighter number requirement (as previously loaded)
    """
    def require_min(self):
        return self._requirements['min']

    """
        require_max()

        Returns the maximum fighter number requirement (as previously loaded)
    """
    def require_max(self):
        return self._requirements['max']

    """
        init(obj)

        takes an - empty - List() object and adds the data fields required by the MetaList
        in order for it to function.

        The List() class has functions mimicking the managing functions of this class, but the
        class will be given a .meta class attribute which will contain a MetaList instance; all
        functions on List() refer back to MetaList for functionality. This is to allow the
        benefits of having an instantiable class type without sacrificing the flexibility of an
        instance/having to struggle with nasty meta programming/self manipulation of objects
    """
    def init(self, obj):
        obj._fighters = [BlankFighter for _ in range(self.require_max())]
        obj._fighter_count = 0
        obj._match_order = self._match_order[::]
        obj._match_results = {}
        obj._match_objs = {}
        obj._score_complete = False
        obj._score_deductions = {
            'results': {},
            'calced': {}
        }

    """
        alloc(obj, Player)

        attempts to allocate a Player on the concrete list obj using the previously loaded allocation
        order; if all list slots have been allocated, an Index error will be raised.
    """
    def alloc(self, obj, player):
        if obj._fighter_count == self.require_max():
            raise IndexError(
                f"attempting to allocate more than {self.require_max()} fighters")

        obj._fighters[self._allocation_order[obj._fighter_count] - 1] = player
        obj._fighter_count += 1

    """
        get_schedule(obj, informational_only)

        generates and returns a schedule of upcoming matches and, where defined by the obj match order, clips;
        matches that have already been resolved or matches where either party cannot yet be determined will not
        be scheduled.

        If informational_only is set to False (which should be the default), then get_schedule might change the
        data to provide a better schedule output, however this is irreversible and might cause issues if not all
        slots have been allocated yet.
    """
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

    """
        _evaluate_fighter_ref(obj, ref)

        evaluates a reference to a fighter and returns the found fighter or None, if not found

        Possible reference forms:

            - {fighter: fighterID}
            - {winner: matchID}
            - {loser: matchID}
            - {placed: position} (but only if placements have been calculated)
            - {placed: position, group: groupID} (but only if placements have been calculated)
    """
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
                # there is no winner, this only happens if both parties are
                # disqualified (direct hansoku-make or blank fighters);
                # no player advances as either winner or loser
                return BlankFighter
            else:
                # undecided yet (strangely the result is in, though)
                return None

        if 'placed' in ref:
            scope = 'all'

            if 'among' in ref:
                scope = ref['among']

            if scope not in obj._score_deductions['calced']:
                return None
                
            return obj._score_deductions['calced'][scope]['order'][ref['placed'] - 1][0]

    """
        get_match_by_id(obj, match_id, informational_only=False)

        looks for, and if not existing, creates a applied match object for the given match_id;
        if information_only is True, then match objects will not be stored in the database, this
        also means that a new match object will be created next time this function is called.
    """
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

    """
        enter_results(obj, match_result)

        enters the results as defined by match_result into the data of obj; if the match that has been
        resolved is still scheduled; it will be removed.
    """
    def enter_results(self, obj, match_result):
        match_id = match_result.get_match().get_id()

        obj._match_results[match_id] = match_result

        # Remove resolved match, if still scheduled
        if (mo := { 'match': match_id }) in obj._match_order:
            obj._match_order.remove(mo)

    # should be called regularly
    """
        match_cleanup(obj)

        cleans up matches that can be resolved right now without further consideration, i.e. those where
        either party (or both) are disqualified (this means either direct hansoku-make or blank fighter, i.e.
        a fighter slot that has not been allocated)
    """
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

    """
        _filtered_match_oder(obj)

        returns a match order where duplicate clips and clips at beginning/end
        are removed (only for completeness-consideration intended)
    """
    def _filtered_match_order(self, obj):
        new_mo = []

        for item in obj._match_order:
            if 'clip' in item:
                if len(new_mo) == 0 or 'clip' in new_mo[-1]:
                    continue
            
            new_mo.append(item)

        if len(new_mo) and 'clip' in new_mo[-1]:
            new_mo = new_mo[:-1]

        return new_mo

    """
        completed(obj)

        returns, whether all obligatory matches (that are those, which are in the general order)
        have been resolved and are clearly decided (either white or blue wins); also there must not
        be any matches scheduled (playoff matches).
    """
    def completed(self, obj):
        if len(self._filtered_match_order(obj)) != 0:
            return False

        for obligatory_match in self._match_order:
            if 'match' not in obligatory_match: continue

            if obligatory_match['match'] not in obj._match_results:
                return False
            
            if not obj._match_results[obligatory_match['match']].clearly_decided():
                return False
        
        return True

    """
        score(obj)

        executes - if still needed - the scoring rules in order until either all succeed or any fails,
        if successful (or a successful execution has already been), then returns True, otherwise, if
        execution fails in any part, if the list is not yet completed or any other fixable issue occurs,
        returns False. If False is returned, you should check for completed() which should return False
        indicating open (or newly opened) matches necessary to resolve the scoring.
    """
    def score(self, obj):
        if not self.completed(obj):
            return False

        if obj._score_complete:
            return True
        
        for func in self._score_rules:
            match func['cmd']:
                case 'calc-points':
                    success = self.__score_calc_points(obj, func['attr'], func['props'])
                
                case 'resolve-playoffs':
                    success = True  # TODO: later

                case 'resolve-fight':
                    success = True  # TODO: later

                case 'first':
                    success = self.__score_set_result(obj, 'first', func['attr'], func['props'])

                case 'second':
                    success = self.__score_set_result(obj, 'second', func['attr'], func['props'])

                case 'third':
                    success = self.__score_set_result(obj, 'second', func['attr'], func['props'])

                case 'fifth':
                    success = self.__score_set_result(obj, 'second', func['attr'], func['props'])

                case _:
                    success = False

            if not success:
                return False
        
        # We have succesfully executed all rules,
        # completion is therefore OK.
        obj._score_complete = True

        return True

    def __score_calc_points(self, obj, attr, props):
        scope = props['among']

        obj._score_deductions['calced'][scope] = {
            'base': [],
            'order': []
        }

        # Initialize base data with 0 points and 0 scores for every non-blank fighter
        # TODO: WE IGNORE SCOPE FOR NOW, WILL BE ADDED LATER
        base_data = { f: (0, 0) for f in obj._fighters if f != BlankFighter }

        # Read every main match and add points/scores according to the match results
        # to white and blue
        for m in self._match_order:
            if 'clip' in m: continue

            match_id = m['match']
            mr = obj._match_results[match_id]
            mobj = mr.get_match()

            white_key = mobj.get_white()
            wp, ws = base_data[white_key]
            base_data[white_key] = (wp + mr.get_points_white(),
                                    ws + mr.get_score_white())

            blue_key = mobj.get_blue()
            wp, ws = base_data[blue_key]
            base_data[blue_key] = (wp + mr.get_points_blue(),
                                   ws + mr.get_score_blue())

        # Store base data-duplicate
        obj._score_deductions['calced'][scope]['base'] = { k: v for k, v in base_data.items() }

        # Sort base data by points/scores, where equal, order is undefined
        sorted_data = sorted(base_data.items(), key=lambda i: i[1], reverse=True)

        # Store sorted data-duplicate
        obj._score_deductions['calced'][scope]['order'] = sorted_data[::]

        # We do not validate for equal scores, that is a task for the playoff-resolvers
        return True

    def __score_set_result(self, obj, on, attr, props):
        fighter_refs = []

        # Transform parsed markup to valid fighter refs
        for fr in attr:
            if 'placed' in fr:
                fighter_refs += [{ "placed": int(fr['placed']['on']) }]

                if 'among' in fr:
                    fighter_refs[-1]['among'] = fr['among']

            elif 'winner' in fr:
                fighter_refs += [{ "winner": fr['winner']['match-id'] }]
            elif 'loser' in fr:
                fighter_refs += [{ "loser": fr['loser']['match-id'] }]
            elif 'fighter' in fr:
                fighter_refs += [{ "fighter": int(fr['fighter']['id']) }]

        # Evaluate references
        fighters = []
        for fr in fighter_refs:
            fighters += [self._evaluate_fighter_ref(obj, fr)]

        # Store results
        obj._score_deductions['results'][on] = fighters

        return True

    def get_first(self, obj):
        assert obj._score_complete, \
            "placements not available until full score evaluation"

        if not 'first' in obj._score_deductions['results']:
            return BlankFighter

        return obj._score_deductions['results']['first'][0]

    def get_second(self, obj):
        assert obj._score_complete, \
            "placements not available until full score evaluation"

        if not 'second' in obj._score_deductions['results']:
            return BlankFighter

        return obj._score_deductions['results']['second'][0]

    def get_third(self, obj):
        assert obj._score_complete, \
            "placements not available until full score evaluation"

        if not 'third' in obj._score_deductions['results']:
            return (BlankFighter, BlankFighter)

        return obj._score_deductions['results']['third']

    def get_fifth(self, obj):
        assert obj._score_complete, \
            "placements not available until full score evaluation"

        if not 'fifth' in obj._score_deductions['results']:
            return (BlankFighter, BlankFighter)

        return obj._score_deductions['results']['fifth']
