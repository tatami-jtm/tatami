from .list_compiler import *
from .metalist import *
from .fighter import Fighter
from .match_result import MatchResult
from .list_new_renderer import ListRenderer
from .empty_list_mock import EmptyListMock

if __name__ == "__main__":
    # example_list = compile_list('pool2')()
    # example_list.alloc(Fighter('aaa', 'A-Fighter', 'A-Team'))
    # example_list.alloc(Fighter('bbb', 'B-Fighter', 'B-Team'))

    # first_match = example_list.get_schedule()[0]['match']
    # fmr = first_match.mk_result()
    # fmr.set_points_white(1)
    # fmr.set_score_white(10)
    # fmr.set_points_blue(0)
    # fmr.set_score_blue(0)
    # fmr.set_time(120)
    # example_list.enter_results(fmr)

    # example_list.score()
    list_cls = compile_list('ko32')
    example_list = list_cls()
    example_list.import_struct({
        'random_seed': 4,
        'fighters': [
            Fighter(f'p{i}', f'{i}-Fighter', f'{i}-Team') for i in range(1, 33)
        ],
        'matches': {
            f'm{i}': MatchResult.mk(1, 10, None, 0, 0, None, None, 120) for i in range(1, 60)
        },
        'playoff_matches': {
        }
    })

    print(example_list.get_schedule())
    example_list.make_image(title="Testmeisterschaft 2023", event_class='U18m', group='-50kg', page=2).show()

    # print("Schedule:", example_list.get_schedule())
    # print("Completed?", example_list.completed())
    # print(example_list.score())

    # print(example_list.get_fifth())

    # print("Schedule:", example_list.get_schedule())

    # print("FIRST:", example_list.get_first())
    # print("SECOND:", example_list.get_second())
    # print("THIRD:", *example_list.get_third())
    # print("FIFTH:", *example_list.get_fifth())

    # print(example_list.export_struct())

    # all_lists = get_all_lists()
    # chosen_list = all_lists[3]

    # print("Avail. lists:",
    #     ", ".join(all_lists))
    # print("Attempting to compile:",
    #     chosen_list)

    # print()

    # list_cls = compile_list(chosen_list)
    # metalist = list_cls.meta

    # print("Name:",
    #     metalist.get_name())
    # print("Requires:",
    #     metalist.require_min(), "--", metalist.require_max())
    # print("Allocation order:",
    #     ", ".join(map(str, metalist._allocation_order)))
    
    # example_list = list_cls()
    # example_list.alloc(Fighter('aaa', 'A-Fighter', 'A-Team'))
    # example_list.get_schedule(True)
    # example_list.alloc(Fighter('bbb', 'B-Fighter', 'B-Team'))
    # example_list.alloc(Fighter('ccc', 'C-Fighter', 'C-Team'))

    # print("Schedule:", example_list.get_schedule())

    # print("###1", example_list._match_results)

    # # print("Resolving first fight.")

    # first_match = example_list.get_schedule()[0]['match']
    # print("###2", first_match)
    # fmr = first_match.mk_result()
    # fmr.set_points_white(1)
    # fmr.set_score_white(10)
    # fmr.set_points_blue(0)
    # fmr.set_score_blue(0)
    # fmr.set_time(120)

    # print("###3", example_list._match_results)


    # #print(example_list._match_results['AvB'])

    # print("Schedule:", example_list.get_schedule())

    # print("completed?", example_list.completed())

    # second_match = example_list.get_schedule()[0]['match']
    # smr = second_match.mk_result()
    # smr.set_points_white(0)
    # smr.set_score_white(0)
    # smr.set_points_blue(1)
    # smr.set_score_blue(10)
    # smr.set_time(120)
    # example_list.enter_results(smr)

    # print("Schedule:", example_list.get_schedule())
    # print("completed?", example_list.completed())

    # print("Scoring: is-finished?", example_list.score())

    # print("Schedule:", example_list.get_schedule())
    # print("completed?", example_list.completed())

    # po_match = example_list.get_schedule()[0]['match']
    # pomr = po_match.mk_result()
    # pomr.set_points_white(0)
    # pomr.set_score_white(0)
    # pomr.set_points_blue(1)
    # pomr.set_score_blue(1)
    # pomr.set_time(120)
    # example_list.enter_results(pomr)

    # print("Schedule:", example_list.get_schedule())
    # print("completed?", example_list.completed())

    # print("Scoring: is-finished?", example_list.score())

    # print("FIRST:", example_list.get_first())
    # print("SECOND:", example_list.get_second())
    # print("THIRD:", *example_list.get_third())
    # print("FIFTH:", *example_list.get_fifth())

    # print(example_list._score_deductions)