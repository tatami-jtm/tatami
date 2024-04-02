from .models import db, Role, EventClass, EventRole

def _get_or_create(cls, **options):
    gotten = cls.query.filter_by(**options).one_or_none()

    if gotten is None:
        gotten = cls(**options)
        db.session.add(gotten)
        db.session.commit()
    
    return gotten

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