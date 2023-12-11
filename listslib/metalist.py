import random

from .match import Match
from .fighter import BlankFighter

ARBITRARY_MAX_VALUE = 1 << 16
MAX_PLAYOFF = 3
PLACE_MAPPING = [None, "first", "second", "third", "third", "fifth", "fifth"]

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
        self.__load_playoff_rules()

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
        self._fighter_group_allocs = {}
        for child in alloc:
            self._allocation_order.append(int(child.attrib['id']))

            if 'group' in child.attrib:
                group_name = child.attrib['group']
                self._fighter_group_allocs[self._allocation_order[-1] - 1] = group_name


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
        self._playoff_match_ids = []

        for match in self._com.findall('rules/match'):
            match_id = match.attrib['id']
            match_data = self.__load_single_match(match)

            self._matches[match_id] = match_data

        for po in self._com.findall("rules/playoff"):
            for match in po.findall('./match'):
                match_id = match.attrib['id']
                match_data = self.__load_single_match(match, po.attrib['id'])
                self._playoff_match_ids.append(match_id)

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
    def __load_single_match(self, match_xml, po_id=None):
        if (white_fighter := match_xml.find('white/fighter')) is not None:
            if po_id:
                white = {'fighter': int(white_fighter.attrib['id']), "playoff": po_id}
            else:
                white = {'fighter': int(white_fighter.attrib['id'])}

        elif (white_winner := match_xml.find('white/winner')) is not None:
            white = {'winner': white_winner.attrib['match-id']}

        elif (white_loser := match_xml.find('white/loser')) is not None:
            white = {'loser': white_loser.attrib['match-id']}

        else:
            white = None

        if (blue_fighter := match_xml.find('blue/fighter')) is not None:
            if po_id:
                blue = {'fighter': int(blue_fighter.attrib['id']), "playoff": po_id}
            else:
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

    """
        __load_playoff_rules()

        Loads the playoff rules and parses them into a single, unified representation with
        conditions, realloc, order and placement-rules.
        
        (matches are already parsed along the main ones)

        XML:

            <playoff id="...">
                <only-if-equal>
                    <points-for place="2" among="all" />
                    <points-for place="1" among="all" />
                </only-if-equal>

                <realloc random?="true|false">
                    <fighter id="..." />
                </realloc>

                <match>...</match>

                <order>
                    <match id="..." />
                </order>

                <first>
                    <winner match-id="..." />
                </first>
                <second>
                    <loser match-id="..." />
                </second>
            </playoff>
    """
    def __load_playoff_rules(self):
        self._playoff_rules = {}

        for por in self._com.findall('rules/playoff'):
            po_id = por.attrib['id']
            po_val = {
                "conditions": [],
                "realloc": [],
                "realloc_random": False,
                "match_order": [],
                "placement_rules": {}
            }

            for rule in por:
                if rule.tag == "only-if-equal":
                    condition = {
                        "equal": []
                    }

                    for child in rule:
                        if child.tag != "points-for": continue
                        condition['equal'].append({
                            "place": int(child.attrib['place']),
                            "among": child.attrib['among']
                        })
                    
                    po_val["conditions"].append(condition)

                elif rule.tag == "realloc":
                    for child in rule:
                        po_val["realloc"].append(int(child.attrib['id']))
                    
                    if "random" in rule.attrib and rule.attrib["random"] == "true":
                        po_val["realloc_random"] = True

                elif rule.tag == "match":
                    continue  # already parsed above

                elif rule.tag == "order":
                    pmo = []

                    for item in rule:
                        if item.tag == 'match':
                            pmo.append({'match': item.attrib['id']})
                        elif item.tag == 'clip':
                            pmo.append({'clip': True})

                    po_val["match_order"] += pmo

                elif rule.tag in ("first", "second", "third"):
                    pos = rule.tag
                    ref = rule[0]  # we only allow ONE placement here

                    if ref.tag == "fighter":
                        po_val["placement_rules"][pos] = { "fighter": ref.attrib['id'], "playoff": po_id }
                    elif ref.tag == "winner":
                        po_val["placement_rules"][pos] = { "winner": ref.attrib['match-id'] }
                    elif ref.tag == "loser":
                        po_val["placement_rules"][pos] = { "loser": ref.attrib['match-id'] }

            self._playoff_rules[po_id] = po_val

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
        obj._fighter_groups = {}
        obj._match_order = self._match_order[::]
        obj._match_results = {}
        obj._match_objs = {}
        obj._score_complete = False
        obj._score_deductions = {
            'results': {},
            'calced': {}
        }
        obj._playoff_data = {}
        obj._random_seed = random.randint(1, 100000)

    """
        alloc(obj, Player)

        attempts to allocate a Player on the concrete list obj using the previously loaded allocation
        order; if all list slots have been allocated, an Index error will be raised.
    """
    def alloc(self, obj, player):
        if obj._fighter_count == self.require_max():
            raise IndexError(
                f"attempting to allocate more than {self.require_max()} fighters")

        alloc_id = self._allocation_order[obj._fighter_count] - 1
        obj._fighters[alloc_id] = player
        obj._fighter_count += 1

        if alloc_id in self._fighter_group_allocs:
            group_name = self._fighter_group_allocs[alloc_id]

            if group_name not in obj._fighter_groups:
                obj._fighter_groups[group_name] = []
            
            obj._fighter_groups[group_name] += [player]

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
        if obj._fighter_count < self.require_min():
            return []

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
            - {fighter: fighterID, playoff: playoffID}
            - {winner: matchID}
            - {loser: matchID}
            - {placed: position} (but only if placements have been calculated)
            - {placed: position, group: groupID} (but only if placements have been calculated)
    """
    def _evaluate_fighter_ref(self, obj, ref):
        if 'fighter' in ref:
            if 'playoff' in ref:
                if ref['playoff'] not in obj._playoff_data:
                    return None

                return obj._playoff_data[ref['playoff']]['alloc'][ref['fighter'] - 1]
            else:
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
                    success = self.__score_resolve_playoffs(obj, func['attr'], func['props'])

                case 'resolve-match':
                    success = self.__score_resolve_match(obj, func['attr'], func['props'])

                case 'first':
                    success = self.__score_set_result(obj, 'first', func['attr'], func['props'])

                case 'second':
                    success = self.__score_set_result(obj, 'second', func['attr'], func['props'])

                case 'third':
                    success = self.__score_set_result(obj, 'third', func['attr'], func['props'])

                case 'fifth':
                    success = self.__score_set_result(obj, 'fifth', func['attr'], func['props'])

                case _:
                    success = False

            if not success:
                return False
        
        # We have succesfully executed all rules,
        # completion is therefore OK.
        obj._score_complete = True

        return True

    """
        __score_calc_points(obj, attr, props)

        calculates the points within a given scope by adding all scores+points earned
        in main matches for every fighter in the given scope-group
    """
    def __score_calc_points(self, obj, attr, props):
        scope = props['among']

        obj._score_deductions['calced'][scope] = {
            'base': [],
            'order': []
        }

        # Initialize base data with 0 points and 0 scores for every non-blank fighter
        # based on the given scope
        if scope == 'all':
            fss = obj._fighters
        else:
            if scope not in obj._fighter_groups:
                fss = []
            else:
                fss = obj._fighter_groups[scope]

        base_data = { f: (0, 0) for f in fss if f != BlankFighter }

        # Read every main match and add points/scores according to the match results
        # to white and blue
        for m in self._match_order:
            if 'clip' in m: continue

            match_id = m['match']
            mr = obj._match_results[match_id]
            mobj = mr.get_match()

            white_key = mobj.get_white()
            if white_key in base_data:  # may be false due to scopes
                wp, ws = base_data[white_key]
                base_data[white_key] = (wp + mr.get_points_white(),
                                        ws + mr.get_score_white())

            blue_key = mobj.get_blue()
            if blue_key in base_data:  # may be false due to scopes
                bp, bs = base_data[blue_key]
                base_data[blue_key] = (bp + mr.get_points_blue(),
                                       bs + mr.get_score_blue())

        # Store base data-duplicate
        obj._score_deductions['calced'][scope]['base'] = {
            k: v for k, v in base_data.items()
        }

        # Sort base data by points/scores, where equal, order is undefined
        sorted_data = sorted(base_data.items(), key=lambda i: i[1], reverse=True)

        # Store sorted data-duplicate
        obj._score_deductions['calced'][scope]['order'] = sorted_data[::]

        # We do not validate for equal scores, that is a task for the playoff-resolvers
        return True

    """
        __score_set_result(obj, on, attr, props)

        sets one of these below mentioned result slots by evaluating the given fighter
        reference and storing the fighter(s) resulting from that in the slot

            - first
            - second
            - third
            - fifth

    """
    def __score_set_result(self, obj, on, attr, props):
        fighter_refs = []

        # Transform parsed markup to valid fighter refs
        for fr in attr:
            if 'placed' in fr:
                fighter_refs += [{ "placed": int(fr['placed']['on']) }]

                if 'among' in fr['placed']:
                    fighter_refs[-1]['among'] = fr['placed']['among']

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

    """
        __score_resolve_match(obj, attr, props)

        resolves a (by-result or by-design) conflict by adding a match, unless added before;
        succeeds only if the added match has been clearly decided; fails otherwise.
    """
    def __score_resolve_match(self, obj, attr, props):
        match_id = props['id']

        if match_id in obj._match_results and obj._match_results[match_id].clearly_decided():
            return True
        
        if match_id not in obj._match_order:
            obj._match_order += [
                { "clip": True },
                { "match": match_id }
            ]

        return False

    def __score_resolve_playoffs(self, obj, attr, props):
        for po_id, po_val in self._playoff_rules.items():
            if not po_id in obj._playoff_data:
                obj._playoff_data[po_id] = {
                    'required': None,
                    'started': False,
                    'completed': False,
                    'alloc': [BlankFighter for _ in range(MAX_PLAYOFF)],
                    'results': {}
                }

            pod = obj._playoff_data[po_id]
            playoff_candidates, match_cond = self.__is_playoff_required(obj, po_id)
            pod['required'] = bool(match_cond)

            if pod['required'] and not pod['started']:

                # realloc fighters
                if po_val['realloc_random']:
                    random.seed(obj._random_seed)
                    random.shuffle(playoff_candidates)
                
                for fc, cand in enumerate(playoff_candidates):
                    alloc_id = po_val['realloc'][fc]
                    pod["alloc"][alloc_id - 1] = cand

                # schedule PO matches
                obj._match_order += po_val['match_order']

                # mark PO as started
                pod['started'] = True
                
                return False
            
            elif pod['required'] and pod['started'] and not pod['completed']:
                # Due to the pre-checking of .completed(), this can only be reached
                # if all playoff matches have been resolved

                for pos, ref in po_val["placement_rules"].items():
                    pod["results"][pos] = self._evaluate_fighter_ref(obj, ref)
                
                match_cond_keys = sorted([c['place'] for c in match_cond['equal']])

                match_results = [(PLACE_MAPPING.index(k), v) for k, v in pod["results"].items()]
                match_results = sorted(match_results, key = lambda r: r[0])

                for mr, mainpos in zip(match_results, match_cond_keys):
                    obj._score_deductions['calced']["all"]['order'][mainpos - 1] = (mr[1], "via-playoff")

                pod['completed'] = True

                return True

            else:
                return True

        return False

    def __is_playoff_required(self, obj, po_id):
        po_val = self._playoff_rules[po_id]

        for cond in po_val['conditions']:
            if 'equal' in cond:
                base_set = set()
                player_list = []

                for dp in cond['equal']:
                    score = obj._score_deductions['calced'][dp['among']]['order'][dp['place'] - 1]
                    base_set.add(score[1])
                    player_list.append(score[0])
                
                if len(base_set) == 1:
                    return player_list, cond
        
        return False, None

    """
        get_first(obj)

        returns the person placed as first in the deducted results, returns BlankFighter if
        no such placement exists, raises AssertionError if scoring has not been completed yet

        if, through some glitch, there were two (or more) people ranked as first, then only one
        of them will be returned
    """
    def get_first(self, obj):
        assert obj._score_complete, \
            "placements not available until full score evaluation"

        if not 'first' in obj._score_deductions['results']:
            return BlankFighter

        return obj._score_deductions['results']['first'][0]

    """
        get_second(obj)

        materially equivalent to get_first, except the fighter placed in the 'second' slot is
        returned
    """
    def get_second(self, obj):
        assert obj._score_complete, \
            "placements not available until full score evaluation"

        if not 'second' in obj._score_deductions['results']:
            return BlankFighter

        return obj._score_deductions['results']['second'][0]

    """
        get_third(obj)

        materially equivalent to get_first, except the fighter(s) placed in the 'third' slot is
        returned and not only one but all fighters placed in that slot are returned.
    """
    def get_third(self, obj):
        assert obj._score_complete, \
            "placements not available until full score evaluation"

        if not 'third' in obj._score_deductions['results']:
            return (BlankFighter, BlankFighter)

        return obj._score_deductions['results']['third']

    """
        get_fifth(obj)

        materially equivalent to get_third, except the fighter(s) placed in the 'fifth' slot is
        returned
    """
    def get_fifth(self, obj):
        assert obj._score_complete, \
            "placements not available until full score evaluation"

        if not 'fifth' in obj._score_deductions['results']:
            return (BlankFighter, BlankFighter)

        return obj._score_deductions['results']['fifth']
    

    """
        import_struct(self, obj, struct)

        imports previously exported list via struct into obj
    """
    def import_struct(self, obj, struct):
        self.init(obj)
        for fighter in struct['fighters']:
            self.alloc(obj, fighter)
        
        if 'random_seed' in struct:
            obj._random_seed = struct['random_seed']

        for match_id in struct['matches']:
            match_result = struct['matches'][match_id]
            match = self.get_match_by_id(obj, match_id)
            match_result.set_match(match)
            self.enter_results(obj, match_result)

        self.get_schedule(obj, False)
        self.score(obj)

        for po_match_id in struct['playoff_matches']:
            po_match_result = struct['playoff_matches'][po_match_id]
            po_match = self.get_match_by_id(obj, po_match_id)
            po_match_result.set_match(po_match)
            self.enter_results(obj, po_match_result)
        
        self.get_schedule(obj, False)
        self.score(obj)
    
    """
        export_struct(self, obj)

        export list from obj into a dictionary struct suitable for import_struct
    """
    def export_struct(self, obj):
        struct = {
            'fighters': [],
            'matches': {},
            'random_seed': obj._random_seed,
            'playoff_matches': {}
        }

        fighters_prep_list = {}

        for pos, fighter in enumerate(obj._fighters):
            absolute_pos = self._allocation_order.index(pos + 1)
            fighters_prep_list[absolute_pos] = fighter

        struct['fighters'] = [v for k, v in sorted(fighters_prep_list.items(), key=lambda o: o[0])]

        for match_id in obj._match_results:
            match_result = obj._match_results[match_id]

            if match_id in self._playoff_match_ids:
                struct['playoff_matches'][match_id] = match_result
            else:
                struct['matches'][match_id] = match_result
        
        return struct