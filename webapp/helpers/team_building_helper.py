import random, math

def build_team_rotation(registrations, delta_match_func, item_weight_func, max_delta=None,
                        max_teams=None, max_rows=None):
    
    if max_teams is None:
        return _build_teams_with_fixed_rows(registrations, delta_match_func, item_weight_func, max_delta, max_rows)
    
    elif max_rows is None:
        return _build_teams_with_fixed_teams(registrations, delta_match_func, item_weight_func, max_delta, max_teams)
    
    else:
        return _build_teams_with_full_rotation(registrations, delta_match_func, item_weight_func, max_delta, max_teams, max_rows)


def _build_teams_with_fixed_rows(registrations, delta_match_func, item_weight_func, max_delta, max_rows):
    team_count = max(2, math.ceil(len(registrations) / max_rows))
    row_count = max_rows

    matrix = _make_matrix(team_count, row_count)
    row = team = 0

    orig_team_count = team_count

    has_valid_assignment = False

    while not has_valid_assignment:
        team_count = orig_team_count
        for _ in range(3):
            matrix = _make_matrix(team_count, row_count)

            team = row = 0

            for reg in registrations:
                first_in_row = matrix[row][0]

                if len(first_in_row) > 0:
                    if not delta_match_func(
                            item_weight_func(reg),
                            item_weight_func(first_in_row[0]),
                            max_delta
                        ):
                        row += 1

                        if row == len(matrix):
                            break

                        matrix[row][0].append(reg)
                        team = 1

                        continue

                matrix[row][team].append(reg)
                team += 1

                if team >= team_count:
                    team = 0
                    row += 1

                    if row == len(matrix):
                        break
            else:
                if row <= row_count:
                    matrix = matrix[:(row + 1)]

                has_valid_assignment = True
                break

            if has_valid_assignment:
                break
            else:
                team_count += 1

        if has_valid_assignment:
            break
        
        row_count += 1
    
    return matrix, _transpose_matrix(team_count, matrix)


def _build_teams_with_fixed_teams(registrations, delta_match_func, item_weight_func, max_delta, max_teams):
    team_count = max_teams
    row_count = math.ceil(len(registrations) / max_teams)


def _build_teams_with_full_rotation(registrations, delta_match_func, item_weight_func, max_delta, max_teams, max_rows):
    team_count = max_teams
    row_count = max_rows

    matrix = _make_matrix(team_count, row_count)


def _make_matrix(team_count, row_count):
    return [[[] for j in range(team_count)] for i in range(row_count)]

def _expand_matrix(matrix, team_count):
    return matrix + [[[] for j in range(team_count)]]

def _transpose_matrix(team_count, matrix):
    rm = [[] for j in range(team_count)]

    for row in matrix:
        for i in range(team_count):
            rm[i].append(row[i])
    
    return rm