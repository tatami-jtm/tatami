import math

def group_by_proximity(items, max_delta, max_size, max_count, priority, *, delta_match_func=None, item_weight_func=None):
    if delta_match_func is None:
        delta_match_func = (lambda w1, w2, max_delta: w1 - w2 <= max_delta)
    
    if item_weight_func is None:
        item_weight_func = lambda item: item

    items = sorted(items, key=item_weight_func)
    
    if priority == 'size':
        return group_by_size(items, max_delta, max_size, max_count, priority, delta_match_func, item_weight_func)
    
    elif priority == 'count':
        return group_by_count(items, max_delta, max_size, max_count, priority, delta_match_func, item_weight_func)
    
    else:
        raise ValueError('priority must be either "size" or "count"')

# Group with size as priority
# i.e.: the max_size constraint must always be met, even if this means we might not meet the max_count constraint
def group_by_size(items, max_delta, max_size, max_count, priority, delta_match_func, item_weight_func):
    # (ref_back, break_here, group_count)
    DP_cache = []

    for i in range(len(items)):
        value = items[i]

        # Always create group for first item
        if i == 0:
            DP_cache.append((-1, True, 0))
        
        # Otherwise create stub item (that would create a new group)
        else:
            DP_cache.append((i, True, DP_cache[-1][2] + 1))

        # Initialize default values for lookup
        current_optimal_gc = None
        current_optimal_lookup = None
        do_break = False

        for pre in range(max_size):
            lookup = i - pre

            # ignore impossible values (if i is still smaller than max_size)
            if lookup < 0:
                continue
            
            # Take the current value if we don't have one yet
            # this would always be the stub value we just added
            # -> this would break before this item
            if current_optimal_gc is None:
                current_optimal_gc = DP_cache[lookup][2]
                current_optimal_lookup = lookup
                do_break = True

            # Otherwise: perform a lookup
            else:
                looked_up_value = items[lookup]

                # we are too far away re: max_delta, thus stop looking
                if not delta_match_func(item_weight_func(value), item_weight_func(looked_up_value), max_delta):
                    break

                # set the new group count if we broke before the looked up item
                if lookup == 0:
                    new_gc = 0
                else:
                    new_gc = DP_cache[lookup - 1][2] + 1

                # if this is the first better case than every other one before, set this lookup as new optimal
                if current_optimal_gc > new_gc:
                    current_optimal_gc = new_gc
                    current_optimal_lookup = lookup
                    do_break = False
        
        # update stub item to reflect lookup
        DP_cache[-1] = (current_optimal_lookup, do_break, current_optimal_gc)

    # now to apply the DP_cache
    groups = []
    ptr = None
    for i in range(len(items))[::-1]:
        value = items[i]
        cache = DP_cache[i]

        if ptr is None:
            ptr = cache[0]
            groups.append([])

        if cache[0] >= ptr:
            groups[-1].append(value)
        else:
            ptr = cache[0]
            groups.append([value])

    return list(map(lambda x: x[::-1], groups[::-1]))

# Group with count as priority
# i.e.: the max_count constraint must always be met, even if this means we might not meet the max_size constraint
def group_by_count(items, max_delta, max_size, max_count, priority, delta_match_func, item_weight_func):
    # (ref_back, break_here, group_size)
    groups = [[]]

    remaining_groups = max_count
    resolved = 0

    for i in range(len(items)):
        value = items[i]

        if len(groups[-1]) == 0:
            groups[-1].append(value)
        
        elif not delta_match_func(item_weight_func(value), item_weight_func(groups[-1][0]), max_delta):
            resolved += len(groups[-1])
            groups.append([value])
            remaining_groups -= 1
        
        else:
            items_remaining = (len(items) - resolved)

            # oopsie, this should not happen
            # it might happen, because the max_delta criterion forces too many groups
            if remaining_groups == 0:
                remaining_groups = 1

            # check whether forward-looking we should now do a break
            if (resolved + math.ceil(items_remaining / remaining_groups)) == i:
                resolved += len(groups[-1])
                groups.append([value])
                remaining_groups -= 1
            
            else:
                groups[-1].append(value)

    return groups