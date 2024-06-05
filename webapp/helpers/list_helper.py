from ..listslib import compile_list, Fighter, MatchResult, get_all_lists, BlankFighter
from ..models import db, Match, Participant

from datetime import datetime as dt
import random

def load_list(group):
    list_type = group.list_system()
    list_cls = compile_list(list_type.list_file)

    list = list_cls()
    struct = {
        'fighters': [],
        'matches': {},
        'playoff_matches': {}
    }

    if group.random_seed:
        struct['random_seed'] = group.random_seed
    
    for participant in group.participants.order_by('placement_index'):
        if participant.placement_index is None:
            continue

        f = Fighter(participant.id, participant.full_name, participant.association_name)
        if participant.disqualified:
            f.disqualify()
        struct['fighters'].append(f)

    for match in group.matches.all():
        if match.has_result():
            if not match.is_playoff:
                struct['matches'][match.listslib_match_id] = match.get_result()[1]._make_list_result()
            else:
                struct['playoff_matches'][match.listslib_match_id] = match.get_result()[1]._make_list_result()

    list.import_struct(struct)

    return list

def dump_list(list, group):
    schedule = list.get_schedule()

    if list.completed():
        if not group.completed:
            group.completed = True
            group.completed_at = dt.now()

        for plm, func in [(1, list.get_first), (2, list.get_second), (3, list.get_third), (5, list.get_fifth)]:
            data = func()
            if type(data) == Fighter or data == BlankFighter:
                data = [data]

            for fighter in data:
                if fighter == BlankFighter: continue

                participant = Participant.query.filter_by(id=fighter.get_id()).one()
                participant.final_placement = plm

    if group.random_seed is None:
        group.random_seed = list._random_seed

    for item in schedule:
        if item['type'] == 'match':
            match_id = item['match'].get_id()
            match_tags = item['match'].get_tags()

            if group.matches.filter_by(listslib_match_id=match_id).count() == 0:
                match = Match(event=group.event, event_class=group.event_class, group=group)
                db.session.add(match)

                match.white = Participant.query.filter_by(id=item['match'].get_white().get_id()).one()
                match.blue = Participant.query.filter_by(id=item['match'].get_blue().get_id()).one()
                match.is_playoff = list.is_playoff(match_id)
                match.listslib_match_id = match_id
                match.list_tags = ",".join(match_tags)

                match.scheduled = False
                match.called_up = False
                match.running = False
                match.completed = False


    db.session.commit()





def force_create_list(group):
    dump_list(load_list(group), group)


def reset_list(group):
    group.marked_ready = False
    group.marked_ready_at = None
    group.opened = False
    group.opened_at = None
    group.completed = False
    group.completed_at = None
    group.currently_used = False
    group.last_used_at = None

    for participant in group.participants:
        participant.final_placement = None
        participant.final_points = None
        participant.final_score = None
        participant.removed = False
        participant.disqualified = False
        participant.removal_cause = None
        participant.last_fight_at = None

    for match in group.matches:
        for result in match.results:
            db.session.delete(result)
        
        db.session.delete(match)

    db.session.commit()