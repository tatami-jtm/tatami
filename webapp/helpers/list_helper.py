from ..listslib import compile_list, Fighter, MatchResult, get_all_lists
from ..models import db, Match, Participant

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

        struct['fighters'].append(Fighter(participant.id, participant.full_name, participant.association_name))

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

    for item in schedule:
        if item['type'] == 'match':
            match_id = item['match'].get_id()
            match_tags = item['match'].get_tags()

            if group.matches.filter_by(listslib_match_id=match_id).count() == 0:
                match = Match(event=group.event, event_class=group.event_class, group=group)
                match.white = Participant.query.filter_by(id=item['match'].get_white().get_id()).one()
                match.blue = Participant.query.filter_by(id=item['match'].get_blue().get_id()).one()
                match.is_playoff = list.is_playoff(match_id)
                match.listslib_match_id = match_id
                match.list_tags = ",".join(match_tags)

                match.scheduled = False
                match.called_up = False
                match.running = False
                match.completed = False

                db.session.add(match)

    db.session.commit()





def force_create_list(group):
    dump_list(load_list(group), group)