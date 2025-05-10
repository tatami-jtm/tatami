from ..models import db, Match
from .list_helper import load_list
from datetime import datetime as dt

def do_promote_scheduled_fights(mat):
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


def do_match_schedule(mat):
    config = make_config(
        mat.event.setting('scheduling.max_concurrent_groups', 3),
        mat.event.setting('scheduling.max_concurrent_participants', 30)
    )

    # Attempt to schedule up to LIMIT_OF_FORECAST_FOR_SCHEDULE matches
    # from all the groups

    LIMIT_OF_FORECAST_FOR_SCHEDULE = mat.event.setting('scheduling.plan_ahead', 5)

    attempts = 2 * LIMIT_OF_FORECAST_FOR_SCHEDULE

    while len(mat.scheduled_matches()) < LIMIT_OF_FORECAST_FOR_SCHEDULE:
        attempts -= 1

        if attempts == 0:
            break

        # if we have a current group, check if there is a valid, first fight in it -> end
        selected_group = mat.assigned_groups.filter_by(currently_used=True).one_or_none()

        if selected_group is not None:
            next_match = get_next_match(selected_group)

            if next_match is None or not next_match.schedulable():
                # if not, if the current group's next item is a break, decrease group break counter
                if next_match is None:
                    selected_group.list_break_count -= 1

                # clear current groups scheduled-for key and current group status
                selected_group.currently_used = False
                selected_group.scheduled_for = None
                selected_group.last_used_at = dt.now()
                db.session.commit()
            else:
                # we have a match, yay

                max_schedule_key = next_match.group.event_class.matches.filter_by(scheduled=True) \
                    .order_by(Match.match_schedule_key.desc()).first()
                
                next_match.scheduled = True
                next_match.scheduled_at = dt.now()
                next_match.device_position = next_match.group.assigned_to_position
                next_match.match_schedule_key = (max_schedule_key.match_schedule_key if max_schedule_key is not None else 0) + 1
                next_match.white.last_fight_at = dt.now() + \
                    next_match.group.estimated_average_fight_duration_delta()

                next_match.blue.last_fight_at = dt.now() + \
                    next_match.group.estimated_average_fight_duration_delta()

                continue

        # if we have a group with a scheduled-for key, choose the one with the
        # lowest key as current group, then restart

        selected_group = get_next_list(mat.assigned_groups.filter_by(completed=False), config)

        if selected_group is None:
            continue
        
        if not selected_group.opened:
            selected_group.opened = True
            selected_group.opened_at = dt.now()

        selected_group.currently_used = True
        selected_group.last_used_at = dt.now()
        db.session.commit()
    
    db.session.commit()


def make_config(max_concurrent_groups, max_concurrent_participants):
    return (max_concurrent_groups, max_concurrent_participants)


def get_next_match(group):
    list_system = load_list(group)
    open_matches = group.matches.filter(
        Match.scheduled==False,
        (Match.obsolete==False) | (Match.obsolete==None)
    )
    schedule = list_system.get_schedule()

    for item in schedule:
        if item['type'] == 'clip':
            return None

        elif item['type'] == 'match':
            match = item['match']
            match_object = open_matches.filter_by(listslib_match_id=match.get_id()).one_or_none()

            if match_object is None:
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
            return get_blockspread_or_presaved_list(groups)
        

    else:
        return get_blockspread_or_presaved_list(groups)


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


def get_blockspread_or_presaved_list(groups):
    groups = groups.filter_by(opened=True).order_by('scheduled_for').all()

    if len(groups) == 0:
        return None

    if groups[0].scheduled_for is not None:
        return groups[0]
    
    group_blocks = { str(group.id) : max(group.list_break_count, 1) for group in groups }

    groups = { group.id: group for group in groups}

    first_block = _blockspread(**group_blocks)[0]

    first_block_groups = sorted(
        [groups[int(gid)] for gid in first_block],
        key = lambda group: group.last_used_at
    )

    for i in range(len(first_block_groups)):
        first_block_groups[i].scheduled_for = i
    
    db.session.commit()

    return first_block_groups[0]


def open_list(list):
    list.opened = True
    list.opened_at = dt.now()
    list.last_used_at = dt.min

    db.session.commit()


def _blockspread(**blocks):
    block_names = blocks.keys()
    sorted_block_names = sorted(block_names, key=lambda b: blocks[b], reverse=True)

    largest_block, *other_blocks = sorted_block_names
    
    # spread largest block
    spread = [(largest_block,) for _ in range(blocks[largest_block])]
    
    for block in other_blocks:
        size = blocks[block]
        
        min_i = 0
        min_ct = None
        
        for i in range(len(spread)):
            if min_ct is None or len(spread[i]) <= min_ct:
                min_i = i
                min_ct = len(spread[i])

        # we need to go back from the end
        if min_i + size >= len(spread):
            for i in range(size):
                spread[-i - 1] = (*spread[-i - 1], block)

        # we need to start from the beginning
        elif size > min_i:
            for i in range(size):
                spread[i] = (*spread[i], block)

        # go before min_i because everything afterwards is definitely larger
        else:
            for i in range(size):
                spread[min_i - i] = (*spread[min_i - i], block)

    return spread