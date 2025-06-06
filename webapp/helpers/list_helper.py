from ..listslib import compile_list, Fighter, MatchResult, get_all_lists, BlankFighter
from ..models import db, Match, Participant

from datetime import datetime as dt
import random

def load_list(group):
    list_type = group.list_system()
    list_cls = list_type.list_class()

    list = list_cls()

    struct = {
        'fighters': [],
        'matches': {},
        'playoff_matches': {},
        'options': []
    }

    if group.random_seed:
        struct['random_seed'] = group.random_seed

    for i in range(list_type.mandatory_maximum):
        participant = group.participants.filter_by(placement_index=i).first()

        if participant is None:
            struct['fighters'].append(BlankFighter)
        
        else:
            f = Fighter(participant.id, participant.full_name, participant.association_name)
            if participant.disqualified:
                f.disqualify()
            elif participant.removed:
                f.remove()
            struct['fighters'].append(f)        

    for match in group.matches.all():
        if not match.obsolete and match.has_result():
            if not match.is_playoff:
                struct['matches'][match.listslib_match_id] = match.get_result()[1]._make_list_result()
            else:
                struct['playoff_matches'][match.listslib_match_id] = match.get_result()[1]._make_list_result()

    if group.event.setting('place.differentiate-better.third', False):
        struct['options'].append("differentiate-better.third")

    if group.event.setting('place.differentiate-better.fifth', False):
        struct['options'].append("differentiate-better.fifth")

    list.import_struct(struct)

    return list

def dump_list(list, group):
    schedule = list.get_schedule()

    if list.completed():
        if not group.completed:
            group.completed = True
            group.completed_at = dt.now()

            if not group.opened:
                group.opened = True
                group.opened_at = dt.now()

        for plm, func in [(1, list.get_first), (2, list.get_second), (3, list.get_third), (5, list.get_fifth)]:
            data = func()
            if type(data) == Fighter or data == BlankFighter:
                data = [data]

            for fighter in data:
                if fighter == BlankFighter or fighter is None: continue

                local_plm = plm

                if plm == 3 and list.has_option("differentiate-better.third"):
                    if list.get_fourth() == fighter:
                        local_plm = 4

                if plm == 5 and list.has_option("differentiate-better.fifth"):
                    if list.get_sixth() == fighter:
                        local_plm = 6

                participant = Participant.query.filter_by(id=fighter.get_id()).one()
                participant.final_placement = local_plm

    if group.random_seed is None:
        group.random_seed = list._random_seed

    # validate completed matches
    for match_id in list._match_results:
        existing_match = group.matches.filter(Match.listslib_match_id==match_id, (Match.obsolete==False) | (Match.obsolete==None)).one_or_none()

        if existing_match is not None:
            existing_match = _check_if_match_is_obsolete(existing_match, list.get_match_by_id(match_id))

    for item in schedule:
        if item['type'] == 'match':
            match_id = item['match'].get_id()
            match_tags = item['match'].get_tags()
            match_no = item['match'].get_no()

            existing_match = group.matches.filter(Match.listslib_match_id==match_id, (Match.obsolete==False) | (Match.obsolete==None)).one_or_none()

            if existing_match is not None:
                existing_match = _check_if_match_is_obsolete(existing_match, item['match'])

            if existing_match is None:
                match = Match(event=group.event, event_class=group.event_class, group=group)
                db.session.add(match)

                match.white = Participant.query.filter_by(id=item['match'].get_white().get_id()).one()
                match.blue = Participant.query.filter_by(id=item['match'].get_blue().get_id()).one()
                match.is_playoff = list.is_playoff(match_id)
                match.listslib_match_id = match_id
                match.list_tags = ",".join(match_tags)
                match.match_list_no = match_no

                match.scheduled = False
                match.called_up = False
                match.running = False
                match.completed = False
                match.obsolete = False

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
    group.list_break_count = group.list_system().break_count
    group.scheduled_for = None

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


def _check_if_match_is_obsolete(dbmatch, listmatch):
    if (dbmatch.white.id != listmatch.get_white().get_id() or
        dbmatch.blue.id != listmatch.get_blue().get_id()):
        
        # Do not modify existing matches that have results
        # or are already scheduled, instead mark them as obsolete
        if dbmatch.scheduled or dbmatch.has_result() or (
            listmatch.get_white().get_id() == '__blank' or
            listmatch.get_blue().get_id() == '__blank'
        ):
            dbmatch.obsolete = True
            dbmatch.scheduled = False
            dbmatch.called_up = False
            dbmatch.running = False
            dbmatch = None

        else:
            dbmatch.white = Participant.query.filter_by(id=listmatch.get_white().get_id()).one()
            dbmatch.blue = Participant.query.filter_by(id=listmatch.get_blue().get_id()).one()

    elif dbmatch.obsolete is None:
        dbmatch.obsolete = False

    return dbmatch