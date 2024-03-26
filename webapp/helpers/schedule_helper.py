from ..models import db
from .list_helper import load_list
from datetime import datetime as dt

def make_config(max_concurrent_groups, max_concurrent_participants):
    return (max_concurrent_groups, max_concurrent_participants)


def get_next_match(group):
    list_system = load_list(group)
    open_matches = group.matches.filter_by(scheduled=False)
    schedule = list_system.get_schedule()

    for item in schedule:
        if item['type'] == 'clip':
            return None

        elif item['type'] == 'match':
            match = item['match']
            match_object = open_matches.filter_by(listslib_match_id=match.get_id()).one_or_none()

            if match_object is None:
                continue

            white = match_object.white
            blue = match_object.blue
            now = dt.now()
            break_time = group.event_class.between_fights_time

            if white.last_fight_at is not None:
                if (now - white.last_fight_at).total_seconds() < break_time:
                    continue
            
            if blue.last_fight_at is not None:
                if (now - blue.last_fight_at).total_seconds() < break_time:
                    continue
            
            return match

    return None


def get_next_list(groups, config):
    if should_open_list(groups, config):
        next_list = open_which_list(groups, config)
        open_list(next_list)
    else:
        next_list = least_recently_used_list(groups)

    return next_list


# greedy algorithm that will always recommend to open a list if
# the two configurable limits of
# - MAX_CONCURRENT_GROUPS, and
# - MAX_CONCURRENT_PARTICIPANTS
# are not exceeded
def should_open_list(groups, config):
    open_groups = groups.filter_by(opened=True).all()
    if len(open_groups) > config[0]:
        return False
    
    participant_count = sum(map(lambda g: g.participants.count(), open_groups))

    if participant_count > config[1]:
        return False
    
    return True


# Return of the lists which have been marked ready but have not been
# opened yet the list that has the most breaks and if there is a tie
# with that the one with the most participants to open
def open_which_list(groups, config):
    not_yet_opened_groups = groups.filter_by(marked_ready=True, opened=False, completed=False)

    not_yet_opened_groups = sorted(not_yet_opened_groups, key=lambda gr: (gr.list_system().break_count, gr.participants.count()), reverse=True)

    return not_yet_opened_groups[0]


def least_recently_used_list(groups, config):
    return groups.filter_by(opened=True).sort_by('last_used_at').first()


def open_list(list):
    list.opened = True
    list.opened_at = dt.now()
    list.last_used_at = dt.min

    db.session.commit()