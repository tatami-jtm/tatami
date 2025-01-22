from .models import db, Role, EventClass, EventRole, ListSystem, ScoreboardRuleset
from .helpers import _get_or_create

def setup_roles():
    _get_or_create(Role, name="platform_admin", is_admin=True)

def setup_class_templates():
    _get_or_create(EventClass, template_name="U11 (weiblich)", is_template=True, event=None,
                   title="U11 (weiblich)", short_title="U11w",
                   fighting_time=120, golden_score_time=0, between_fights_time=360,
                   use_proximity_weight_mode=True, default_maximal_proximity=3000, default_maximal_size=4)
    
    _get_or_create(EventClass, template_name="U11 (männlich)", is_template=True, event=None,
                   title="U11 (männlich)", short_title="U11m",
                   fighting_time=120, golden_score_time=0, between_fights_time=360,
                   use_proximity_weight_mode=True, default_maximal_proximity=3000, default_maximal_size=4)
    
    _get_or_create(EventClass, template_name="U13 (weiblich)", is_template=True, event=None,
                   title="U13 (weiblich)", short_title="U13w",
                   fighting_time=180, golden_score_time=0, between_fights_time=600,
                   use_proximity_weight_mode=False, weight_generator="-27\n-30\n-33\n-36\n-40\n-44\n-48\n-52\n-57\n+57")
    
    _get_or_create(EventClass, template_name="U13 (männlich)", is_template=True, event=None,
                   title="U13 (männlich)", short_title="U13m",
                   fighting_time=180, golden_score_time=0, between_fights_time=600,
                   use_proximity_weight_mode=False, weight_generator="-28\n-31\n-34\n-37\n-40\n-43\n-46\n-50\n-55\n+55")
    
    _get_or_create(EventClass, template_name="U15 (weiblich)", is_template=True, event=None,
                   title="U15 (weiblich)", short_title="U15w",
                   fighting_time=180, golden_score_time=180, between_fights_time=600,
                   use_proximity_weight_mode=False, weight_generator="-33\n-36\n-40\n-44\n-48\n-52\n-57\n-63\n+63")
    
    _get_or_create(EventClass, template_name="U15 (männlich)", is_template=True, event=None,
                   title="U15 (männlich)", short_title="U15m",
                   fighting_time=180, golden_score_time=180, between_fights_time=600,
                   use_proximity_weight_mode=False, weight_generator="-34\n-37\n-40\n-43\n-46\n-50\n-55\n-60\n-66\n+66")
    
    _get_or_create(EventClass, template_name="U18 (weiblich)", is_template=True, event=None,
                   title="U18 (weiblich)", short_title="U18w",
                   fighting_time=240, golden_score_time=-1, between_fights_time=600,
                   use_proximity_weight_mode=False, weight_generator="-40\n-44\n-48\n-52\n-57\n-63\n-70\n-78\n+78")
    
    _get_or_create(EventClass, template_name="U18 (männlich)", is_template=True, event=None,
                   title="U18 (männlich)", short_title="U18m",
                   fighting_time=240, golden_score_time=-1, between_fights_time=600,
                   use_proximity_weight_mode=False, weight_generator="-46\n-50\n-55\n-60\n-66\n-73\n-81\n-90\n+90")
    
    _get_or_create(EventClass, template_name="Frauen", is_template=True, event=None,
                   title="Frauen", short_title="F",
                   fighting_time=240, golden_score_time=-1, between_fights_time=600,
                   use_proximity_weight_mode=False, weight_generator="-48\n-52\n-57\n-63\n-70\n-78\n+78")
    
    _get_or_create(EventClass, template_name="Männer", is_template=True, event=None,
                   title="Männer", short_title="M",
                   fighting_time=240, golden_score_time=-1, between_fights_time=600,
                   use_proximity_weight_mode=False, weight_generator="-60\n-66\n-73\n-81\n90\n-100\n+100")

def setup_list_systems():
    _get_or_create(ListSystem, title="Einzelliste", list_file="single",
                   mandatory_minimum=1, mandatory_maximum=1, enabled=True,
                   estimated_fight_count=0, break_count=0, display_page_count=1)
    
    _get_or_create(ListSystem, title="2er-Pool", list_file="pool2",
                   mandatory_minimum=2, mandatory_maximum=2, enabled=True,
                   estimated_fight_count=1, break_count=0, display_page_count=1)
    
    _get_or_create(ListSystem, title="Best of Three", list_file="bestof3",
                   mandatory_minimum=2, mandatory_maximum=2, enabled=True,
                   estimated_fight_count=2, break_count=2, display_page_count=1)
    
    _get_or_create(ListSystem, title="3er-Pool", list_file="pool3",
                   mandatory_minimum=3, mandatory_maximum=3, enabled=True,
                   estimated_fight_count=3, break_count=2, display_page_count=1)
    
    _get_or_create(ListSystem, title="4er-Pool", list_file="pool4",
                   mandatory_minimum=4, mandatory_maximum=4, enabled=True,
                   estimated_fight_count=6, break_count=2, display_page_count=1)
    
    _get_or_create(ListSystem, title="5er-Pool", list_file="pool5",
                   mandatory_minimum=5, mandatory_maximum=5, enabled=True,
                   estimated_fight_count=10, break_count=4, display_page_count=1)
    
    _get_or_create(ListSystem, title="Doppel-Pool 8 TN", list_file="doublepool8",
                   mandatory_minimum=5, mandatory_maximum=8, enabled=True,
                   estimated_fight_count=15, break_count=3, display_page_count=1)
    
    _get_or_create(ListSystem, title="Doppel-KO 8 TN", list_file="ko8",
                   mandatory_minimum=5, mandatory_maximum=8, enabled=True,
                   estimated_fight_count=11, break_count=2, display_page_count=1)
    
    _get_or_create(ListSystem, title="Doppel-KO 16 TN", list_file="ko16",
                   mandatory_minimum=9, mandatory_maximum=16, enabled=True,
                   estimated_fight_count=27, break_count=4, display_page_count=1)
    
    _get_or_create(ListSystem, title="Doppel-KO 32 TN", list_file="ko32",
                   mandatory_minimum=17, mandatory_maximum=32, enabled=True,
                   estimated_fight_count=59, break_count=7, display_page_count=3)

def setup_event_roles():
    _get_or_create(EventRole, name="Anmeldung",
                   may_use_registration=True)
    _get_or_create(EventRole, name="Waage",
                   may_use_weigh_in=True)
    _get_or_create(EventRole, name="Anmeldung und Waage",
                   may_use_registration=True, may_use_weigh_in=True)
    _get_or_create(EventRole, name="Hauptliste",
                   may_use_registration=True, may_use_placement_tool=True, may_use_global_list=True,
                   may_use_results=True)
    _get_or_create(EventRole, name="Listentisch",
                   may_use_assigned_lists=True)
    _get_or_create(EventRole, name="Tischbesetzung",
                   may_use_scoreboard=True)
    _get_or_create(EventRole, name="Liste + Tischbesetzung",
                   may_use_assigned_lists=True, may_use_scoreboard=True)
    _get_or_create(EventRole, name="Listenanzeige",
                   may_use_beamer=True)
    _get_or_create(EventRole, name="Demonstration",
                   may_use_registration=True, may_use_weigh_in=True, may_use_placement_tool=True,
                   may_use_global_list=True, may_use_results=True, may_use_assigned_lists=True,
                   may_use_scoreboard=True, may_use_beamer=True)


def setup_scoreboard_rulesets():
    _get_or_create(
        ScoreboardRuleset,
        title="IJF (2025) - 1I/2W/Y/3S/H",
        enabled=True,
        is_default=True,
        rules="""
{
    "scores": {
        "ippon": {
            "name": "Ippon",
            "short_name": "I",
            "max_count": 1,
            "penalty": false,
            "points": 10,
            "ends_fight": true,
            "is_equal_if_accumulated": true
        },
        "wazaari": {
            "name": "Wazaari",
            "short_name": "W",
            "max_count": 2,
            "penalty": false,
            "points": 7,
            "accumulates": "ippon",
            "ends_fight": false,
            "is_equal_if_accumulated": false
        },
        "yuko": {
            "name": "Yuko",
            "short_name": "Y",
            "penalty": false,
            "points": 5,
            "ends_fight": false,
            "is_equal_if_accumulated": false
        },
        "shido": {
            "name": "Shido",
            "short_name": "S",
            "max_count": 3,
            "penalty": true,
            "accumulates": "hansokumake",
            "disqualifies": false,
            "ends_fight": false,
            "is_equal_if_accumulated": false
        },
        "hansokumake": {
            "name": "Hansoku-make",
            "short_name": "HM",
            "max_count": 1,
            "penalty": true,
            "disqualifies": true,
            "points": 10,
            "ends_fight": true,
            "is_equal_if_accumulated": false
        }
    },
    "osaekomi": [
        { "at": 5, "score": "yuko", "final": false },
        { "at": 10, "score": "wazaari", "final": false },
        { "at": 20, "score": "ippon", "final": true }
    ],
    "ranking": ["hansokumake", "ippon", "wazaari", "yuko"],
    "controls": ["ippon", "wazaari", "yuko", "osaekomi", "shido", "hansokumake"],
    "display": [
        { "style": "full_text", "for": "ippon", "text": "IPPON" },
        { "style": "counter", "for": "wazaari", "size": "lg" },
        { "style": "counter", "for": "yuko", "size": "md" },
        { "style": "penalty_card", "for_lower": "shido", "for_higher": "hansokumake" }
    ],
    "small_display": ["ippon", "wazaari", "yuko", "shido", "hansokumake"]
}
        """.strip())
    
    _get_or_create(
        ScoreboardRuleset,
        title="IJF (2018) - 1I/2W/3S/H",
        enabled=True,
        is_default=False,
        rules="""
{
    "scores": {
        "ippon": {
            "name": "Ippon",
            "short_name": "I",
            "max_count": 1,
            "penalty": false,
            "points": 10,
            "ends_fight": true,
            "is_equal_if_accumulated": true
        },
        "wazaari": {
            "name": "Wazaari",
            "short_name": "W",
            "max_count": 2,
            "penalty": false,
            "points": 7,
            "accumulates": "ippon",
            "ends_fight": false,
            "is_equal_if_accumulated": false
        },
        "shido": {
            "name": "Shido",
            "short_name": "S",
            "max_count": 3,
            "penalty": true,
            "accumulates": "hansokumake",
            "disqualifies": false,
            "ends_fight": false,
            "is_equal_if_accumulated": false
        },
        "hansokumake": {
            "name": "Hansoku-make",
            "short_name": "HM",
            "max_count": 1,
            "penalty": true,
            "disqualifies": true,
            "points": 10,
            "ends_fight": true,
            "is_equal_if_accumulated": false
        }
    },
    "osaekomi": [
        { "at": 10, "score": "wazaari", "final": false },
        { "at": 20, "score": "ippon", "final": true }
    ],
    "ranking": ["hansokumake", "ippon", "wazaari"],
    "controls": ["ippon", "wazaari", "osaekomi", "shido", "hansokumake"],
    "display": [
        { "style": "full_text", "for": "ippon", "text": "IPPON" },
        { "style": "counter", "for": "wazaari", "size": "lg" },
        { "style": "penalty_card", "for_lower": "shido", "for_higher": "hansokumake" }
    ],
    "small_display": ["ippon", "wazaari", "shido", "hansokumake"]
}
        """.strip())