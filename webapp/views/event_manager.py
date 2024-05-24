from flask import Blueprint, render_template, abort, flash, session, g, \
    request, redirect, url_for, send_file
from flask_security import login_required, current_user
from werkzeug.utils import secure_filename

from ..models import db, Event, EventClass, DeviceRegistration, \
    DevicePosition, EventRole, Association, Registration, ListSystemRule, \
    ListSystem, Role, User

from ..helpers import _get_or_create

from datetime import datetime
import time, uuid, os, csv, io

eventmgr_view = Blueprint('event_manager', __name__)


def check_and_apply_event(func):
    def inner_func(event, *args, **kwargs):
        event = Event.from_slug(event)

        g.event = event

        return func(*args, **kwargs)

    inner_func.__name__ = func.__name__
    return inner_func


def check_is_event_supervisor(func):
    def inner_func(*args, **kwargs):
        if (not g.event.is_supervisor(current_user) and
                not current_user.has_privilege('create_tournaments')):
            abort(404)

        return func(*args, **kwargs)

    inner_func.__name__ = func.__name__
    return inner_func

@eventmgr_view.context_processor
def inject_device_options():
    device_positions = DevicePosition.query.filter_by(event=g.event).order_by('is_mat', 'position').all()
    device_roles = EventRole.query.all()
    return {
        "device_positions": device_positions,
        "device_roles": device_roles
    }


@eventmgr_view.route('/')
@login_required
@check_and_apply_event
@check_is_event_supervisor
def index():
    stats = {
        "mats":
            DevicePosition.query.filter_by(event=g.event, is_mat=True).count(),
        "classes":
            EventClass.query.filter_by(event=g.event).count(),
        "started_classes":
            EventClass.query.filter_by(event=g.event, begin_weigh_in=True).count(),
        "registrations":
            (total_registrations := g.event.total_registrations_count()),
        "confirmed_registrations":
            g.event.confirmed_registrations_count(),
        "registered_ratio":
            g.event.registered_registrations_count(),
        "weighed_in_ratio":
            g.event.weighed_registrations_count(),
        "placed_ratio":
            int(g.event.placed_ratio() * 1000) / 10,
        "open_matches":
            g.event.matches.filter_by(completed=False).count(),
        "scheduled_matches":
            g.event.matches.filter_by(scheduled=True, completed=False).count(),
        "completed_matches":
            g.event.matches.filter_by(completed=True).count(),
        "estimated_current_end":
            g.event.estimated_current_end()
    }

    invalid_registration_state_query = g.event.registrations.filter_by(registered=False, weighed_in=True).order_by('last_name', 'first_name', 'club')

    any_notice = False
    any_notice = any_notice or invalid_registration_state_query.count()

    return render_template("event-manager/index.html", stat=stats, invalid_registration_state_query=invalid_registration_state_query, any_notice=any_notice)


@eventmgr_view.route('/config')
@login_required
@check_and_apply_event
@check_is_event_supervisor
def config():
    system_rules = ListSystemRule.query.filter_by(event=g.event)
    
    ranges = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 8), (9, 16), (17, 32)]

    roles = Role.query.order_by(Role.is_admin.desc(), Role.name).all()
    users = User.query.all()

    return render_template("event-manager/config.html", ranges=ranges,
                           ListSystem=ListSystem, system_rules=system_rules,
                           roles=roles, users=users)


@eventmgr_view.route('/config', methods=['POST'])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def save_config():
    if request.form['form'] == 'general':
        role = Role.query.get_or_404(request.form['supervising_role'])
        user = User.query.get_or_404(request.form['supervising_user'])
        first_day = request.form['event_day_first'] + "T06:00"
        last_day = request.form['event_day_last'] + "T23:00"

        g.event.title = request.form['title']
        g.event.first_day = datetime.fromisoformat(first_day)
        g.event.last_day = datetime.fromisoformat(last_day)
        g.event.supervising_role = role
        g.event.supervising_user = user

        db.session.commit()

        flash("Einstellungen erfolgreich gespeichert", 'success')
        g.event.log(current_user.qualified_name(), 'DEBUG', 'Veranstaltungsdaten wurden geändert.')

    elif request.form['form'] == 'misc':
        g.event.save_setting('count_weighin_as_registration', 'count_weighin_as_registration' in request.form)
        g.event.save_setting('write_activity_log', 'write_activity_log' in request.form)
        g.event.save_setting('use_association_instead_of_club', 'use_association_instead_of_club' in request.form)

        flash("Einstellungen erfolgreich gespeichert", 'success')
        g.event.log(current_user.qualified_name(), 'DEBUG', 'Allgemeine Einstellungen wurden aktualisiert.')

    elif request.form['form'] == 'scheduling':
        g.event.save_setting('scheduling.use', 'use-scheduling' in request.form)

        if request.form['scheduling-max-group']:
            g.event.save_setting('scheduling.max_concurrent_groups', int(request.form['scheduling-max-group']))
        else:
            g.event.reset_setting('scheduling.max_concurrent_groups')

        if request.form['scheduling-max-participant']:
            g.event.save_setting('scheduling.max_concurrent_participants', int(request.form['scheduling-max-participant']))
        else:
            g.event.reset_setting('scheduling.max_concurrent_participants')

        if request.form['scheduling-plan-ahead']:
            g.event.save_setting('scheduling.plan_ahead', int(request.form['scheduling-plan-ahead']))
        else:
            g.event.reset_setting('scheduling.plan_ahead')

        flash("Einstellungen erfolgreich gespeichert", 'success')
        g.event.log(current_user.qualified_name(), 'DEBUG', 'Einstellungen bzgl. Listenführung wurden aktualisiert.')

    elif request.form['form'] == 'list_system_rules':
        ranges = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 8), (9, 16), (17, 32)]

        for rng in ranges:
            rng_rule = _get_or_create(ListSystemRule, event=g.event,
                                      minimum=rng[0], maximum=rng[1])
            
            form_key = f"list_system-{ rng[0] }-{ rng[1] }"
            system = ListSystem.all_enabled().filter_by(id=request.values[form_key]).one_or_none()
            rng_rule.system = system

        db.session.commit()

        flash("Einstellungen erfolgreich gespeichert", 'success')
        g.event.log(current_user.qualified_name(), 'DEBUG', 'Einstellungen bzgl. Zuweisung der Listensysteme wurden aktualisiert.')
    
    else:
        flash("Ungültige Einstellungsgruppe ausgewählt", 'danger')
    
    return redirect(url_for('event_manager.config', event=g.event.slug))


@eventmgr_view.route('/classes')
@login_required
@check_and_apply_event
@check_is_event_supervisor
def classes():
    return render_template("event-manager/classes/index.html")


@eventmgr_view.route('/classes/<id>/edit')
@login_required
@check_and_apply_event
@check_is_event_supervisor
def edit_class(id):
    event_class = EventClass.query.filter_by(id=id).one_or_404()
    templates = EventClass.query.filter_by(is_template=True).order_by(EventClass.template_name).all()
    return render_template("event-manager/classes/edit.html", event_class=event_class, templates=templates, new=False)



@eventmgr_view.route('/classes/<id>/edit', methods=["POST"])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def update_class(id):
    event_class = EventClass.query.filter_by(id=id).one_or_404()

    event_class.title = request.form['name']
    event_class.short_title = request.form['short_name']
    event_class.use_proximity_weight_mode = request.form['weight_mode'] == 'proximity'
    event_class.weight_generator = request.form['weight_generator']

    event_class.weight_generator = event_class.weight_generator.replace("\r\n", "\n")
    event_class.weight_generator = event_class.weight_generator.replace("\n\r", "\n")
    event_class.weight_generator = event_class.weight_generator.replace("\r", "\n")

    event_class.default_maximal_proximity = None
    if request.form['default_maximal_proximity']:
        event_class.default_maximal_proximity = int(request.form['default_maximal_proximity'])

    event_class.default_maximal_size = None
    if request.form['default_maximal_size']:
        event_class.default_maximal_size = int(request.form['default_maximal_size'])

    event_class.fighting_time = int(request.form['fighting_time'])
    event_class.golden_score_time = int(request.form['golden_score_time'])
    event_class.between_fights_time = int(request.form['between_fights_time'])

    if current_user.has_privilege('alter_presets'):
        event_class.is_template = 'is_template' in request.form
        event_class.template_name = request.form['template_name']

    db.session.commit()

    return redirect(url_for('event_manager.edit_class', event=g.event.slug, id=event_class.id))


@eventmgr_view.route('/classes/create', methods=["GET", "POST"])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def create_class():
    event_class = EventClass(event=g.event)

    if request.method == "POST":
        event_class.title = request.form['name']
        event_class.short_title = request.form['short_name']
        event_class.use_proximity_weight_mode = request.form['weight_mode'] == 'proximity'
        event_class.weight_generator = request.form['weight_generator']

        event_class.weight_generator = event_class.weight_generator.replace("\r\n", "\n")
        event_class.weight_generator = event_class.weight_generator.replace("\n\r", "\n")
        event_class.weight_generator = event_class.weight_generator.replace("\r", "\n")

        event_class.default_maximal_proximity = None
        if request.form['default_maximal_proximity']:
            event_class.default_maximal_proximity = int(request.form['default_maximal_proximity'])

        event_class.default_maximal_size = None
        if request.form['default_maximal_size']:
            event_class.default_maximal_size = int(request.form['default_maximal_size'])

        event_class.fighting_time = int(request.form['fighting_time'])
        event_class.golden_score_time = int(request.form['golden_score_time'])
        event_class.between_fights_time = int(request.form['between_fights_time'])

        event_class.begin_weigh_in = False
        event_class.begin_placement = False
        event_class.begin_fighting = False
        event_class.ended_fighting = False

        if current_user.has_privilege('alter_presets'):
            event_class.is_template = 'is_template' in request.form
            event_class.template_name = request.form['template_name']
        else:
            event_class.is_template = False

        db.session.add(event_class)
        db.session.commit()

        return redirect(url_for('event_manager.edit_class', event=g.event.slug, id=event_class.id))
    
    templates = EventClass.query.filter_by(is_template=True).order_by(EventClass.template_name).all()

    return render_template("event-manager/classes/new.html", event_class=event_class, templates=templates, new=True)


@eventmgr_view.route('/classes/<id>/progress/next', methods=['GET', 'POST'])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def class_step_forward(id):
    event_class = EventClass.query.filter_by(id=id).one_or_404()

    if not event_class.begin_weigh_in:
        event_class.begin_weigh_in = True
        event_class.begin_weigh_in_at = datetime.now()
    elif not event_class.begin_placement:
        event_class.begin_placement = True
        event_class.begin_placement_at = datetime.now()
    elif not event_class.begin_fighting:
        event_class.begin_fighting = True
        event_class.begin_fighting_at = datetime.now()
    elif not event_class.ended_fighting:
        event_class.ended_fighting = True
        event_class.ended_fighting_at = datetime.now()

    db.session.commit()

    g.event.log(current_user.qualified_name(), 'DEBUG', f'Kampfklasse {event_class.title} wurde in den nächsten Zustand gesetzt.')

    if request.values.get('to', '') == 'index':
        flash(f"Kampfklasse {event_class.title} wurde erfolgreich in den nächsten Zustand gesetzt.", 'success')
        return redirect(url_for('event_manager.classes', event=g.event.slug))
    
    return redirect(url_for('event_manager.edit_class', event=g.event.slug, id=event_class.id))


@eventmgr_view.route('/classes/<id>/progress/back', methods=['GET', 'POST'])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def class_step_back(id):
    event_class = EventClass.query.filter_by(id=id).one_or_404()

    if event_class.ended_fighting:
        event_class.ended_fighting = False
        event_class.ended_fighting_at = None
    elif event_class.begin_fighting:
        event_class.begin_fighting = False
        event_class.begin_fighting_at = None
    elif event_class.begin_placement:
        event_class.begin_placement = False
        event_class.begin_placement_at = None
    elif event_class.begin_weigh_in:
        event_class.begin_weigh_in = False
        event_class.begin_weigh_in_at = None

    db.session.commit()
    g.event.log(current_user.qualified_name(), 'DEBUG', f'Kampfklasse {event_class.title} wurde in den früheren Zustand zurückgesetzt.')

    return redirect(url_for('event_manager.edit_class', event=g.event.slug, id=event_class.id))


@eventmgr_view.route('/classes/<id>/merge_into', methods=['GET', 'POST'])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def merge_into_class(id):
    event_class = EventClass.query.filter_by(id=id).one_or_404()

    if request.method == 'POST':
        source_class = EventClass.query.filter_by(id=request.form['source']).one_or_404()

        if source_class.id == event_class.id:
            abort(400)

        modified_registrations = []
        g.event.log(current_user.qualified_name(), 'DEBUG',
                    f'Merge {source_class.title} -> {event_class.title} beginnt.')

        for reg in source_class.registrations:
            reg.event_class = event_class
            modified_registrations.append(reg.short_name())

        db.session.commit()
        g.event.log(current_user.qualified_name(), 'DEBUG',
                    f'Merge {source_class.title} -> {event_class.title}. Registrierungen übertragen: ' + ", ".join(modified_registrations))

        modified_groups = []
        for group in source_class.groups:
            group.title = event_class.short_title + " " + group.cut_title()
            group.event_class = event_class
            modified_groups.append(group.title)
        
        db.session.commit()
        g.event.log(current_user.qualified_name(), 'DEBUG',
                    f'Merge {source_class.title} -> {event_class.title}. Gruppen übertragen: ' + ", ".join(modified_groups))
        
        modified_matches = []
        for match in source_class.matches:
            match.event_class = event_class
            modified_matches.append(f"{match.group.title} - {match.white.full_name}/{match.blue.full_name}")
        
        db.session.commit()
        g.event.log(current_user.qualified_name(), 'DEBUG',
                    f'Merge {source_class.title} -> {event_class.title}. Kämpfe übertragen: ' + ", ".join(modified_matches))
        
        db.session.delete(source_class)
        db.session.commit()

        g.event.log(current_user.qualified_name(), 'DEBUG',
                    f'Merge {source_class.title} -> {event_class.title} abgeschlossen, Kampfklasse gelöscht.')
        
        flash(f"Kampfklasse {source_class.title} erfolgreich mit {event_class.title} zusammengeführt. {len(modified_registrations)} TN, {len(modified_groups)} Gruppen, {len(modified_matches)} Kämpfe wurden übertragen.", 'success')
        
        return redirect(url_for('event_manager.classes', event=g.event.slug))

    else:
        classes = g.event.classes.filter(EventClass.id != id).all()
        return render_template("event-manager/classes/merge.html", event_class=event_class, classes=classes)


@eventmgr_view.route('/registrations')
@login_required
@check_and_apply_event
@check_is_event_supervisor
def registrations():
    filtered_class = None
    status_filter = request.values.get('status_filter', None)

    if request.values.get('class_filter', None):
        filtered_class = EventClass.query.filter_by(id=request.values['class_filter']).one_or_404()

    return render_template("event-manager/registrations/index.html", filtered_class=filtered_class, status_filter=status_filter)


@eventmgr_view.route('/registrations/print')
@login_required
@check_and_apply_event
@check_is_event_supervisor
def print_registrations():
    filtered_class = None

    if request.values.get('id', None):
        filtered_class = EventClass.query.filter_by(id=request.values['id']).one_or_404()

    return render_template("event-manager/registrations/print_all.html", filtered_class=filtered_class)


@eventmgr_view.route('/registrations/class_<id>_registrations.csv')
@login_required
@check_and_apply_event
@check_is_event_supervisor
def class_registrations_as_csv(id):
    evcl = g.event.classes.filter_by(id=id).one_or_404()

    data = [()]
    field_names = (
        'Nachname',
        'Vorname',
        'Verein',
        'Verband',
        'Gewicht (gemeldet)',
        'Gewicht (Waage)',
        'Bestätigt?',
        'Angemeldet?',
        'Eingewogen?'
    )

    for registration in evcl.registrations.order_by('last_name', 'first_name', 'club'):
        data.append((
            registration.last_name,
            registration.first_name,
            registration.club,
            registration.association.short_name if registration.association else None,
            registration.suggested_group,
            registration.verified_weight / 1000,
            'x' if registration.confirmed else '',
            'x' if registration.registered else '',
            'x' if registration.weighed_in else ''
        ))
    
    
    csv_io = io.StringIO()
    csvwriter = csv.writer(csv_io, delimiter=',', quotechar='\"')
    csvwriter.writerow(field_names)
    csvwriter.writerows(data)

    # Flask is stupid and only accepts BytesIO,
    # however csv is stupid too and only works with StringIO
    # so we need to convert the csv_io to mem_io
    mem_io = io.BytesIO()
    mem_io.write(csv_io.getvalue().encode())
    mem_io.seek(0)

    return send_file(mem_io, mimetype='text/csv')


@eventmgr_view.route('/registrations/<id>/edit')
@login_required
@check_and_apply_event
@check_is_event_supervisor
def edit_registration(id):
    registration = Registration.query.filter_by(id=id).one_or_404()
    return render_template("event-manager/registrations/edit.html", registration=registration)


@eventmgr_view.route('/registrations/<id>/edit', methods=["POST"])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def update_registration(id):
    registration = Registration.query.filter_by(id=id).one_or_404()
    registration.first_name = request.form['first_name']
    registration.last_name = request.form['last_name']
    registration.club = request.form['club']
    registration.contact_details = request.form['contact_details']
    registration.suggested_group = request.form['suggested_group']

    registration.confirmed = "confirmed" in request.form
    registration.registered = "registered" in request.form
    registration.weighed_in = "weighed_in" in request.form
    registration.placed = "placed" in request.form

    if len(request.form['association']):
        registration.association_id = int(request.form['association'])
    else:
        registration.association_id = None

    if len(request.form['event_class']):
        registration.event_class_id = int(request.form['event_class'])
    else:
        registration.event_class_id = None

    if request.form['verified_weight']:
        registration.verified_weight = int(float(request.form['verified_weight']) * 1000)
    else:
        registration.verified_weight = None

    db.session.commit()
    g.event.log(current_user.qualified_name(), 'DEBUG', f'TN-Anmeldung {registration.short_name()} wurde bearbeitet.')

    return redirect(url_for('event_manager.edit_registration', event=g.event.slug, id=registration.id))


@eventmgr_view.route('/registrations/create', methods=["GET", "POST"])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def create_registration():
    registration = Registration(event=g.event)

    if request.method == "POST":
        registration.first_name = request.form['first_name']
        registration.last_name = request.form['last_name']
        registration.club = request.form['club']
        registration.contact_details = request.form['contact_details']
        registration.suggested_group = request.form['suggested_group']

        registration.confirmed = "confirmed" in request.form
        registration.registered = "registered" in request.form
        registration.weighed_in = "weighed_in" in request.form
        registration.placed = False

        if len(request.form['association']):
            registration.association_id = int(request.form['association'])
        else:
            registration.association_id = None

        if len(request.form['event_class']):
            registration.event_class_id = int(request.form['event_class'])
        else:
            registration.event_class_id = None

        if request.form['verified_weight']:
            registration.verified_weight = int(float(request.form['verified_weight']) * 1000)
        else:
            registration.verified_weight = None

        db.session.add(registration)
        db.session.commit()
        g.event.log(current_user.qualified_name(), 'DEBUG', f'Neue TN-Anmeldung für {registration.short_name()} angelegt.')

        return redirect(url_for('event_manager.edit_registration', event=g.event.slug, id=registration.id))

    return render_template("event-manager/registrations/new.html", registration=registration)


@eventmgr_view.route('/registrations/import', methods=['GET', 'POST'])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def import_registrations_index():
    if request.method == 'POST':
        if 'csvfile' in request.files:
            csvfile = request.files['csvfile']

            if csvfile and csvfile.filename != '':
                fn = str(uuid.uuid4())
                csvfile.save(f"temp/{fn}.csv")

                return redirect(url_for('event_manager.import_registrations_inspector', event=g.event.slug, fn=fn))

            else:
                flash("Keine Datei hochgeladen.", 'danger')

        else:
            flash("Keine Datei hochgeladen.", 'danger')

    return render_template("event-manager/registrations/import/index.html")


@eventmgr_view.route('/registrations/import/<fn>')
@login_required
@check_and_apply_event
@check_is_event_supervisor
def import_registrations_inspector(fn):
    data, rowcount, colcount = _load_csv(fn)
    return render_template("event-manager/registrations/import/inspect.html", data=data, rowcount=rowcount, colcount=colcount)


@eventmgr_view.route('/registrations/import/<fn>', methods=['POST'])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def import_registrations_do(fn):
    data, _, _ = _load_csv(fn)

    relevant_data = data[int(request.form['start-row']):]

    if len(relevant_data) == 0:
        flash("Es muss wenigstens eine Zeile ausgewählt werden.", 'error')
        return redirect(url_for('event_manager.import_registrations_inspector', event=g.event.slug, fn=fn))
    
    first_name_offset = int(request.form['first_name'])
    last_name_offset = int(request.form['last_name'])
    contact_details_offset = int(request.form['contact_details'])
    club_offset = int(request.form['club'])
    association_offset = int(request.form['association'])
    event_class_offset = int(request.form['event_class'])
    suggested_group_offset = int(request.form['suggested_group'])

    successful = 0

    for row in relevant_data:
        association = row[association_offset]
        event_class = row[event_class_offset]

        registration = Registration(event=g.event)

        registration.first_name = row[first_name_offset]
        registration.last_name = row[last_name_offset]
        registration.club = row[club_offset]
        registration.contact_details = row[contact_details_offset]
        registration.suggested_group = row[suggested_group_offset]

        registration.confirmed = request.form['confirm_all'] == 'yes'
        registration.registered = False
        registration.weighed_in = False
        registration.placed = False

        if len(association):
            assoc = g.event.associations.filter(
                Association.short_name.ilike(f"%{association}%") |
                Association.name.ilike(f"%{association}%")
            ).one_or_none()

            registration.association_id = assoc.id if assoc is not None else None
        else:
            registration.association_id = None

        if len(event_class):
            evcl = g.event.classes.filter(
                EventClass.short_title.ilike(f"%{event_class}%") |
                EventClass.title.ilike(f"%{event_class}%") |
                EventClass.template_name.ilike(f"%{event_class}%")
            ).one_or_none()

            registration.event_class_id = evcl.id if evcl is not None else None
        else:
            registration.event_class_id = None

        db.session.add(registration)
        db.session.commit()
        g.event.log(current_user.qualified_name(), 'DEBUG', f'Neue TN-Anmeldung für {registration.short_name()} angelegt.')

        successful += 1
    
    flash(f"Erfolgreich importiert: {successful} TN", 'success')
    g.event.log(current_user.qualified_name(), 'DEBUG', f'Es wurden {successful} TN-Anmeldungen importiert.')

    os.remove(f"temp/{fn}.csv")
    return redirect(url_for('event_manager.registrations', event=g.event.slug))


@eventmgr_view.route('/associations')
@login_required
@check_and_apply_event
@check_is_event_supervisor
def associations():
    return render_template("event-manager/associations/index.html")


@eventmgr_view.route('/associations/<id>/edit')
@login_required
@check_and_apply_event
@check_is_event_supervisor
def edit_association(id):
    association = Association.query.filter_by(id=id).one_or_404()
    return render_template("event-manager/associations/edit.html", association=association)


@eventmgr_view.route('/associations/<id>/edit', methods=["POST"])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def update_association(id):
    association = Association.query.filter_by(id=id).one_or_404()
    association.short_name = request.form['short_name']
    association.name = request.form['name']

    db.session.commit()
    g.event.log(current_user.qualified_name(), 'DEBUG', f'Verband {association.short_name} wurde bearbeitet.')

    return redirect(url_for('event_manager.edit_association', event=g.event.slug, id=association.id))


@eventmgr_view.route('/associations/create', methods=["GET", "POST"])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def create_association():
    association = Association(event=g.event)

    if request.method == "POST":
        association.short_name = request.form['short_name']
        association.name = request.form['name']

        db.session.add(association)
        db.session.commit()
        g.event.log(current_user.qualified_name(), 'DEBUG', f'Neuer Verband {association.short_name} angelegt.')

        return redirect(url_for('event_manager.edit_association', event=g.event.slug, id=association.id))

    return render_template("event-manager/associations/new.html", association=association)


@eventmgr_view.route('/devices')
@login_required
@check_and_apply_event
@check_is_event_supervisor
def devices():
    admin_pos = DevicePosition.query.filter_by(
        event=g.event, is_mat=False).order_by('position').all()
    mat_pos = DevicePosition.query.filter_by(
        event=g.event, is_mat=True).order_by('position').all()
    requests = DeviceRegistration.query.filter_by(
        event=g.event, confirmed=False).all()
    return render_template(
        "event-manager/devices.html",
        mat_pos=mat_pos,
        admin_pos=admin_pos,
        requests=requests)


@eventmgr_view.route('/devices/<id>/update', methods=["POST"])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def device_update(id):
    device = DeviceRegistration.query.filter_by(
        event=g.event, id=id).one_or_404()
    pos = DevicePosition.query.filter_by(
        event=g.event, id=request.form['position']).one_or_404()
    name = request.form['name']
    role = EventRole.query.filter_by(id=request.form['role']).one_or_404()

    device.position_id = pos.id
    device.title = name
    device.event_role_id = role.id

    newly_confirmed = False
    if not device.confirmed:
        device.confirmed = True
        device.confirmed_at = datetime.now()
        device.registered_by_id = current_user.id
        newly_confirmed = True

    db.session.commit()
    
    if newly_confirmed:
        g.event.log(current_user.qualified_name(), 'DEBUG', f'Gerät {device.title} mit Rolle {device.event_role.name} an {device.position.title} freigegeben.')
    else:
        g.event.log(current_user.qualified_name(), 'DEBUG', f'Gerät {device.title} bearbeitet.')

    return redirect(url_for('event_manager.devices', event=g.event.slug))


@eventmgr_view.route('/devices/<id>/delete', methods=["GET", "POST"])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def device_delete(id):
    device = DeviceRegistration.query.filter_by(
        event=g.event, id=id).one_or_404()
    db.session.delete(device)
    db.session.commit()

    g.event.log(current_user.qualified_name(), 'DEBUG', f'Gerät {device.title} gelöscht.')

    return redirect(url_for('event_manager.devices', event=g.event.slug))


@eventmgr_view.route('/devices/<id>/inspect')
@login_required
@check_and_apply_event
@check_is_event_supervisor
def device_inspect(id):
    device = DeviceRegistration.query.filter_by(
        event=g.event, id=id).one_or_404()

    session['device_token'] = device.token

    g.event.log(current_user.qualified_name(), 'DEBUG', f'Sitzung von Gerät {device.title} beigetreten.')

    flash(f"Willkommen! Beitritt zur Sitzung von {device.title} war erfolgreich.", 'success')

    return redirect(url_for('devices.index', event=g.event.slug))


@eventmgr_view.route('/devices/allow-registration', methods=["POST"])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def devices_allow_register():
    g.event.allow_device_registration = 'allow' in request.form
    db.session.commit()

    if g.event.allow_device_registration:
        g.event.log(current_user.qualified_name(), 'DEBUG', f'Registrierung von Geräten nun: ERLAUBT')
    else:
        g.event.log(current_user.qualified_name(), 'DEBUG', f'Registrierung von Geräten nun: VERBOTEN')

    return redirect(url_for('event_manager.devices', event=g.event.slug))


@eventmgr_view.route('/devices/position/<id>/update', methods=["POST"])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def device_position_update(id):
    device_position = DevicePosition.query.filter_by(
        event=g.event, id=id).one_or_404()
    name = request.form['name']
    is_mat = request.form['is_mat'] == '1'

    device_position.title = name
    device_position.is_mat = is_mat

    db.session.commit()
    g.event.log(current_user.qualified_name(), 'DEBUG', f'Hallenposition {device_position.title} bearbeitet.')

    return redirect(url_for('event_manager.devices', event=g.event.slug))


@eventmgr_view.route('/devices/position/<id>/delete', methods=["GET", "POST"])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def device_position_delete(id):
    device_position = DevicePosition.query.filter_by(
        event=g.event, id=id).one_or_404()

    if device_position.devices.count():
        flash(f"Position {device_position.title} kann nicht gelöscht werden, "
              "da ihr noch Geräte zugewiesen sind.", 'danger')
        return redirect(url_for('event_manager.devices', event=g.event.slug))

    db.session.delete(device_position)
    db.session.commit()
    g.event.log(current_user.qualified_name(), 'DEBUG', f'Hallenposition {device_position.title} gelöscht.')

    return redirect(url_for('event_manager.devices', event=g.event.slug))


@eventmgr_view.route('/devices/position/create', methods=["GET", "POST"])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def device_position_create():
    device_position = DevicePosition(event=g.event)
    device_position.title = "Neue Position"
    device_position.is_mat = "mat" in request.values
    device_position.position = int(time.time())

    if device_position.is_mat:
        mat_count = DevicePosition.query.filter_by(
            event=g.event, is_mat=True).count()
        device_position.title = f"Matte {mat_count + 1}"

    db.session.add(device_position)
    db.session.commit()

    g.event.log(current_user.qualified_name(), 'DEBUG', f'Hallenposition {device_position.title} angelegt. Matte={int(device_position.is_mat)}')

    return redirect(url_for('event_manager.devices', event=g.event.slug))


@eventmgr_view.route('/quick-sign-in', methods=["POST"])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def quick_sign_in():
    device = None
    if 'device_token' in session:
        device = DeviceRegistration.query.filter_by(
        event=g.event, token=session['device_token']).one_or_none()
    
    if device is None:
        device = DeviceRegistration(event=g.event)
        db.session.add(device)

    device.token = str(uuid.uuid4())
    device.title = f"Admin-Zugang - {current_user.display_name}"

    device.confirmed = True
    device.confirmed_at = datetime.now()

    device.registered_at = datetime.now()
    device.registered_by_id = current_user.id

    pos = DevicePosition.query.filter_by(
        event=g.event, id=request.form['position']).one_or_404()
    role = EventRole.query.filter_by(id=request.form['role']).one_or_404()

    device.position_id = pos.id
    device.event_role_id = role.id

    db.session.commit()

    session['device_token'] = device.token

    flash('Willkommen! Die Schnelleinwahl war erfolgreich.', 'success')

    g.event.log(current_user.qualified_name(), 'DEBUG', f'Schnelleinwahl vorgenommen mit Rolle {device.event_role.name} an {device.position.title}')

    return redirect(url_for('devices.index', event=g.event.slug))


@eventmgr_view.route('/log')
@login_required
@check_and_apply_event
@check_is_event_supervisor
def log():
    return render_template("event-manager/log.html")


def _load_csv(fn):
    # Make sure we only have safe filenames
    fn = secure_filename(fn)
    fn = f"temp/{fn}.csv"

    if not os.path.isfile(fn):
        abort(404)

    data = []

    with open(fn, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)

        for row in csvreader:
            data.append(row)

    rowcount = len(data)
    if rowcount == 0:
        abort(400)

    colcount = len(data[0])

    return data, rowcount, colcount