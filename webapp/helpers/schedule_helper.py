from ..models import db, Match
from .list_helper import load_list
from datetime import datetime as dt

LIMIT_OF_FORECAST_FOR_SCHEDULE = 5

def do_match_schedule(mat):
    config = make_config(
        mat.event.setting('scheduling.max_concurrent_groups', 3),
        mat.event.setting('scheduling.max_concurrent_participants', 30)
    )

    # Attempt to schedule up to LIMIT_OF_FORECAST_FOR_SCHEDULE matches
    # from all the groups

    attempts = 2 * LIMIT_OF_FORECAST_FOR_SCHEDULE

    while len(mat.scheduled_matches()) < LIMIT_OF_FORECAST_FOR_SCHEDULE:
        attempts -= 1

        if attempts == 0:
            break

        selected_group = mat.assigned_groups.filter_by(currently_used=True).one_or_none()

        if selected_group is None:
            selected_group = get_next_list(mat.assigned_groups.filter_by(completed=False), config)

            if selected_group is None:
                continue
            
            if not selected_group.opened:
                selected_group.opened = True
                selected_group.opened_at = dt.now()

            selected_group.currently_used = True
            selected_group.last_used_at = dt.now()
            db.session.commit()
        
        next_match = get_next_match(selected_group)

        if next_match is None:
            selected_group.currently_used = False
            selected_group.last_used_at = dt.now()
            db.session.commit()

            continue  # possibly enter break

        max_schedule_key = next_match.group.event_class.matches.filter_by(scheduled=True) \
            .order_by(Match.match_schedule_key.desc()).first()
        
        next_match.scheduled = True
        next_match.scheduled_at = dt.now()
        next_match.match_schedule_key = (max_schedule_key.match_schedule_key if max_schedule_key is not None else 0) + 1
        next_match.white.last_fight_at = dt.now()
        next_match.blue.last_fight_at = dt.now()

    # Promote/Choose current and waiting match from scheduled

    current_match = mat.current_match()
    waiting_match = mat.waiting_match()
    
    scheduled_matches = mat.scheduled_matches(include_called_up=False)
    if current_match is None:
        if waiting_match is not None:
            # promote waiting match
            waiting_match.running = True
            waiting_match.running_since = dt.now()

        elif len(scheduled_matches):
            # choose current match
            oldest_scheduled_match = scheduled_matches[0]
            oldest_scheduled_match.called_up = True
            oldest_scheduled_match.called_up_at = dt.now()
            oldest_scheduled_match.running = True
            oldest_scheduled_match.running_since = dt.now()

    scheduled_matches = mat.scheduled_matches(include_called_up=False)
    if mat.waiting_match() is None:
        if len(scheduled_matches):
            oldest_scheduled_match = scheduled_matches[0]
            oldest_scheduled_match.called_up = True
            oldest_scheduled_match.called_up_at = dt.now()
    
    db.session.commit()


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
            
            return match_object

    return None


def get_next_list(groups, config):
    if should_open_list(groups, config):
        next_list = open_which_list(groups, config)

        if next_list is not None:
            open_list(next_list)
            return next_list

        else:
            return least_recently_used_list(groups)
        

    else:
        return least_recently_used_list(groups)


# greedy algorithm that will always recommend to open a list if
# the two configurable limits of
# - MAX_CONCURRENT_GROUPS, and
# - MAX_CONCURRENT_PARTICIPANTS
# are not exceeded
def should_open_list(groups, config):
    open_groups = groups.filter_by(opened=True).all()
    if len(open_groups) >= config[0]:
        return False
    
    participant_count = sum(map(lambda g: g.participants.count(), open_groups))

    if participant_count >= config[1]:
        return False
    
    return True


# Return of the lists which have been marked ready but have not been
# opened yet the list that has the most breaks and if there is a tie
# with that the one with the most participants to open
def open_which_list(groups, config):
    not_yet_opened_groups = groups.filter_by(marked_ready=True, opened=False, completed=False).all()

    if len(not_yet_opened_groups) == 0:
        return None

    not_yet_opened_groups = sorted(not_yet_opened_groups, key=lambda gr: (gr.list_system().break_count, gr.participants.count()), reverse=True)

    return not_yet_opened_groups[0]


def least_recently_used_list(groups):
    query = groups.filter_by(opened=True).order_by('last_used_at')

    if query.count() != 0:
        return query.first()
    else:
        return None


def open_list(list):
    list.opened = True
    list.opened_at = dt.now()
    list.last_used_at = dt.min

    db.session.commit()